"""
E-Labz Webhook Handler — Stripe + Lemon Squeezy Event Listener
Receives payment webhooks, logs revenue, and triggers notifications.

Run: python -m orchestrator.webhook_handler
Listens on port 8081 (separate from dashboard on 8080)
"""

import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

import os
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger, log_scheduler_event
except ImportError:
    import logging
    logger = logging.getLogger("webhook_handler")
    def log_scheduler_event(*args): pass

try:
    from orchestrator.revenue_agent import get_revenue_agent
except ImportError:
    def get_revenue_agent(): return None

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None

# ============================================================
# CONFIG
# ============================================================

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_NEWSLETTER_CHANNEL = os.getenv("SLACK_NEWSLETTER_CHANNEL", "")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8081"))


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhooks from Stripe and Lemon Squeezy."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.path == "/webhooks/stripe":
            self._handle_stripe(body)
        elif self.path == "/webhooks/lemonsqueezy":
            self._handle_lemonsqueezy(body)
        elif self.path == "/webhooks/test":
            self._handle_test(body)
        else:
            self.send_response(404)
            self.end_headers()
            return

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "service": "e-labz-webhooks",
                "timestamp": datetime.now().isoformat()
            }).encode())
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"E-Labz Webhook Handler")

    def log_message(self, format, *args):
        """Suppress default HTTP logs, use our logger."""
        logger.info(f"Webhook: {args[0] if args else ''}")

    # ============================================================
    # STRIPE WEBHOOKS
    # ============================================================

    def _handle_stripe(self, body: bytes):
        """Process Stripe webhook events."""
        try:
            event = json.loads(body)
            event_type = event.get("type", "unknown")
            logger.info(f"💰 Stripe webhook: {event_type}")

            if event_type == "checkout.session.completed":
                self._process_stripe_sale(event["data"]["object"])
            elif event_type == "payment_intent.succeeded":
                self._process_stripe_payment(event["data"]["object"])
            elif event_type == "customer.subscription.created":
                self._process_stripe_subscription(event["data"]["object"])

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"received": true}')

        except Exception as e:
            logger.error(f"Stripe webhook error: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _process_stripe_sale(self, session: dict):
        """Process a completed checkout session."""
        revenue = get_revenue_agent()
        if revenue:
            revenue.record_sale(
                product_id=session.get("metadata", {}).get("product_id", "unknown"),
                amount_cents=session.get("amount_total", 0),
                customer_email=session.get("customer_email", ""),
                source="stripe_checkout",
                stripe_id=session.get("id", "")
            )

        memory = get_memory()
        if memory:
            email = session.get("customer_email", "")
            memory.remember_revenue_signal(
                username=email,
                signal_type="purchase",
                product_id=session.get("metadata", {}).get("product_id", ""),
                context=f"Purchased via Stripe checkout: ${session.get('amount_total', 0)/100:.2f}"
            )

        self._send_slack_notification(
            f"💰 New sale! ${session.get('amount_total', 0)/100:.2f} "
            f"from {session.get('customer_email', 'unknown')}"
        )

    def _process_stripe_payment(self, payment: dict):
        """Process a successful payment intent."""
        logger.info(f"Payment succeeded: ${payment.get('amount', 0)/100:.2f}")

    def _process_stripe_subscription(self, sub: dict):
        """Process a new subscription."""
        logger.info(f"New subscription: {sub.get('id', 'unknown')}")
        self._send_slack_notification(
            f"🔄 New subscription! Plan: {sub.get('plan', {}).get('nickname', 'unknown')}"
        )

    # ============================================================
    # LEMON SQUEEZY WEBHOOKS
    # ============================================================

    def _handle_lemonsqueezy(self, body: bytes):
        """Process Lemon Squeezy webhook events."""
        try:
            payload = json.loads(body)
            event_type = payload.get("meta", {}).get("event_name", "unknown")
            logger.info(f"🍋 Lemon Squeezy webhook: {event_type}")

            if event_type == "order_created":
                data = payload.get("data", {}).get("attributes", {})
                revenue = get_revenue_agent()
                if revenue:
                    revenue.record_sale(
                        product_id=data.get("first_order_item", {}).get("product_name", "unknown"),
                        amount_cents=int(float(data.get("total", 0)) * 100),
                        customer_email=data.get("user_email", ""),
                        source="lemonsqueezy",
                        stripe_id=f"ls_{data.get('id', '')}"
                    )

                self._send_slack_notification(
                    f"🍋 LS Sale! ${float(data.get('total', 0)):.2f} "
                    f"— {data.get('first_order_item', {}).get('product_name', 'unknown')}"
                )

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"received": true}')

        except Exception as e:
            logger.error(f"LS webhook error: {e}")
            self.send_response(400)
            self.end_headers()

    # ============================================================
    # TEST WEBHOOK
    # ============================================================

    def _handle_test(self, body: bytes):
        """Test endpoint for verifying webhook setup."""
        logger.info(f"Test webhook received: {body[:100]}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "received": True,
            "timestamp": datetime.now().isoformat()
        }).encode())

    # ============================================================
    # NOTIFICATIONS
    # ============================================================

    def _send_slack_notification(self, message: str):
        """Send a notification to Slack."""
        if not SLACK_BOT_TOKEN or not SLACK_NEWSLETTER_CHANNEL:
            logger.info(f"Slack notification (not sent): {message}")
            return

        try:
            import requests
            requests.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
                json={
                    "channel": SLACK_NEWSLETTER_CHANNEL,
                    "text": message,
                    "unfurl_links": False
                },
                timeout=5
            )
        except Exception as e:
            logger.warning(f"Slack notification failed: {e}")


def run_webhook_server(port: int = WEBHOOK_PORT):
    """Start the webhook server."""
    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    print(f"🔔 Webhook server running on port {port}")
    print(f"   Stripe:  POST /webhooks/stripe")
    print(f"   LS:      POST /webhooks/lemonsqueezy")
    print(f"   Health:  GET  /health")
    print(f"   Test:    POST /webhooks/test")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Webhook server stopped")
        server.server_close()


if __name__ == "__main__":
    run_webhook_server()
