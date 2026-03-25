"""
E-Labz ADK Bridge v2 — Wired into Coordinator + Memory + Revenue
Bridge between ADK agent pipelines and the swarm orchestrator.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import logger
except ImportError:
    import logging
    logger = logging.getLogger("adk_bridge")

try:
    from orchestrator.memory_service import get_memory
except ImportError:
    def get_memory(): return None

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "adk"


def run_leadgen(target_market: str = "AI startups") -> list:
    """Bridge to the LeadGen ADK pipeline with memory integration."""
    logger.info(f"🚀 Running ADK LeadGen for: {target_market}")
    try:
        from ADK_Pipelines.leadgen.agent import root_agent as leadgen_agent
        
        state = {"target_market": target_market}
        result = leadgen_agent.run(state)
        
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        leads = result.get("enriched_leads", [])
        
        output_file = OUTPUT_DIR / "latest_leads.json"
        output_file.write_text(json.dumps(leads, indent=2))
        
        # Save to memory for targeting
        memory = get_memory()
        if memory and leads:
            memory.remember_strategy(
                "leadgen_results",
                datetime.now().strftime("%Y-%m-%d"),
                min(len(leads) / 10.0, 1.0),
                f"Found {len(leads)} leads for {target_market}"
            )
        
        logger.info(f"✅ LeadGen: {len(leads)} leads found")
        return leads
        
    except ImportError:
        logger.info("ADK LeadGen pipeline not available")
        return []
    except Exception as e:
        logger.warning(f"ADK LeadGen error: {e}")
        return []


def run_content_engine(niche: str = "AI automation") -> list:
    """Bridge to the ContentEngine ADK pipeline with memory integration."""
    logger.info(f"🚀 Running ADK ContentEngine for: {niche}")
    try:
        from ADK_Pipelines.contentengine.agent import root_agent as content_agent
        
        state = {"niche": niche}
        result = content_agent.run(state)
        
        posts = []
        for i in range(1, 6):
            post = result.get(f"post_{i}")
            if post:
                posts.append(post)
        
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / "latest_posts.json"
        output_file.write_text(json.dumps(posts, indent=2))
        
        # Feed into tweet cache for the scheduler
        _feed_to_tweet_cache(posts)
        
        # Save to memory
        memory = get_memory()
        if memory and posts:
            memory.remember_strategy(
                "content_engine",
                datetime.now().strftime("%Y-%m-%d"),
                min(len(posts) / 5.0, 1.0),
                f"Generated {len(posts)} posts for {niche}"
            )
        
        logger.info(f"✅ ContentEngine: {len(posts)} posts generated")
        return posts
        
    except ImportError:
        logger.info("ADK ContentEngine pipeline not available")
        return []
    except Exception as e:
        logger.warning(f"ADK ContentEngine error: {e}")
        return []


def run_site_audit(url: str = "https://e-labz.netlify.app") -> dict:
    """Bridge to the SiteAudit ADK pipeline."""
    logger.info(f"🚀 Running ADK SiteAudit for: {url}")
    try:
        from ADK_Pipelines.siteaudit.agent import root_agent as audit_agent
        
        state = {"url": url}
        result = audit_agent.run(state)
        
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / "latest_audit.json"
        output_file.write_text(json.dumps(result, indent=2, default=str))
        
        return result
        
    except ImportError:
        logger.info("ADK SiteAudit pipeline not available")
        return {"status": "unavailable"}
    except Exception as e:
        logger.warning(f"ADK SiteAudit error: {e}")
        return {"status": "error", "message": str(e)}


def _feed_to_tweet_cache(posts: list):
    """Feed ADK content output into the tweet cache for posting."""
    try:
        cache_path = Path(__file__).parent.parent / "output" / "research" / "tweet_cache.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        existing = []
        if cache_path.exists():
            existing = json.loads(cache_path.read_text())
        
        # Extract tweetable snippets from posts
        for post in posts:
            if isinstance(post, str) and len(post) > 20:
                # Trim to tweet length
                snippet = post[:270] if len(post) > 270 else post
                if snippet not in existing:
                    existing.append(snippet)
            elif isinstance(post, dict):
                title = post.get("title", "")
                if title and title not in existing:
                    existing.append(title[:270])
        
        # Keep last 50 items
        existing = existing[-50:]
        cache_path.write_text(json.dumps(existing, indent=2))
        
    except Exception as e:
        logger.warning(f"Tweet cache feed failed: {e}")


if __name__ == "__main__":
    print("Testing ADK Bridge v2...")
    leads = run_leadgen("AI automation agencies")
    print(f"Leads: {len(leads)}")
    
    posts = run_content_engine("AI agents")
    print(f"Posts: {len(posts)}")
    
    print("✅ ADK Bridge v2 working")
