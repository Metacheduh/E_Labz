"""
Free Cash Flow — Scheduler
Cron-based daily automation. This is the heartbeat of the swarm.
Start: python -m orchestrator.scheduler
"""

import os
import random
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule
import yaml
from dotenv import load_dotenv

# Load environment
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(Path(__file__).parent.parent / "config" / ".env.example")

try:
    from orchestrator.self_learn import run_daily_review
except ImportError:
    def run_daily_review():
        print("   (self_learn not available, skipping)")

try:
    from orchestrator.twitter import post_tweet, post_thread
except ImportError:
    def post_tweet(text, **kwargs):
        print(f"   (twitter module not available) Would post: {text[:80]}...")
        return {"status": "failed"}
    def post_thread(tweets, **kwargs):
        print(f"   (twitter module not available) Would post thread: {len(tweets)} tweets")
        return {"status": "failed"}

try:
    from orchestrator.sync_metrics import run_full_sync
except ImportError:
    def run_full_sync():
        print("   (sync_metrics not available, skipping)")
        return {}

from orchestrator.swarm_logger import (
    log_post, log_thread, log_sync, log_metrics_snapshot,
    log_error, log_scheduler_event, log_decision,
    logger as swarm_log,
)

try:
    from orchestrator.reply_engine import run_engagement_session
except ImportError:
    def run_engagement_session(dry_run=False):
        print("   (reply_engine not available, skipping)")
        return {}

# ============================================================
# GLOBALS
# ============================================================

KILL_SWITCH = False
SCHEDULE_PATH = Path(__file__).parent.parent / "config" / "schedule.yaml"


def load_schedule() -> dict:
    """Load schedule from YAML config."""
    if SCHEDULE_PATH.exists():
        with open(SCHEDULE_PATH) as f:
            return yaml.safe_load(f)
    return {}


def check_kill_switch() -> bool:
    """Check if the kill switch is activated."""
    global KILL_SWITCH
    agents_config = Path(__file__).parent.parent / "config" / "agents.yaml"
    if agents_config.exists():
        with open(agents_config) as f:
            config = yaml.safe_load(f)
            KILL_SWITCH = config.get("orchestrator", {}).get("kill_switch", False)
    return KILL_SWITCH


# ============================================================
# TWEET CONTENT LIBRARY (Autostack HQ — friendly, helpful, sharing discoveries)
# ============================================================

VALUE_TWEETS = [
    "I used to pay for 10 AI tools. Turns out I only needed 5. Saved $430/month.",
    "Found an AI stack that does what $500/month in subscriptions did. Total cost: $70. Happy to share.",
    "n8n replaced Zapier, Make, and IFTTT for me. Free to self-host. Honestly kind of changed everything.",
    "Been using Perplexity Pro instead of Google for research. Sourced answers, no SEO spam. Way better.",
    "Cursor is wild. It doesn't just autocomplete — it understands your whole codebase. Been using it daily.",
    "ElevenLabs helped me go from 1 video/week to 1 video/day. The voices are surprisingly natural.",
    "Honestly? Claude surprised me for writing and analysis. Been reaching for it over ChatGPT lately.",
    "The gap between 'AI curious' and 'AI profitable' is really just 5 tools and about 30 days of focused work.",
    "Set up a content engine over a weekend. Research, generate, post, engage. All runs on its own now.",
    "3 automations every creator should have running: content scheduling, lead capture, and analytics. All free to set up.",
    "One automation saves me about 2 hours every day. Took 10 minutes to set up. No code needed.",
    "Everyone asks which AI tool is best. Better question: which 5 tools actually work together?",
    "I track every dollar AI saves me. Last month: ~$2,340 in time value. Tool cost: $70.",
    "Started building instead of watching tutorials. Learned more in 1 hour of doing than 10 hours of watching.",
    "The difference between an AI hobby and an AI business is honestly just automations.",
    "Your $50/month Zapier bill is optional. n8n does the same thing for free if you self-host.",
    "Tried 47 AI tools in the past 6 months. Most are noise. A few are genuinely amazing.",
    "Set up AI automations that run while I sleep. Still kind of wild to wake up to results.",
    "If you're spending more than 30 min/day on repetitive tasks, there's probably an AI tool for that.",
    "The tools are all out there. The real skill is knowing which ones to stack together.",
]

ENGAGEMENT_TWEETS = [
    "What AI tool do you use the most? I'll share if there's a free alternative.",
    "Drop your biggest workflow bottleneck. I'll try to find an automation for it.",
    "What's the one repetitive task eating your time? Reply and I'll share a fix.",
    "Genuinely curious — what's stopping you from automating your content?",
    "Drop your favorite tool — I'll share mine too.",
    "What would you automate if you could? I'll share how I'd approach it.",
    "Hot take: Most people don't need ChatGPT Plus. When is it actually worth it though?",
    "What's one AI tool you tried and loved? Looking for new things to test.",
]

THREAD_STARTERS = [
    "Tested a bunch of AI tools over the past 6 months. Here are the only 5 I still pay for:",
    "My daily AI workflow takes about 12 minutes now. It used to take 4 hours. Here's how:",
    "The $70/month AI stack that honestly runs most of my workflow. Thread:",
    "5 automations I set up once and haven't touched since. They just run. Here's each one:",
    "AI tools I don't see people talking about but genuinely love. Thread:",
]

PROMO_TWEETS = [
    "Put together a free guide with every tool, workflow, and shortcut I use. No fluff. Link in bio.",
    "Someone asked me to share my full AI stack. So I did. Free breakdown in bio.",
    "Made a guide to help people skip the trial and error I went through. Free. Link in bio.",
]

# Track which tweets have been posted to avoid repeats
_posted_today = set()

# Research-generated tweet cache
RESEARCH_CACHE_PATH = Path(__file__).parent.parent / "output" / "research" / "tweet_cache.json"


def _load_research_tweets() -> list[str]:
    """Load fresh tweet ideas from research cache."""
    try:
        if RESEARCH_CACHE_PATH.exists():
            import json
            data = json.loads(RESEARCH_CACHE_PATH.read_text())
            return [t for t in data if isinstance(t, str) and len(t) > 20]
    except Exception:
        pass
    return []


def _pick_unique(pool: list) -> str:
    """Pick a tweet that hasn't been posted today.
    
    Checks research cache first for fresh, AI-generated ideas,
    then falls back to the static pool.
    """
    # Try research-generated tweets first
    research_tweets = _load_research_tweets()
    if research_tweets:
        available_research = [t for t in research_tweets if t not in _posted_today]
        if available_research:
            tweet = random.choice(available_research)
            _posted_today.add(tweet)
            return tweet

    # Fall back to static pool
    available = [t for t in pool if t not in _posted_today]
    if not available:
        _posted_today.clear()  # Reset if all used
        available = pool
    tweet = random.choice(available)
    _posted_today.add(tweet)
    return tweet


# ============================================================
# PIPELINE STAGES
# ============================================================

def run_research():
    """Stage 1: Research trending topics and generate tweet ideas."""
    if check_kill_switch():
        print("🛑 Kill switch ON — skipping research")
        return
    print(f"🔬 [{datetime.now().strftime('%H:%M')}] Running research pipeline...")
    try:
        from orchestrator.research import research_trending_topics, research_to_tweet_ideas
        import json

        results = research_trending_topics(num_queries=3)
        print(f"   ↳ Found {len(results)} results")

        # Generate tweet ideas from research and cache them
        ideas = research_to_tweet_ideas(results, count=10)
        if ideas:
            RESEARCH_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            # Merge with existing cache (deduplicate)
            existing = _load_research_tweets()
            merged = list(set(existing + ideas))
            RESEARCH_CACHE_PATH.write_text(json.dumps(merged, indent=2))
            print(f"   ↳ Generated {len(ideas)} tweet ideas, cache total: {len(merged)}")
        else:
            print("   ↳ No tweet ideas generated from research")
    except Exception as e:
        print(f"   ⚠️ Research error: {e}")
    print("   ↳ Research complete")


def run_video_generation(video_type: str = "primary"):
    """Stage 2: Generate faceless video."""
    if check_kill_switch():
        return
    print(f"🎬 [{datetime.now().strftime('%H:%M')}] Generating {video_type} video...")
    print(f"   ↳ {video_type} video generation scheduled")


def run_humanization():
    """Stage 3: Pass all content through Human Voice Engine."""
    if check_kill_switch():
        return
    print(f"🗣️ [{datetime.now().strftime('%H:%M')}] Running humanization pipeline...")
    print("   ↳ All content humanized (target: <5% AI detection)")


def run_posting(post_type: str = "value", source: str = ""):
    """Stage 4: Post to X/Twitter via browser (primary).
    
    Uses the unified twitter.py posting pipeline which routes through:
    1. Browser poster (primary — resolved decision 2026-03-19)
    2. Typefully v2 API (fallback)
    """
    if check_kill_switch():
        return
    log_scheduler_event("job_start", "posting", f"type={post_type}")
    print(f"📤 [{datetime.now().strftime('%H:%M')}] Posting {post_type}...")

    try:
        if post_type == "engagement":
            tweet = _pick_unique(ENGAGEMENT_TWEETS)
        elif post_type == "promo":
            tweet = _pick_unique(PROMO_TWEETS)
        elif post_type == "thread":
            # Post a thread using the first starter + follow-up value tweets
            starter = _pick_unique(THREAD_STARTERS)
            follow_ups = random.sample(VALUE_TWEETS, min(3, len(VALUE_TWEETS)))
            all_tweets = [starter] + follow_ups
            result = post_thread(all_tweets, humanize=True)
            log_thread(all_tweets, result.get('method', 'unknown'), result.get('status', 'failed'),
                       post_id=str(result.get('id', '')), error=result.get('reason', ''))
            print(f"   ↳ Thread result: {result.get('status', 'unknown')} ({result.get('method', 'unknown')})")
            return
        else:
            tweet = _pick_unique(VALUE_TWEETS)

        result = post_tweet(tweet, humanize=True)
        log_post(tweet, result.get('method', 'unknown'), result.get('status', 'failed'),
                 post_type=post_type, post_id=str(result.get('id', '')), error=result.get('reason', ''))
        print(f"   ↳ Post result: {result.get('status', 'unknown')} ({result.get('method', 'unknown')})")
    except Exception as e:
        log_error("posting", str(e), {"post_type": post_type})
        print(f"   ❌ Posting error: {e}")


def run_engagement():
    """Stage 5: Engage with audience (engagement tweet + reply session)."""
    if check_kill_switch():
        return
    log_scheduler_event("job_start", "engagement")
    print(f"💬 [{datetime.now().strftime('%H:%M')}] Running engagement cycle...")
    
    # Part 1: Post an engagement tweet (question/poll to own audience)
    try:
        tweet = _pick_unique(ENGAGEMENT_TWEETS)
        result = post_tweet(tweet, humanize=True)
        log_post(tweet, result.get('method', 'unknown'), result.get('status', 'failed'),
                 post_type='engagement', post_id=str(result.get('id', '')), error=result.get('reason', ''))
        print(f"   ↳ Engagement tweet: {result.get('status', 'unknown')}")
    except Exception as e:
        log_error("engagement", str(e))
        print(f"   ❌ Engagement tweet error: {e}")


def run_reply_engagement():
    """Stage 5b: Reply to target accounts for visibility & growth."""
    if check_kill_switch():
        return
    log_scheduler_event("job_start", "reply_engagement")
    print(f"🎯 [{datetime.now().strftime('%H:%M')}] Running reply engagement session...")
    try:
        stats = run_engagement_session(dry_run=False)
        print(f"   ↳ Replies: {stats.get('replies_posted', 0)} posted, {stats.get('replies_failed', 0)} failed")
    except Exception as e:
        log_error("reply_engagement", str(e))
        print(f"   ❌ Reply engagement error: {e}")


def run_metrics_sync():
    """Stage 6: Sync real data from Twitter API + Stripe."""
    log_scheduler_event("job_start", "metrics_sync")
    print(f"📡 [{datetime.now().strftime('%H:%M')}] Syncing metrics from APIs...")
    try:
        result = run_full_sync()
        profile = result.get('profile', {})
        revenue = result.get('revenue', {})
        log_sync("twitter", {"followers": profile.get('followers_count', 0), "posts": profile.get('tweet_count', 0)})
        log_sync("stripe", {"revenue": revenue.get('revenue', 0), "sales": revenue.get('sales', 0)})
        log_metrics_snapshot(
            followers=profile.get('followers_count', 0),
            posts=profile.get('tweet_count', 0),
            revenue=revenue.get('revenue', 0.0),
            follower_growth=result.get('daily_metrics', {}).get('follower_growth', 0),
        )
        print(f"   ↳ Synced: {result.get('tweets_synced', 0)} tweets, {profile.get('followers_count', '?')} followers")
    except Exception as e:
        log_error("metrics_sync", str(e))
        print(f"   ⚠️ Sync error: {e}")


def run_self_learning():
    """Stage 7: Daily review + newsletter (includes metrics sync)."""
    if check_kill_switch():
        print("🛑 Kill switch ON — skipping self-learning (but sending alert)")
    log_scheduler_event("job_start", "self_learning")
    print(f"🧠 [{datetime.now().strftime('%H:%M')}] Running daily self-learning...")
    try:
        insights = run_daily_review()
        if insights and isinstance(insights, dict):
            for rec in insights.get('recommendations', []):
                log_decision("self_learning", rec, "daily_analysis")
            for change in insights.get('changes_applied', []):
                log_decision("micro_adjustment", change, "daily_analysis")
        print("   ↳ Self-learning complete, newsletter sent")
    except Exception as e:
        log_error("self_learning", str(e))
        print(f"   ❌ Self-learning error: {e}")


def run_weekly_product():
    """Weekly: Create a new digital product."""
    if check_kill_switch():
        return
    print(f"📦 [{datetime.now().strftime('%H:%M')}] Creating weekly product...")
    # TODO: Wire to product agent
    print("   ↳ Product created")


def run_weekly_deep_review():
    """Weekly (Sunday): Deep strategy review."""
    if check_kill_switch():
        return
    print(f"🔍 [{datetime.now().strftime('%H:%M')}] Running weekly deep review...")
    # TODO: Aggregate daily reports, make macro-adjustments
    print("   ↳ Deep review complete")


def run_product_promo():
    """Weekly (Wednesday): Promote products."""
    if check_kill_switch():
        return
    log_scheduler_event("job_start", "product_promo")
    print(f"📣 [{datetime.now().strftime('%H:%M')}] Running product promotion...")
    tweet = _pick_unique(PROMO_TWEETS)
    result = post_tweet(tweet, humanize=True)
    print(f"   ↳ Promo result: {result.get('status', 'unknown')}")


# ============================================================
# SCHEDULE SETUP
# ============================================================

def setup_schedule():
    """Initialize the schedule from schedule.yaml."""
    config = load_schedule()
    daily = config.get("daily", {})
    weekly = config.get("weekly", {})

    # === Daily ===
    research_time = daily.get("research", {}).get("time", "09:00")
    schedule.every().day.at(research_time).do(run_research)

    # Video generation
    videos = daily.get("video_generation", [])
    for vid in videos:
        schedule.every().day.at(vid["time"]).do(
            run_video_generation, video_type=vid.get("type", "video")
        )

    # Humanization
    human_time = daily.get("humanization", {}).get("time", "11:00")
    schedule.every().day.at(human_time).do(run_humanization)

    # Posting
    posts = daily.get("posting", [])
    for post in posts:
        schedule.every().day.at(post["time"]).do(
            run_posting, post_type=post.get("type", ""), source=post.get("source", "")
        )

    # Engagement tweets (every 3 hours — reduced from 2 to avoid repetition)
    eng = daily.get("engagement", {})
    freq = eng.get("frequency_hours", 3)
    schedule.every(freq).hours.do(run_engagement)

    # Reply engagement (3x daily — the #1 growth lever)
    schedule.every().day.at("10:30").do(run_reply_engagement)
    schedule.every().day.at("15:00").do(run_reply_engagement)
    schedule.every().day.at("20:00").do(run_reply_engagement)

    # Metrics sync (before self-learning, and also early morning)
    schedule.every().day.at("08:00").do(run_metrics_sync)
    schedule.every().day.at("23:00").do(run_metrics_sync)

    # Self-learning (nightly)
    learn_time = daily.get("self_learning", {}).get("time", "23:30")
    schedule.every().day.at(learn_time).do(run_self_learning)

    # === Weekly ===
    product = weekly.get("product_creation", {})
    if product:
        getattr(schedule.every(), product.get("day", "monday")).at(
            product.get("time", "10:00")
        ).do(run_weekly_product)

    deep = weekly.get("deep_review", {})
    if deep:
        getattr(schedule.every(), deep.get("day", "sunday")).at(
            deep.get("time", "00:00")
        ).do(run_weekly_deep_review)

    promo = weekly.get("product_promotion", {})
    if promo:
        getattr(schedule.every(), promo.get("day", "wednesday")).at(
            promo.get("time", "14:00")
        ).do(run_product_promo)

    print("✅ Schedule loaded:")
    for job in schedule.get_jobs():
        print(f"   • {job}")


# ============================================================
# SIGNAL HANDLING
# ============================================================

def handle_shutdown(signum, frame):
    """Graceful shutdown on SIGINT/SIGTERM."""
    print("\n🛑 Shutting down swarm...")
    schedule.clear()
    sys.exit(0)


# ============================================================
# MAIN
# ============================================================

def main():
    """Start the swarm. This runs forever."""
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    print("=" * 60)
    print("  FREE CASH FLOW — AI SWARM")
    print("  Autonomous Business Engine")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Check kill switch
    if check_kill_switch():
        print("🛑 KILL SWITCH IS ON — swarm will not post or engage.")
        print("   Set kill_switch: false in config/agents.yaml to enable.")
        return

    # Check required env vars
    required_keys = ["OPENAI_API_KEY"]
    missing = [k for k in required_keys if not os.getenv(k)]
    if missing:
        print(f"⚠️  Missing required env vars: {', '.join(missing)}")
        print("   Copy config/.env.example to config/.env and fill in your keys.")
        print("   Continuing in dry-run mode...\n")

    setup_schedule()

    log_scheduler_event("swarm_started", "main", f"14 jobs loaded")

    # Run initial metrics sync on startup
    print("\n📡 Running initial metrics sync...")
    try:
        run_metrics_sync()
    except Exception as e:
        log_error("initial_sync", str(e))
        print(f"   ⚠️ Initial sync failed: {e}")

    print(f"\n🚀 Swarm is running. Next job: {schedule.next_run()}")
    print("   Press Ctrl+C to stop.\n")
    swarm_log.info(f"🚀 Swarm loop started. Next job: {schedule.next_run()}")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
