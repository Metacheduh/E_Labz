"""
Free Cash Flow — Root Agent (DEPRECATED)

⚠️  This module is NOT used by the scheduler (scheduler.py calls modules directly).
    It was intended as a unified agent abstraction but was never wired in.
    Kept for reference — may be wired in as a proper agent interface later.
    For now, use the individual orchestrator modules directly:
      - orchestrator.twitter (posting)
      - orchestrator.reply_engine (engagement)
      - orchestrator.research (topic discovery)
      - orchestrator.humanize (content humanization)
      - orchestrator.self_learn (daily analysis)
      - orchestrator.store (product/revenue)

Deprecated: 2026-03-19
"""

import os
from pathlib import Path

from orchestrator.humanize import publish, verify_human
from orchestrator.metrics import (
    get_daily_metrics,
    get_growth_metrics,
    get_monthly_revenue,
    log_daily_metrics,
    log_post_metrics,
)
from orchestrator.self_learn import run_daily_review


# ============================================================
# AGENT ROUTER
# ============================================================

class SwarmAgent:
    """The root agent that coordinates all sub-agents."""

    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.output_dir = Path(__file__).parent.parent / "output"
        self.agents_dir = Path(__file__).parent.parent / "agents"
        self.kill_switch = False

    def research(self, topic: str = "") -> dict:
        """Route research task to GPT Researcher + Brave Search."""
        print(f"🔬 Research: {topic or 'trending topics'}")
        # TODO: Call agents/researcher/main.py
        return {"status": "pending", "topic": topic}

    def generate_video(self, script: str = "", topic: str = "") -> dict:
        """Route video generation to Faceless Video Generator."""
        print(f"🎬 Video: {topic}")
        # TODO: Call agents/video
        return {"status": "pending", "topic": topic}

    def create_product(self, title: str = "", topic: str = "") -> dict:
        """Route product creation to eBook Generator."""
        print(f"📦 Product: {title or topic}")
        # TODO: Call agents/product
        return {"status": "pending", "title": title}

    def post_to_twitter(self, content: str, content_type: str = "tweet") -> dict:
        """Humanize content and post to Twitter/X."""
        # ALWAYS go through the Human Voice Engine
        humanized = publish(content, content_type=content_type)

        if humanized is None:
            return {"status": "failed", "reason": "Failed humanization (<5% AI detection)"}

        print(f"📤 Posting: {humanized[:80]}...")
        # TODO: Call agents/twitter
        return {"status": "pending", "content": humanized}

    def engage(self) -> dict:
        """Route engagement task to Growth Agent."""
        print("💬 Engaging with audience...")
        # TODO: Call agents/growth
        return {"status": "pending"}

    def check_revenue(self) -> dict:
        """Check revenue metrics and projections."""
        return get_monthly_revenue()

    def check_growth(self, days: int = 7) -> dict:
        """Check follower growth metrics."""
        return get_growth_metrics(days)

    def self_learn(self) -> dict:
        """Trigger the daily self-learning review + newsletter."""
        return run_daily_review()

    def kill(self):
        """Emergency shutdown."""
        self.kill_switch = True
        print("🛑 KILL SWITCH ACTIVATED — all operations stopped")
        return {"status": "killed"}

    def status(self) -> dict:
        """Get current swarm status."""
        return {
            "kill_switch": self.kill_switch,
            "today": get_daily_metrics(),
            "revenue": get_monthly_revenue(),
            "growth": get_growth_metrics(7),
        }


# Singleton instance
agent = SwarmAgent()
