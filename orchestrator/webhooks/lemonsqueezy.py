"""
Lemon Squeezy Webhook Handler
Receives sale notifications and triggers email alerts + revenue sync.

Add to Cloud Run health server or run as standalone Flask endpoint.
Configure webhook URL in LS dashboard → Settings → Webhooks:
  https://swarm-scheduler-793665873420.us-east1.run.app/webhook/lemonsqueezy
"""

import json
import hashlib
import hmac
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

_ENV = Path(__file__).parent.parent.parent / "config" / ".env"
load_dotenv(_ENV, override=True)

# Set this in LS Dashboard → Settings → Webhooks → Signing Secret
LS_WEBHOOK_SECRET = os.getenv("LS_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Lemon Squeezy webhook signature."""
    if not LS_WEBHOOK_SECRET:
        return True  # Skip verification if no secret configured
    expected = hmac.new(
        LS_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def handle_webhook(payload: bytes, headers: dict) -> dict:
    """Process a Lemon Squeezy webhook event.
    
    Returns dict with status and action taken.
    """
    # Verify signature
    signature = headers.get("X-Signature", "")
    if not verify_signature(payload, signature):
        return {"status": "rejected", "reason": "invalid signature"}

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return {"status": "rejected", "reason": "invalid JSON"}

    event_name = data.get("meta", {}).get("event_name", "unknown")
    
    # Route events
    if event_name == "order_created":
        return _handle_order(data)
    elif event_name == "subscription_created":
        return _handle_subscription(data)
    else:
        print(f"  [WEBHOOK] Unhandled event: {event_name}")
        return {"status": "ignored", "event": event_name}


def _handle_order(data: dict) -> dict:
    """Handle new order — send notification email + log."""
    attrs = data.get("data", {}).get("attributes", {})
    
    product_name = attrs.get("first_order_item", {}).get("product_name", "Unknown")
    total = attrs.get("total", 0) / 100  # cents to dollars
    customer_email = attrs.get("user_email", "")
    customer_name = attrs.get("user_name", "")
    
    print(f"  [WEBHOOK] 💰 New order: {product_name} — ${total:.2f} from {customer_email}")
    
    # Send internal notification
    try:
        from orchestrator.utils.email_client import send_sale_notification
        send_sale_notification(product_name, total, customer_email)
    except Exception as e:
        print(f"  [WEBHOOK] Email notification failed: {e}")
    
    # Log to file for revenue tracking
    _log_sale(product_name, total, customer_email, customer_name)
    
    return {
        "status": "processed",
        "event": "order_created",
        "product": product_name,
        "amount": total,
    }


def _handle_subscription(data: dict) -> dict:
    """Handle new subscription."""
    attrs = data.get("data", {}).get("attributes", {})
    product_name = attrs.get("product_name", "Unknown")
    customer_email = attrs.get("user_email", "")
    
    print(f"  [WEBHOOK] 🔁 New subscription: {product_name} from {customer_email}")
    return {"status": "processed", "event": "subscription_created"}


def _log_sale(product: str, amount: float, email: str, name: str):
    """Append sale to local revenue log."""
    log_dir = Path(__file__).parent.parent.parent / "output" / "revenue"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "sales_log.jsonl"
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "product": product,
        "amount": amount,
        "customer_email": email,
        "customer_name": name,
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"  [WEBHOOK] Logged sale to {log_file}")
