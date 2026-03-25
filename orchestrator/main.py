"""
E-Labz Swarm — Unified Entry Point for Cloud Run
Runs the dashboard API + scheduler in a single process on one port.
Cloud Run only exposes one port, so we combine everything here.
"""

import json
import os
import signal
import sys
import threading
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from dotenv import load_dotenv

# Load environment (local dev: config/.env, Cloud Run: env vars injected)
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)

PORT = int(os.getenv("PORT", "8080"))


# ──────────────────────────────────────────────────────────────
# Dashboard API Handler (health + metrics)
# ──────────────────────────────────────────────────────────────

class SwarmHandler(BaseHTTPRequestHandler):
    """Serves health checks, metrics, and status."""

    def do_GET(self):
        if self.path == "/health":
            self._json({"status": "ok", "uptime": _uptime(), "timestamp": datetime.now().isoformat()})
        elif self.path == "/api/metrics":
            self._serve_metrics()
        elif self.path == "/api/swarm":
            self._serve_swarm_status()
        elif self.path == "/api/revenue":
            self._serve_revenue()
        elif self.path == "/":
            self._json({
                "service": "E-Labz Swarm",
                "version": "2.0",
                "status": "running",
                "endpoints": ["/health", "/api/metrics", "/api/swarm", "/api/revenue"],
            })
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def do_POST(self):
        """Handle webhook POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""

        if self.path == "/webhooks/stripe":
            self._handle_stripe_webhook(body)
        else:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "not found"}).encode())

    def _json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _serve_metrics(self):
        try:
            from orchestrator.intelligence.metrics import get_daily_metrics, get_monthly_revenue, get_growth_metrics
            self._json({
                "current": get_daily_metrics() or {},
                "revenue": get_monthly_revenue() or {},
                "growth": get_growth_metrics(days=10) or {},
            })
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _serve_swarm_status(self):
        agents = [
            {"name": "Research Agent", "status": "active", "icon": "🔍"},
            {"name": "Content Agent", "status": "active", "icon": "✍️"},
            {"name": "Human Voice Engine", "status": "active", "icon": "🛡️"},
            {"name": "Twitter Agent", "status": "active", "icon": "📱"},
            {"name": "Memory Agent", "status": "active", "icon": "🧠"},
            {"name": "Revenue Agent", "status": "active", "icon": "💰"},
            {"name": "Engagement Agent", "status": "active", "icon": "💬"},
            {"name": "ADK Coordinator", "status": "active", "icon": "🎛️"},
        ]
        self._json({"agents": agents, "total": len(agents), "scheduler_running": _scheduler_alive()})

    def _serve_revenue(self):
        try:
            from orchestrator.revenue_agent import get_revenue_agent
            rev = get_revenue_agent()
            if rev:
                self._json(rev.get_revenue_report())
            else:
                self._json({"error": "Revenue agent not initialized"}, 503)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _handle_stripe_webhook(self, body: bytes):
        try:
            from orchestrator.webhook_handler import handle_stripe_event
            event = json.loads(body)
            handle_stripe_event(event)
            self._json({"received": True})
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def log_message(self, format, *args):
        # Only log errors, suppress routine request logs
        if args and len(args) > 1 and str(args[1]).startswith("5"):
            print(f"⚠️ HTTP {args[1]}: {args[0]}")


# ──────────────────────────────────────────────────────────────
# Scheduler Thread
# ──────────────────────────────────────────────────────────────

_start_time = datetime.now()
_scheduler_thread = None


def _uptime() -> str:
    delta = datetime.now() - _start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def _scheduler_alive() -> bool:
    return _scheduler_thread is not None and _scheduler_thread.is_alive()


def run_scheduler_background():
    """Run the scheduler in a background thread."""
    try:
        from orchestrator.core.scheduler import setup_schedule, run_metrics_sync
        import schedule as sched

        setup_schedule()

        # Initial metrics sync
        print("📡 Initial metrics sync...")
        try:
            run_metrics_sync()
        except Exception as e:
            print(f"   ⚠️ Initial sync failed (non-fatal): {e}")

        print(f"🚀 Scheduler running. Next job: {sched.next_run()}")

        while True:
            sched.run_pending()
            time.sleep(30)
    except Exception as e:
        print(f"❌ Scheduler crashed: {e}")
        import traceback
        traceback.print_exc()


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main():
    """Start the API server + scheduler."""
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

    print("=" * 60)
    print("  E-LABZ SWARM — Cloud Run Edition")
    print(f"  Port: {PORT}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Validate critical env vars
    critical = ["OPENAI_API_KEY"]
    missing = [k for k in critical if not os.getenv(k)]
    if missing:
        print(f"⚠️ Missing env vars: {', '.join(missing)} — some features disabled")

    # Start scheduler in background thread
    global _scheduler_thread
    _scheduler_thread = threading.Thread(target=run_scheduler_background, daemon=True, name="scheduler")
    _scheduler_thread.start()

    # Start HTTP server (foreground — Cloud Run expects this)
    server = HTTPServer(("0.0.0.0", PORT), SwarmHandler)
    print(f"\n📊 API server listening on 0.0.0.0:{PORT}")
    print(f"   GET  /health         — health check")
    print(f"   GET  /api/metrics    — dashboard metrics")
    print(f"   GET  /api/swarm      — agent status")
    print(f"   GET  /api/revenue    — revenue report")
    print(f"   POST /webhooks/stripe — Stripe webhooks\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
