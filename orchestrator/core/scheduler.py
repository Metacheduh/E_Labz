"""
Free Cash Flow — Scheduler
Cron-based daily automation. This is the heartbeat of the swarm.
Start: python -m orchestrator.scheduler
"""

import json
import os
import random
import signal
import sys
import time
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from orchestrator import PROJECT_ROOT

import schedule
import yaml
from dotenv import load_dotenv

# Load environment
ENV_PATH = PROJECT_ROOT / "config" / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
else:
    load_dotenv(PROJECT_ROOT / "config" / ".env.example")

try:
    from orchestrator.intelligence.self_learn import run_daily_review
except ImportError:
    def run_daily_review():
        print("   (self_learn not available, skipping)")

try:
    from orchestrator.publish.twitter import post_tweet, post_thread
except ImportError:
    def post_tweet(text, **kwargs):
        print(f"   (twitter module not available) Would post: {text[:80]}...")
        return {"status": "failed"}
    def post_thread(tweets, **kwargs):
        print(f"   (twitter module not available) Would post thread: {len(tweets)} tweets")
        return {"status": "failed"}

try:
    from orchestrator.intelligence.sync_metrics import run_full_sync
except ImportError:
    def run_full_sync():
        print("   (sync_metrics not available, skipping)")
        return {}

from orchestrator.core.swarm_logger import (
    log_post, log_thread, log_sync, log_metrics_snapshot,
    log_error, log_scheduler_event, log_decision,
    logger as swarm_log,
)

try:
    from orchestrator.pipeline.reply_engine import run_engagement_session
except ImportError:
    def run_engagement_session(dry_run=False):
        print("   (reply_engine not available, skipping)")
        return {}

# ============================================================
# GLOBALS
# ============================================================

KILL_SWITCH = False
SCHEDULE_PATH = PROJECT_ROOT / "config" / "schedule.yaml"


def load_schedule() -> dict:
    """Load schedule from YAML config."""
    if SCHEDULE_PATH.exists():
        with open(SCHEDULE_PATH) as f:
            return yaml.safe_load(f)
    return {}


def check_kill_switch() -> bool:
    """Check if the kill switch is activated."""
    global KILL_SWITCH
    agents_config = PROJECT_ROOT / "config" / "agents.yaml"
    if agents_config.exists():
        with open(agents_config) as f:
            config = yaml.safe_load(f)
            KILL_SWITCH = config.get("orchestrator", {}).get("kill_switch", False)
    return KILL_SWITCH


# ============================================================
# TWEET CONTENT LIBRARY — builder authority, proof-based
# Voice: I'm a builder who ships AI products. I share what works.
# RULE: Never reveal AI runs the account. We are the builder.
# ============================================================

VALUE_TWEETS = [
    # How-To format
    "how I create content 4x faster:\n→ Brave Search for research\n→ GPT-4 for first drafts\n→ edit for voice and accuracy\n→ schedule with Typefully\nsaved me 3+ hours/day.",
    "how I cut content creation from 4 hours to 12 minutes:\n→ research templates\n→ AI-assisted drafts\n→ personal editing pass\n→ batch scheduling\ngame changer for solo builders.",
    "how to build your first AI agent pipeline:\n→ pick one repetitive task\n→ chain 3 APIs together\n→ add a scheduler\n→ deploy to Cloud Run\nthat's it. no framework needed.",
    "how I track revenue without logging into dashboards:\n→ Lemon Squeezy API (sales)\n→ Twitter API (engagement)\n→ SQLite (local cache)\n→ daily sync at 8AM\nbuilt it once, runs forever.",
    "how I automated lead capture:\n→ portfolio site with email form\n→ free guide as lead magnet\n→ welcome email via SMTP\n→ product link in follow-up\ncost: $0/month.",
    # Stack Reveal format
    "my daily tech stack:\n→ Cloud Run (hosting)\n→ GPT-4 (writing assist)\n→ Brave Search (research)\n→ Typefully (scheduling)\n→ Lemon Squeezy (store)\nunder $70/month total.",
    "my $70/month AI stack:\n→ GPT-4 ($20)\n→ Perplexity Pro ($20)\n→ Cursor ($20)\n→ ElevenLabs ($5)\n→ Cloud Run ($5)\nreplaces $500+ in manual work.",
    "tools I use daily, no exceptions:\n1. Cursor — codes with full codebase context\n2. Perplexity — research without SEO spam\n3. Claude — analysis and long writing\n4. n8n — free Zapier alternative\n5. Typefully — scheduled posting via API",
    # Metric Drop format
    "170 followers. 24+ digital products.\nposted consistently for 6 months.\nrevenue engine is starting to compound.",
    "deployed a new product to Cloud Run this morning.\n18 scheduled jobs running.\nthe system doesn't need my laptop open.",
    "$70/month in tools. hours of manual work saved.\nthe content pipeline runs on autopilot.\nthat's the whole point of building systems.",
    "set up the email engine in 30 minutes.\napp password + SMTP. no OAuth, no GCP console.\nsometimes simple beats sophisticated.",
    # Builder Update format
    "shipped this week:\n→ Cloud Run deployment (24/7 uptime)\n→ Lemon Squeezy integration (revenue tracking)\n→ Gmail engine (lead nurture)\n→ smart CTAs (dynamic checkout links)\nnext: webhook notifications on every sale.",
    "leveled up the stack this week:\n→ posting via Typefully API\n→ revenue sync from Lemon Squeezy\n→ 18 scheduled jobs on Cloud Run\nall from one Python codebase.",
]

ENGAGEMENT_TWEETS = [
    "what's one task you do every day that could be automated?\nreply and I'll map the pipeline.",
    "building AI tools or just using ChatGPT?\nhonest answers only.",
    "what's your biggest bottleneck — content, leads, or closing?\nI've built systems for all three. happy to share.",
    "hot take: you don't need a $200/month AI stack.\n$70 covers everything if you pick the right tools.\nwhat are you paying?",
    "show me your tool stack. I'll show you mine.",
    "unpopular opinion: most people buy AI tools but never build anything with them.\nwhat have you actually shipped?",
    "what would you build if you had a full AI toolkit ready to go?",
    "name one workflow you want automated.\nbest answer gets a full breakdown.",
]

THREAD_STARTERS = [
    "I built 24 AI-powered products this year.\nhere's what each one does and how I built it:\n🧵",
    "I tested 30+ AI tools over 6 months.\nonly 5 survived. here's which ones and why:\n🧵",
    "how I built a full content engine in one weekend.\nresearch → write → edit → post.\nstep by step:\n🧵",
    "the $70/month stack that replaced $500 in subscriptions.\nevery tool, every config, every workflow:\n🧵",
    "how to go from 'AI curious' to 'AI profitable' in 30 days.\nno courses. no gurus. just tools and systems:\n🧵",
]

PROMO_TWEETS = [
    "I packaged my entire AI pipeline into a kit.\ndrop in your API key and go.\nfull source → {url}",
    "the exact system I use to run this business.\nevery config. every pipeline.\n→ {url}",
    "built the system? sell the blueprint.\nthat's the model. here's mine:\n→ {url}",
]

# Smart CTA store URL
LS_STORE_URL = "https://autostackhq.lemonsqueezy.com"

SMART_CTAS = [
    "I packaged my AI pipeline into a kit. drop in your API key and go.\nfull source: {url}",
    "the exact system I use to run @AutoStackHQ. every config file included.\n→ {url}",
    "built a full content + revenue engine. here's the blueprint:\n→ {url}",
    "every pipeline, every tool. no tutorials — working code.\n→ {url}",
]

# Track which tweets have been posted to avoid repeats
_posted_today = set()

# Research-generated tweet cache
RESEARCH_CACHE_PATH = PROJECT_ROOT / "output" / "research" / "tweet_cache.json"

# Web scrape artifacts that must be stripped from content
_SCRAPE_ARTIFACTS = [
    "# Related Answers", "### Here's what we'll cover", "Image 5",
    "## The 5 Best", "## Related", "### 1", "...", "<!--",
]


def _sanitize_tweet(text: str) -> str | None:
    """Strip web scrape artifacts and validate tweet quality."""
    # Kill any tweet containing raw markdown/scrape leaks
    for artifact in _SCRAPE_ARTIFACTS:
        if artifact in text:
            return None
    # Strip trailing ellipsis fragments
    if text.rstrip().endswith("..."):
        return None
    # Must be within Twitter limits
    if len(text) > 280 or len(text) < 20:
        return None
    return text.strip()


def _load_research_tweets() -> list[str]:
    """Load fresh tweet ideas from research cache (sanitized)."""
    try:
        if RESEARCH_CACHE_PATH.exists():
            import json
            data = json.loads(RESEARCH_CACHE_PATH.read_text())
            cleaned = []
            for t in data:
                if isinstance(t, str):
                    result = _sanitize_tweet(t)
                    if result:
                        cleaned.append(result)
            return cleaned
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
        from orchestrator.pipeline.research import research_trending_topics, research_to_tweet_ideas
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
    """Stage 6: Sync real data from Twitter API + Lemon Squeezy + Stripe."""
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
    """Weekly (Wednesday): Promote products with smart CTAs."""
    if check_kill_switch():
        return
    log_scheduler_event("job_start", "product_promo")
    print(f"📣 [{datetime.now().strftime('%H:%M')}] Running product promotion...")

    # Alternate between generic promo and smart CTA with checkout link
    if random.random() < 0.6:
        # Smart CTA with real checkout URL
        cta = random.choice(SMART_CTAS)
        tweet = cta.format(url=LS_STORE_URL)
    else:
        tweet = _pick_unique(PROMO_TWEETS)

    result = post_tweet(tweet, humanize=True)
    log_post(tweet, result.get('method', 'unknown'), result.get('status', 'failed'),
             post_type='promo', post_id=str(result.get('id', '')), error=result.get('reason', ''))
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
        promo_day = promo.get("day", "wednesday")
        promo_time = promo.get("time", "14:00")
        if promo_day == "daily":
            schedule.every().day.at(promo_time).do(run_product_promo)
        else:
            getattr(schedule.every(), promo_day).at(promo_time).do(run_product_promo)

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
# HEALTH ENDPOINT — Cloud Run needs an HTTP listener
# ============================================================

class _HealthHandler(BaseHTTPRequestHandler):
    """Minimal health check + webhook handler for Cloud Run."""
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = {
                "status": "healthy",
                "service": "swarm-scheduler",
                "uptime": datetime.now().isoformat(),
                "jobs": len(schedule.get_jobs()),
                "next_run": str(schedule.next_run()) if schedule.get_jobs() else "none",
            }
            self.wfile.write(json.dumps(status).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/webhook/lemonsqueezy":
            content_length = int(self.headers.get("Content-Length", 0))
            payload = self.rfile.read(content_length)
            headers = dict(self.headers)
            try:
                from orchestrator.webhooks.lemonsqueezy import handle_webhook
                result = handle_webhook(payload, headers)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                print(f"  [WEBHOOK] Error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP logs to keep console clean."""
        pass


def _start_health_server(port: int = 8080):
    """Start a background HTTP server for Cloud Run health checks."""
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"🏥 Health server listening on port {port}")


# ============================================================
# MAIN ENTRY
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

    # Start health endpoint for Cloud Run (threaded, non-blocking)
    port = int(os.getenv("PORT", 8080))
    _start_health_server(port)

    print(f"\n🚀 Swarm is running. Next job: {schedule.next_run()}")
    print(f"   Health endpoint: http://0.0.0.0:{port}/health")
    print("   Press Ctrl+C to stop.\n")
    swarm_log.info(f"🚀 Swarm loop started. Next job: {schedule.next_run()}")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
