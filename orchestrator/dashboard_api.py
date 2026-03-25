"""
E-Labz Dashboard API v2 — Revenue + Memory + Swarm Status
Serves metrics to the dashboard UI on port 8080.
"""

import json
import os
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.intelligence.metrics import get_daily_metrics, get_monthly_revenue, get_growth_metrics

try:
    from orchestrator.revenue_agent import get_revenue_agent
except ImportError:
    def get_revenue_agent(): return None

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_header('Access-Control-Allow-Origin', '*')

        if self.path == '/api/metrics':
            self._serve_metrics()
        elif self.path == '/api/revenue':
            self._serve_revenue()
        elif self.path == '/api/memory':
            self._serve_memory_stats()
        elif self.path == '/api/swarm':
            self._serve_swarm_status()
        elif self.path == '/health':
            self._json_response({"status": "ok", "timestamp": datetime.now().isoformat()})
        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def _serve_metrics(self):
        try:
            current = get_daily_metrics()
            revenue = get_monthly_revenue()
            growth = get_growth_metrics(days=10)

            history = []
            db_path = Path(__file__).parent.parent / "data" / "metrics.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT date as timestamp, follower_total as followers,
                           revenue as revenue_today, posts_published as total_posts
                    FROM daily_metrics ORDER BY date DESC LIMIT 10
                """).fetchall()
                history = [dict(r) for r in reversed(rows)]
                conn.close()

            # Add revenue agent data
            rev_data = {}
            rev = get_revenue_agent()
            if rev:
                rev_data = rev.get_revenue_report()

            self._json_response({
                "current": current or (history[-1] if history else {}),
                "revenue": revenue,
                "revenue_agent": rev_data,
                "growth": growth,
                "history": history
            })

        except Exception as e:
            self._json_response({"error": str(e)}, 500)

    def _serve_revenue(self):
        rev = get_revenue_agent()
        if rev:
            self._json_response(rev.get_revenue_report())
        else:
            self._json_response({"error": "Revenue agent not available"}, 503)

    def _serve_memory_stats(self):
        mem = get_memory()
        if not mem:
            self._json_response({"error": "Memory service not available"}, 503)
            return

        try:
            conn = sqlite3.connect(str(mem.db_path))
            stats = {}
            for table in ["relationships", "strategies", "content_memory", "revenue_signals"]:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    stats[table] = count
                except:
                    stats[table] = 0
            conn.close()
            self._json_response({"memory_stats": stats, "mode": mem.mode})
        except Exception as e:
            self._json_response({"error": str(e)}, 500)

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
            {"name": "Voice Agent", "status": "ready", "icon": "🎙️"},
            {"name": "Analytics Agent", "status": "active", "icon": "📊"},
        ]
        self._json_response({"agents": agents, "total": len(agents), "active": sum(1 for a in agents if a["status"] == "active")})

    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def run_api(port=8080):
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"📊 Dashboard API v2 running on port {port}")
    print(f"   /api/metrics  — Full metrics + revenue")
    print(f"   /api/revenue  — Revenue agent report")
    print(f"   /api/memory   — Memory service stats")
    print(f"   /api/swarm    — Agent status")
    print(f"   /health       — Health check")
    server.serve_forever()


if __name__ == "__main__":
    run_api()
