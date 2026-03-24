"""
Free Cash Flow — Reply Engagement Engine v2.0
The #1 growth strategy for accounts under 1K followers.

How it works:
1. Target list of large AI/automation accounts (curated, tiered)
2. Discover their recent tweets via web search (Twitter API search is paywalled)
3. Generate value-adding replies using GPT-4o-mini (context-aware, tone-varied)
4. Post replies via Browser (free tier allows tweet creation including replies)
5. Log everything for self-learning

Run: python3 -m orchestrator.reply_engine
"""

import json
import os
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

try:
    from orchestrator.swarm_logger import log_post, log_error, log_scheduler_event, logger
except ImportError:
    import logging
    logger = logging.getLogger("reply_engine")

# ============================================================
# TARGET ACCOUNTS — Tiered by audience size
# ============================================================

TARGET_ACCOUNTS = {
    "tier_1": {
        # 100K+ followers — reply for max visibility
        "accounts": [
            "alexhormozi",      # Business growth, 3M+
            "levaborozdina",    # AI/automation creator
            "therundownai",     # AI newsletter
            "bentaborsky",      # AI content
            "gregisenberg",     # Startup/AI
            "danshipper",       # AI business writer
            "maboroshi_ai",     # AI tools
            "mattshumer_",      # AI builder
        ],
        "replies_per_session": 3,
        "goal": "Get seen by their large audiences",
    },
    "tier_2": {
        # 10K-100K followers — build relationships
        "accounts": [
            "haborobotics",     # AI automation
            "nonmayank",        # AI solopreneur
            "theaisolopreneur", # AI business
            "aiaborobotics",    # AI tools
            "jaaboroschmid",    # No-code AI
            "nocodedevs",       # No-code community
            "buildspace",       # Builders
        ],
        "replies_per_session": 4,
        "goal": "Build mutual relationships, get reposts",
    },
    "tier_3": {
        # 1K-10K followers — community building
        "accounts": [
            "aibuilderclub",
            "indiehackers",
            "solopreneurship",
        ],
        "replies_per_session": 3,
        "goal": "Build loyal community members",
    },
}


# ============================================================
# LLM-POWERED REPLY GENERATION v2.0
# Context-aware replies using GPT-4o-mini with tone variety
# Falls back to templates if API fails
# ============================================================

# Reply tones — cycled through for variety
REPLY_TONES = {
    "casual": {
        "instruction": "Reply like a friend casually sharing what worked for them. Use lowercase, keep it short. Sound natural.",
        "example": "yeah I went through this exact thing. switched my whole stack in a weekend and honestly it was worth the effort",
    },
    "insightful": {
        "instruction": "Share a specific, non-obvious insight or real number from your experience. Keep it helpful and concise.",
        "example": "the part that surprised me — 80% of tools I tested were GPT wrappers. found 5 that are genuinely different",
    },
    "curious": {
        "instruction": "Ask a genuine question about their approach. Show you actually read their tweet. Be specific and friendly.",
        "example": "oh interesting — what are you using for the automation layer? I tried a few things before landing on n8n",
    },
    "helpful": {
        "instruction": "Offer a helpful tip or resource related to what they said. Be generous with info, not salesy.",
        "example": "if you haven't tried perplexity for that, it might save you a ton of time. sourced answers, no SEO spam",
    },
    "supportive": {
        "instruction": "Validate their point with your own experience. Share a quick result that backs up what they said. Be warm.",
        "example": "this hit. did something similar and honestly the difference was immediate. worth the time investment",
    },
}

# Brand persona context for all replies (Autostack HQ — friendly/helpful)
BRAND_PERSONA = """You are @AutoStackHQ — a friendly builder who shares AI automation discoveries.
Your vibe:
- You're the helpful friend who figured stuff out and wants to share
- You test AI tools obsessively and love talking about what works
- You've built a content engine, tested 47+ tools, use a $70/month stack
- You're genuine, not an authority. You say "I found" not "You need"
- You celebrate other people's wins and ask real questions
- You admit when things don't work

Voice rules:
- Use contractions always (don't, won't, can't — never "do not")
- No emojis. No hashtags.
- Never start with "Great point!" or "Absolutely!" or "Love this!"
- Never say "leverage", "comprehensive", "streamline", "game-changing"
- Sound like you're texting a friend, not writing a LinkedIn post
- Keep replies under 240 characters
- One idea per reply
- CRITICAL: Each reply must feel unique. Never repeat the same structure.
  Bad: "built something similar" (overused). Good: be specific about WHAT you built.
"""

# Fallback template system (used if LLM call fails)
FALLBACK_TEMPLATES = {
    "casual": [
        "yeah I've been testing this too. {experience}. honestly worth the time",
        "oh nice — I had a similar experience. {experience}",
        "same here, {experience}. took way less time than I expected",
        "can relate. {experience}. still kind of wild to me",
    ],
    "insightful": [
        "one thing I noticed — {data_point}",
        "real numbers on this from my side: {data_point}",
        "tested this myself actually. {data_point}",
        "{data_point}. surprised me when I first saw it",
    ],
    "curious": [
        "oh interesting — what are you using for {topic}? I tried a few different setups",
        "curious about your approach to {topic}. found something that works but always looking for better",
        "how are you handling {topic}? been experimenting with a few approaches",
    ],
    "helpful": [
        "if you haven't tried it, {data_point}. might save you some time",
        "fwiw {data_point}. helped me a lot when I was figuring this out",
        "one thing that helped me: {data_point}. worth a look",
    ],
    "supportive": [
        "this hit. {experience}. the difference was honestly immediate",
        "can confirm — {experience}. changed how I think about this stuff",
        "exactly this. {experience}. glad more people are talking about it",
    ],
}

EXPERIENCE_POOL = [
    "built a full content engine that runs while I sleep",
    "went from manual posting to fully scheduled in one afternoon",
    "cut my tool spend from $200 to $70/month with better output",
    "saved 2 hours/day on content creation alone",
    "automated research, writing, and posting in a single pipeline",
    "went from 4 hours of content work to 12 minutes",
    "replaced 3 paid tools with Claude alone",
    "set up 5 automated workflows in a weekend",
    "switched from Zapier to n8n and saved $50/month instantly",
    "got my whole engagement loop running on autopilot",
    "built the research pipeline in an afternoon with tavily + n8n",
    "went from zero automation to posting 3x/day in one weekend",
]

DATA_POOL = [
    "I tracked 47 AI tools over 6 months and only 5 were worth the subscription",
    "80% of AI tools I tried were just GPT wrappers with a fancy UI",
    "the average solopreneur wastes $200/month on tools they use once",
    "one automation saved me 14 hours/week — took 10 minutes to set up",
    "my $70/month AI stack does what a $500/month setup used to do",
    "ElevenLabs cut my video production time by 80%",
    "Perplexity Pro replaced Google for research entirely",
    "switching from Zapier to n8n saved $600/year with zero functionality loss",
    "claude handles 90% of my writing tasks better than chatgpt for half the price",
    "n8n's free tier does more than zapier's $50/month plan",
]

TOPIC_POOL = [
    "the automation layer", "content scheduling", "AI model selection",
    "the research pipeline", "video generation", "cost optimization",
    "scaling past the first 1K followers", "engagement automation",
    "the posting workflow", "lead gen with AI",
]

# Track which tone was used last to ensure variety
_tone_rotation = {"last_used": None, "history": []}


def _get_next_tone() -> str:
    """Rotate through tones to ensure variety. Never repeat the same tone twice in a row."""
    tones = list(REPLY_TONES.keys())
    last = _tone_rotation.get("last_used")
    history = _tone_rotation.get("history", [])

    # Avoid last used tone
    available = [t for t in tones if t != last]

    # Also avoid tones used in last 3 replies if possible
    if len(history) >= 3:
        recent = set(history[-3:])
        fresh = [t for t in available if t not in recent]
        if fresh:
            available = fresh

    tone = random.choice(available)
    _tone_rotation["last_used"] = tone
    _tone_rotation["history"] = (history + [tone])[-10:]
    return tone


def generate_reply_llm(tweet_text: str, username: str = "", tone: str = None) -> Optional[str]:
    """Generate a contextual reply using GPT-4o-mini.

    Args:
        tweet_text: The tweet being replied to
        username: The author of the tweet
        tone: Reply tone (casual, insightful, contrarian, curious, supportive)

    Returns:
        Generated reply text, or None if LLM call fails
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return None

    if not tone:
        tone = _get_next_tone()

    tone_config = REPLY_TONES.get(tone, REPLY_TONES["casual"])

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        prompt = f"""You are replying to this tweet from @{username or 'someone'}:

"{tweet_text}"

{tone_config['instruction']}

Example of this tone: "{tone_config['example']}"

RULES:
- Reply must be under 240 characters
- Must be relevant to what they actually said
- ONE idea only — don't try to cover everything
- No emojis. No hashtags.
- Never start with "Great point" or "Absolutely" or "I agree"
- Use lowercase. Contractions always.
- Sound human. Like you're texting a friend who builds stuff.
- Don't be generic. Reference something specific from their tweet.
- NEVER use the words: leverage, comprehensive, streamline, innovative, revolutionary

Reply (under 240 chars):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": BRAND_PERSONA},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.9,  # High temp for variety
            presence_penalty=0.6,  # Discourage repetition
            frequency_penalty=0.4,
        )

        reply = response.choices[0].message.content.strip()

        # Strip quotes if the model wrapped it
        reply = reply.strip('"').strip("'").strip('\u201c').strip('\u201d')

        # Enforce character limit
        if len(reply) > 275:
            # Try to truncate at last sentence
            last_period = reply[:270].rfind('.')
            if last_period > 100:
                reply = reply[:last_period + 1]
            else:
                reply = reply[:272] + "..."

        # Run through humanizer to strip any remaining AI fingerprints
        try:
            from orchestrator.humanize import humanize_content
            reply = humanize_content(reply, content_type="reply", aggressiveness=0.6)
        except ImportError:
            pass

        logger.info(f"LLM reply generated (tone={tone}): {reply[:60]}...")
        return reply

    except Exception as e:
        logger.warning(f"LLM reply generation failed: {e}")
        return None


def generate_reply_template(tweet_text: str, tone: str = None) -> str:
    """Fallback: Generate a reply using enhanced templates.

    Used when LLM call fails or API key is missing.
    """
    if not tone:
        tone = _get_next_tone()

    templates = FALLBACK_TEMPLATES.get(tone, FALLBACK_TEMPLATES["casual"])
    template = random.choice(templates)

    # Fill in template variables
    reply = template.format(
        experience=random.choice(EXPERIENCE_POOL),
        data_point=random.choice(DATA_POOL),
        caveat=random.choice(DATA_POOL).lower(),
        topic=random.choice(TOPIC_POOL),
    )

    # Ensure under 280 chars
    if len(reply) > 275:
        reply = reply[:272] + "..."

    return reply


def generate_reply(tweet_text: str, style: str = None) -> str:
    """Generate a contextual, value-adding reply.

    Priority: LLM (context-aware) > Templates (fallback)
    The tone auto-rotates for variety.
    """
    tone = style or _get_next_tone()

    # Try LLM first (context-aware, unique)
    llm_reply = generate_reply_llm(tweet_text, tone=tone)
    if llm_reply:
        return llm_reply

    # Fallback to enhanced templates
    logger.info("Falling back to template-based reply generation")
    return generate_reply_template(tweet_text, tone=tone)


# ============================================================
# TWEET DISCOVERY (via web search since Twitter API is paywalled)
# ============================================================

def find_recent_tweets(username: str, count: int = 5) -> list[dict]:
    """Find recent tweets from a user via Tavily Search.
    
    Brave Search doesn't index x.com well. Tavily works.
    Returns list of {text, url, tweet_id} dicts.
    """
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_key:
        logger.warning(f"No TAVILY_API_KEY — can't discover tweets for @{username}")
        return []
    
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_key,
                "query": f"{username} latest tweet",
                "search_depth": "basic",
                "include_domains": ["x.com", "twitter.com"],
                "max_results": count + 2,  # Extra buffer for non-tweet results
            },
            timeout=15,
        )
        
        if resp.status_code != 200:
            logger.warning(f"Tavily search failed for @{username}: {resp.status_code}")
            return []
        
        data = resp.json()
        tweets = []
        
        for result in data.get("results", []):
            url = result.get("url", "")
            # Extract tweet ID from URL like https://x.com/username/status/1234567890
            match = re.search(r'/status/(\d+)', url)
            if match:
                tweet_id = match.group(1)
                content = result.get("content", result.get("title", ""))
                title = result.get("title", "")
                # Use the longer text as tweet content
                text = content if len(content) > len(title) else title
                
                # Extract the actual username from URL
                user_match = re.search(r'x\.com/(\w+)/status', url)
                actual_username = user_match.group(1) if user_match else username
                
                tweets.append({
                    "tweet_id": tweet_id,
                    "text": text,
                    "url": url,
                    "username": actual_username,
                })
        
        return tweets[:count]
    
    except Exception as e:
        logger.error(f"Tweet discovery failed for @{username}: {e}")
        return []


def find_tweets_by_topic(topic: str, count: int = 5) -> list[dict]:
    """Find recent tweets about a topic via Tavily Search."""
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_key:
        return []
    
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": tavily_key,
                "query": f"{topic} tweet discussion",
                "search_depth": "basic",
                "include_domains": ["x.com", "twitter.com"],
                "max_results": count + 2,
            },
            timeout=15,
        )
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        tweets = []
        for result in data.get("results", []):
            url = result.get("url", "")
            match = re.search(r'/status/(\d+)', url)
            if match and "/status/" in url:
                username_match = re.search(r'x\.com/(\w+)/status', url)
                tweets.append({
                    "tweet_id": match.group(1),
                    "text": result.get("content", result.get("title", "")),
                    "url": url,
                    "username": username_match.group(1) if username_match else "unknown",
                })
        
        return tweets[:count]
    
    except Exception as e:
        logger.error(f"Topic tweet search failed for '{topic}': {e}")
        return []


# ============================================================
# REPLY POSTING
# ============================================================

def post_reply(tweet_id: str, reply_text: str, username: str = "", tweet_url: str = "") -> dict:
    """Post a reply to a specific tweet.
    
    Priority: Browser reply > Twitter API
    Browser is primary because Twitter API returns 402 (paywalled).
    """
    # Build tweet URL if not provided
    if not tweet_url:
        tweet_url = f"https://x.com/{username}/status/{tweet_id}"
    
    # Method 1: Browser-based reply (primary — bypasses API paywall)
    try:
        from orchestrator.browser_poster import browser_reply_to_tweet
        result = browser_reply_to_tweet(tweet_url, reply_text)
        if result.get("status") == "posted":
            log_post(
                reply_text, "browser_reply", "posted",
                post_type="reply",
                post_id=str(tweet_id),
            )
            logger.info(f"REPLY to @{username} (tweet {tweet_id}): {reply_text[:60]}...")
            result["in_reply_to"] = tweet_id
            result["username"] = username
            return result
        else:
            logger.warning(f"Browser reply failed: {result.get('reason', 'unknown')}")
    except Exception as e:
        logger.warning(f"Browser reply error: {e}")
    
    # Method 2: Twitter API (fallback — may be paywalled)
    try:
        import tweepy
        
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        )
        
        response = client.create_tweet(
            text=reply_text,
            in_reply_to_tweet_id=tweet_id,
            user_auth=True,
        )
        
        if response and response.data:
            reply_id = response.data.get("id", "")
            log_post(
                reply_text, "twitter_api_reply", "posted",
                post_type="reply",
                post_id=str(reply_id),
            )
            logger.info(f"REPLY to @{username} (tweet {tweet_id}): {reply_text[:60]}...")
            return {
                "status": "posted",
                "reply_id": reply_id,
                "in_reply_to": tweet_id,
                "username": username,
                "text": reply_text,
                "method": "twitter_api",
            }
    except Exception as e:
        logger.warning(f"Twitter API reply failed: {e}")
    
    error_msg = "All reply methods failed"
    log_error("reply_engine", error_msg, {"tweet_id": tweet_id, "username": username})
    return {"status": "failed", "error": error_msg}


# ============================================================
# ENGAGEMENT SESSION
# ============================================================

def run_engagement_session(dry_run: bool = False) -> dict:
    """Run a full engagement session.
    
    1. Pick target accounts from each tier
    2. Find their recent tweets
    3. Generate contextual replies (LLM-powered with tone variety)
    4. Post replies
    5. Return stats
    """
    log_scheduler_event("job_start", "reply_engagement")
    print(f"\n{'='*50}")
    print(f"REPLY ENGAGEMENT SESSION v2.0 — {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    stats = {
        "started": datetime.now().isoformat(),
        "replies_attempted": 0,
        "replies_posted": 0,
        "replies_failed": 0,
        "accounts_engaged": [],
        "tones_used": [],
        "errors": [],
    }
    
    # Track what we've replied to today to avoid doubles
    replied_today_file = Path(__file__).parent.parent / "data" / f"replied_{datetime.now().strftime('%Y-%m-%d')}.json"
    replied_today_file.parent.mkdir(parents=True, exist_ok=True)
    
    if replied_today_file.exists():
        with open(replied_today_file) as f:
            replied_ids = set(json.load(f))
    else:
        replied_ids = set()
    
    for tier_name, tier_config in TARGET_ACCOUNTS.items():
        accounts = tier_config["accounts"]
        max_replies = tier_config["replies_per_session"]
        
        # Pick random subset of accounts for this session
        session_accounts = random.sample(accounts, min(len(accounts), max_replies))
        
        print(f"\n  {tier_name.upper()} — targeting {len(session_accounts)} accounts")
        
        for username in session_accounts:
            print(f"    Searching for @{username}'s recent tweets...")
            
            tweets = find_recent_tweets(username, count=3)
            
            if not tweets:
                print(f"       No tweets found for @{username}")
                continue
            
            # Find a tweet we haven't replied to yet
            target_tweet = None
            for tweet in tweets:
                if tweet["tweet_id"] not in replied_ids:
                    target_tweet = tweet
                    break
            
            if not target_tweet:
                print(f"       Already replied to all found tweets from @{username}")
                continue
            
            # Generate a reply with tone rotation
            current_tone = _get_next_tone()
            reply_text = generate_reply(target_tweet["text"], style=current_tone)
            stats["replies_attempted"] += 1
            stats["tones_used"].append(current_tone)
            
            print(f"       Tweet: {target_tweet['text'][:60]}...")
            print(f"       Reply ({current_tone}): {reply_text[:60]}...")
            
            if dry_run:
                print(f"       DRY RUN — would reply to {target_tweet['url']}")
                stats["replies_posted"] += 1
                stats["accounts_engaged"].append(username)
                replied_ids.add(target_tweet["tweet_id"])
                continue
            
            # Post the reply
            result = post_reply(
                tweet_id=target_tweet["tweet_id"],
                reply_text=reply_text,
                username=target_tweet.get("username", username),
                tweet_url=target_tweet.get("url", ""),
            )
            
            if result["status"] == "posted":
                stats["replies_posted"] += 1
                stats["accounts_engaged"].append(username)
                replied_ids.add(target_tweet["tweet_id"])
                print(f"       Reply posted!")
            else:
                stats["replies_failed"] += 1
                stats["errors"].append(f"@{username}: {result.get('error', 'unknown')}")
                print(f"       Failed: {result.get('error', 'unknown')}")
            
            # Rate limiting — space out replies
            time.sleep(random.uniform(30, 90))
    
    # Save replied IDs
    with open(replied_today_file, "w") as f:
        json.dump(list(replied_ids), f)
    
    stats["finished"] = datetime.now().isoformat()
    
    # Save session stats
    stats_file = Path(__file__).parent.parent / "logs" / "engagement" / f"session_{datetime.now().strftime('%Y-%m-%d_%H%M')}.json"
    stats_file.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n{'---'*17}")
    print(f"SESSION COMPLETE")
    print(f"   Replies posted: {stats['replies_posted']}/{stats['replies_attempted']}")
    print(f"   Tones used: {', '.join(stats['tones_used']) or 'none'}")
    print(f"   Accounts engaged: {', '.join(stats['accounts_engaged']) or 'none'}")
    if stats["errors"]:
        print(f"   Errors: {len(stats['errors'])}")
    print(f"{'---'*17}\n")
    
    return stats


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN MODE — no actual replies will be posted\n")
    result = run_engagement_session(dry_run=dry_run)
    print(json.dumps(result, indent=2))
