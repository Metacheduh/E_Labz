"""
E-Labz Multi-Platform Content Adapters
Transforms tweets into formatted content for LinkedIn, Medium, Dev.to, and newsletter.

Each adapter takes a tweet/thread and reformats it for the target platform.
"""

import os
import json
from datetime import datetime
from pathlib import Path

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("platform_adapters")

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None


# ============================================================
# LINKEDIN ADAPTER
# ============================================================

class LinkedInAdapter:
    """Convert tweet content → LinkedIn post format."""

    def adapt(self, tweet_text: str, thread: list = None) -> str:
        """Format content for LinkedIn."""
        if thread:
            # Thread → LinkedIn carousel-style post
            hook = thread[0]
            body_points = thread[1:-1]  # Skip hook and CTA
            cta = thread[-1]

            post = f"{hook}\n\n"
            for point in body_points:
                post += f"→ {point}\n\n"
            post += f"---\n{cta}\n\n"
            post += "#AI #Automation #AIAgents #BuildInPublic #Entrepreneurship"
        else:
            # Single tweet → LinkedIn post with context
            post = f"{tweet_text}\n\n"
            post += "What's your take? Drop a comment below.\n\n"
            post += "#AI #AIAgents #BuildInPublic"

        return post

    def get_hashtags(self, topic: str = "") -> str:
        tags = ["#AI", "#Automation", "#BuildInPublic", "#AIAgents"]
        if "agent" in topic.lower():
            tags.append("#AgentAI")
        if "revenue" in topic.lower() or "money" in topic.lower():
            tags.append("#Entrepreneurship")
        return " ".join(tags)


# ============================================================
# MEDIUM ADAPTER
# ============================================================

class MediumAdapter:
    """Convert thread content → Medium article draft."""

    def adapt(self, thread: list, title: str = "") -> dict:
        """Format thread as Medium article structure."""
        if not title:
            title = thread[0][:80] if thread else "AI Automation Insights"

        # Build article body from thread points
        body = f"# {title}\n\n"
        body += f"*Originally shared on Twitter — expanded with additional context.*\n\n"

        for i, tweet in enumerate(thread):
            if i == 0:
                body += f"{tweet}\n\n---\n\n"
            elif i == len(thread) - 1:
                body += f"## What's Next?\n\n{tweet}\n\n"
            else:
                body += f"## Point {i}\n\n{tweet}\n\n"

        body += "---\n\n"
        body += "*I'm building an autonomous AI business engine in public. "
        body += "Follow along on [Twitter](https://twitter.com/AutoStackHQ) "
        body += "or check out the tools at [E-Labz](https://e-labz.netlify.app).*\n"

        return {
            "title": title,
            "body": body,
            "tags": ["artificial-intelligence", "automation", "ai-agents", "entrepreneurship", "building-in-public"],
            "status": "draft"
        }


# ============================================================
# DEV.TO ADAPTER
# ============================================================

class DevToAdapter:
    """Convert technical thread → Dev.to article with frontmatter."""

    def adapt(self, thread: list, title: str = "", series: str = "AI Agent Chronicles") -> str:
        """Format thread as Dev.to markdown with frontmatter."""
        if not title:
            title = thread[0][:80] if thread else "Building AI Agents"

        # Dev.to frontmatter
        article = f"""---
title: "{title}"
published: false
description: "{thread[0][:150] if thread else 'AI automation insights'}"
tags: ai, automation, agents, python
series: {series}
cover_image:
---

"""
        for i, tweet in enumerate(thread):
            if i == 0:
                article += f"{tweet}\n\n"
            elif i == len(thread) - 1:
                article += f"## Next Steps\n\n{tweet}\n\n"
            else:
                article += f"### {tweet[:60]}...\n\n{tweet}\n\n"

        article += "---\n\n"
        article += "🔗 [E-Labz](https://e-labz.netlify.app) — AI Products Shipped in Weeks\n"

        return article


# ============================================================
# NEWSLETTER ADAPTER
# ============================================================

class NewsletterAdapter:
    """Convert thread → email newsletter format."""

    def adapt(self, thread: list, subject: str = "") -> dict:
        """Format thread as email newsletter."""
        if not subject:
            subject = f"🧠 {thread[0][:50]}..." if thread else "AI Swarm Weekly"

        html = f"""<div style="max-width:600px;margin:0 auto;font-family:system-ui,-apple-system,sans-serif;color:#e0e0e0;background:#0a0a0a;padding:32px;">
    <div style="text-align:center;padding-bottom:24px;border-bottom:1px solid #222;">
        <h1 style="color:#fff;font-size:24px;margin:0;">⚡ E-Labz Weekly</h1>
        <p style="color:#888;font-size:14px;margin:8px 0 0;">AI automation insights from the swarm</p>
    </div>
"""

        for i, tweet in enumerate(thread):
            if i == 0:
                html += f'    <h2 style="color:#06d6a0;font-size:20px;margin:24px 0 12px;">{tweet}</h2>\n'
            elif i == len(thread) - 1:
                html += f'    <div style="background:#111;padding:16px;border-radius:8px;margin:16px 0;border-left:3px solid #4361ee;">{tweet}</div>\n'
            else:
                html += f'    <p style="font-size:16px;line-height:1.6;margin:12px 0;">→ {tweet}</p>\n'

        html += """
    <div style="text-align:center;padding-top:24px;border-top:1px solid #222;margin-top:24px;">
        <a href="https://e-labz.netlify.app" style="color:#4361ee;text-decoration:none;">Visit E-Labz</a>
        <span style="color:#333;padding:0 8px;">|</span>
        <a href="https://twitter.com/AutoStackHQ" style="color:#4361ee;text-decoration:none;">Follow on Twitter</a>
    </div>
</div>"""

        return {
            "subject": subject,
            "html": html,
            "text": "\n\n".join(thread),
            "status": "draft"
        }


# ============================================================
# PLATFORM MANAGER
# ============================================================

class PlatformManager:
    """Coordinate content distribution across all platforms."""

    def __init__(self):
        self.linkedin = LinkedInAdapter()
        self.medium = MediumAdapter()
        self.devto = DevToAdapter()
        self.newsletter = NewsletterAdapter()

    def distribute(self, thread: list, platforms: list = None) -> dict:
        """Distribute thread content to multiple platforms."""
        if platforms is None:
            platforms = ["linkedin", "medium", "devto", "newsletter"]

        results = {}
        output_dir = Path(__file__).parent.parent / "output" / "platforms"
        output_dir.mkdir(parents=True, exist_ok=True)

        for platform in platforms:
            try:
                if platform == "linkedin":
                    content = self.linkedin.adapt(None, thread)
                    results["linkedin"] = {"content": content, "status": "ready"}
                elif platform == "medium":
                    article = self.medium.adapt(thread)
                    results["medium"] = article
                elif platform == "devto":
                    article = self.devto.adapt(thread)
                    results["devto"] = {"content": article, "status": "ready"}
                elif platform == "newsletter":
                    email = self.newsletter.adapt(thread)
                    results["newsletter"] = email
            except Exception as e:
                results[platform] = {"error": str(e)}

        # Save all outputs
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = output_dir / f"distribution_{timestamp}.json"
        output_file.write_text(json.dumps(results, indent=2, default=str))

        # Log to memory
        memory = get_memory()
        if memory:
            memory.remember_content(
                content_text=thread[0] if thread else "",
                content_type="multi_platform",
                topic=f"Distributed to {', '.join(platforms)}"
            )

        logger.info(f"📡 Content distributed to {len(results)} platforms")
        return results


# Singleton
_manager = None

def get_platform_manager() -> PlatformManager:
    global _manager
    if _manager is None:
        _manager = PlatformManager()
    return _manager


if __name__ == "__main__":
    test_thread = [
        "I built an AI swarm that runs my business 24/7. Here's how:",
        "1. Research agent scans 50+ sources daily",
        "2. Content agent drafts with human voice engine",
        "3. Revenue agent tracks Stripe sales automatically",
        "Full breakdown in bio. What would you automate first?"
    ]

    manager = get_platform_manager()
    results = manager.distribute(test_thread)

    for platform, data in results.items():
        print(f"\n{'='*40}")
        print(f"📡 {platform.upper()}")
        print(f"{'='*40}")
        if isinstance(data, dict) and "content" in data:
            print(data["content"][:200] + "...")
        elif isinstance(data, dict) and "body" in data:
            print(data["body"][:200] + "...")
        elif isinstance(data, dict) and "html" in data:
            print(data["subject"])

    print(f"\n✅ Distributed to {len(results)} platforms")
