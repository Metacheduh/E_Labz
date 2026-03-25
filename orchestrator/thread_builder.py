"""
E-Labz Thread Builder v2 — LLM-Powered Threads with Memory + Revenue CTAs
Generates high-engagement threads from research data with smart product mentions.
"""

import json
import os
import random
import hashlib
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("thread_builder")

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None

try:
    from orchestrator.revenue_agent import get_revenue_agent
except ImportError:
    def get_revenue_agent(): return None

RESEARCH_CACHE_PATH = Path(__file__).parent.parent / "output" / "research" / "tweet_cache.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============================================================
# THREAD TEMPLATES (Human voice — no AI speak)
# ============================================================

THREAD_TEMPLATES = [
    {
        "type": "tutorial",
        "hook": "I built an AI swarm that runs my business 24/7. Research, content, posting, engagement — all autonomous. Here's exactly how it works:",
        "cta": "I put the full technical breakdown in a guide. Link in bio if you want it."
    },
    {
        "type": "comparison",
        "hook": "Most AI tools are noise. I tested 47 of them over 6 months. Here are the only 5 that actually move the needle:",
        "cta": "Want the full breakdown with configs? Free stack guide in my bio."
    },
    {
        "type": "behind_the_scenes",
        "hook": "The difference between an AI hobby and an AI business is automation. Here's what my daily workflow actually looks like:",
        "cta": "If you want to build your own — we have 2 build slots left this quarter. Link in bio."
    },
    {
        "type": "money",
        "hook": "I replaced $500/month in SaaS tools with an AI stack that costs $70. Here's the exact swap list:",
        "cta": "Full tool-by-tool comparison in the free guide. Link in bio."
    },
    {
        "type": "mistakes",
        "hook": "5 mistakes I made building AI automations (so you don't have to):",
        "cta": "I documented all the fixes in the AI Automation Playbook. Grab it from the link in bio."
    },
    {
        "type": "framework",
        "hook": "The 3-agent framework that runs my content engine. Took 6 months to figure out, sharing it in 60 seconds:",
        "cta": "Full agent configs and code in the Swarm Playbook. Link in bio."
    }
]

VALUE_POINTS = [
    "Research agent scans 50+ sources daily using Tavily + Brave. Finds trending topics before they blow up.",
    "Content agent writes drafts, then the Human Voice Engine runs them through 5 detox stages. Under 5% AI detection.",
    "Engagement agent remembers every conversation. It knows who you talked to last week and what they care about.",
    "Revenue agent tracks every sale, generates smart CTAs based on what topics are trending, and syncs with Stripe automatically.",
    "The self-learning loop reviews performance every night. Bad content styles get deprioritized. Winners get amplified.",
    "Browser automation handles Twitter posting — no API fees, no rate limits, no third-party risk.",
    "Memory service stores relationship history across sessions. The swarm gets smarter with every interaction.",
    "Everything runs on a scheduler. 15+ jobs from 7am to midnight. Research, content, posting, engagement, analytics.",
    "Thread builder pulls from real research data. No generic AI slop — every thread has specific tools, numbers, and results.",
    "Voice agent converts top tweets into audio clips. Same brand voice across text and audio.",
]


def build_thread(count: int = 5, topic: str = "") -> list[str]:
    """Build a high-quality thread from research data and templates."""
    try:
        # Load fresh ideas from research cache
        ideas = []
        if RESEARCH_CACHE_PATH.exists():
            raw = json.loads(RESEARCH_CACHE_PATH.read_text())
            if isinstance(raw, list):
                ideas = [str(i) for i in raw if i]

        # Try LLM-powered thread generation
        if OPENAI_API_KEY and topic:
            llm_thread = _generate_llm_thread(topic, count)
            if llm_thread:
                return llm_thread

        # Fallback: template-based thread
        template = random.choice(THREAD_TEMPLATES)

        # Pick value points (mix research + defaults)
        available_points = ideas[:10] if ideas else []
        available_points.extend(random.sample(VALUE_POINTS, min(5, len(VALUE_POINTS))))
        random.shuffle(available_points)

        points = available_points[:count - 2]

        # Assemble: Hook → Points → CTA → Engagement closer
        thread = [template["hook"]]
        for i, point in enumerate(points):
            # Clean up — remove existing numbering if present
            clean = point.lstrip("0123456789. ")
            thread.append(f"{i+1}. {clean}")

        # Add smart CTA from revenue agent
        revenue = get_revenue_agent()
        if revenue and random.random() < 0.4:
            cta = revenue.get_smart_cta(topic or "AI automation")
            thread.append(cta["cta_text"])
        else:
            thread.append(template["cta"])

        # Engagement closer
        closers = [
            "What would you automate first? Drop a reply.",
            "Which of these surprised you the most?",
            "Running anything similar? I want to hear about it.",
            "What's the one tool you can't live without? Curious.",
            "Building in public — what should I share next?",
        ]
        thread.append(random.choice(closers))

        # Save to memory
        memory = get_memory()
        if memory:
            memory.remember_content(
                content_text=thread[0],
                content_type="thread",
                topic=topic or template["type"]
            )

        return thread

    except Exception as e:
        logger.warning(f"Thread builder error: {e}")
        return _fallback_thread()


def _generate_llm_thread(topic: str, count: int) -> list[str]:
    """Generate a thread using GPT-4o-mini."""
    try:
        import requests
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": (
                        "You write Twitter threads for an AI automation brand. "
                        "Rules: casual tone, no AI buzzwords (never say leverage, comprehensive, innovative, cutting-edge, delve), "
                        "use specific numbers and tools, sound like a helpful friend not a corporation. "
                        "Each tweet must be under 270 characters. "
                        f"Return exactly {count} tweets as a JSON array of strings."
                    )},
                    {"role": "user", "content": f"Write a thread about: {topic}"}
                ],
                "temperature": 0.8,
                "max_tokens": 1000
            },
            timeout=15
        )
        data = resp.json()
        content = data["choices"][0]["message"]["content"]

        # Parse JSON array from response
        if "```" in content:
            content = content.split("```")[1].strip()
            if content.startswith("json"):
                content = content[4:].strip()

        tweets = json.loads(content)
        if isinstance(tweets, list) and len(tweets) >= 3:
            return [t[:280] for t in tweets]

    except Exception as e:
        logger.warning(f"LLM thread generation failed: {e}")

    return []


def _fallback_thread() -> list[str]:
    """Emergency fallback thread."""
    return [
        "My daily AI workflow takes about 12 minutes now. Here's how:",
        "1. Research agent finds trending topics automatically",
        "2. Content engine drafts posts, voice engine makes them human",
        "3. Browser automation handles posting — no API needed",
        "Full breakdown in bio. What would you automate first?"
    ]


if __name__ == "__main__":
    thread = build_thread(count=6, topic="AI agent memory systems")
    print("Generated thread:")
    for i, tweet in enumerate(thread):
        print(f"\n  [{i+1}] {tweet}")
    print(f"\n✅ Thread: {len(thread)} tweets")
