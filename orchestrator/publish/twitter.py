"""
Free Cash Flow — Twitter/X Posting Agent
Posts tweets and threads via browser automation (primary).
Falls back to Typefully API if browser unavailable.
All content passes through the Human Voice Engine before posting.

Resolved Decision (2026-03-19): Browser posting is primary.
Typefully was never used for actual posting. Twitter API is read-only.
"""

import os
import json
from pathlib import Path
from orchestrator import PROJECT_ROOT
from typing import Optional

import requests
try:
    import tweepy
except ImportError:
    tweepy = None  # Tweepy is optional — only used for read-only API calls
from dotenv import load_dotenv

from orchestrator.pipeline.humanize import publish

# Load env
ENV_PATH = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

TYPEFULLY_API_KEY = os.getenv("TYPEFULLY_API_KEY", "")
POSTING_METHOD = os.getenv("POSTING_METHOD", "browser")  # browser, typefully, api


# ============================================================
# TYPEFULLY (Primary — free, reliable, scheduled)
# ============================================================

def _typefully_post(text: str, schedule: bool = False, thread_tweets: list = None) -> dict:
    """Post via Typefully API v2.
    
    Previous v1 code had wrong auth header format (X-API-KEY: Bearer key).
    v2 uses standard Authorization: Bearer header.
    """
    if not TYPEFULLY_API_KEY:
        return {"error": "No TYPEFULLY_API_KEY"}

    # First, get the social set ID (cached after first call)
    if not hasattr(_typefully_post, "_social_set_id"):
        try:
            sets_resp = requests.get(
                "https://api.typefully.com/v2/social-sets",
                headers={"Authorization": f"Bearer {TYPEFULLY_API_KEY}"},
            )
            if sets_resp.status_code == 200:
                results = sets_resp.json().get("results", [])
                if results:
                    _typefully_post._social_set_id = results[0]["id"]
                else:
                    return {"error": "No Typefully social sets found"}
            else:
                return {"error": f"Typefully sets {sets_resp.status_code}: {sets_resp.text}"}
        except Exception as e:
            return {"error": f"Typefully connection failed: {e}"}

    social_set_id = _typefully_post._social_set_id

    # Build v2 draft payload
    if thread_tweets:
        posts = [{"text": t} for t in thread_tweets]
    else:
        posts = [{"text": text}]

    payload = {
        "platforms": {
            "x": {
                "enabled": True,
                "posts": posts,
            }
        },
    }

    # Set scheduling
    if schedule:
        payload["publish_at"] = "next-free-slot"
    else:
        payload["publish_at"] = "now"

    resp = requests.post(
        f"https://api.typefully.com/v2/social-sets/{social_set_id}/drafts",
        headers={
            "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        return {
            "status": "posted" if not schedule else "scheduled",
            "id": data.get("id", ""),
            "text": text[:280] if not thread_tweets else thread_tweets[0][:280],
            "method": "typefully_v2",
        }
    else:
        return {"error": f"Typefully v2 {resp.status_code}: {resp.text}"}


# ============================================================
# TWITTER API (Read-only — for metrics, no posting fees)
# ============================================================

def _get_client():
    """Get an authenticated Tweepy v2 client (read-only use)."""
    if tweepy is None:
        raise ImportError("tweepy is not installed — run: pip install tweepy")
    return tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
    )


def get_me() -> dict:
    """Get authenticated user info (free API call)."""
    client = _get_client()
    me = client.get_me(user_auth=True, user_fields=["public_metrics"])
    if me and me.data:
        metrics = me.data.get("public_metrics", {}) if hasattr(me.data, "get") else {}
        return {
            "id": me.data.id,
            "username": me.data.username,
            "name": me.data.name,
            "followers": metrics.get("followers_count", 0),
        }
    return {}


def get_my_tweets(count: int = 10) -> list[dict]:
    """Get recent tweets (free read API)."""
    client = _get_client()
    me = client.get_me(user_auth=True)
    if not me or not me.data:
        return []

    tweets = client.get_users_tweets(
        me.data.id,
        max_results=min(count, 100),
        tweet_fields=["public_metrics", "created_at"],
        user_auth=True,
    )

    if not tweets or not tweets.data:
        return []

    return [
        {
            "id": t.id,
            "text": t.text,
            "created_at": str(t.created_at) if hasattr(t, "created_at") else "",
            "metrics": t.public_metrics if hasattr(t, "public_metrics") else {},
        }
        for t in tweets.data
    ]


# ============================================================
# UNIFIED POSTING INTERFACE
# ============================================================

def post_tweet(text: str, humanize: bool = True, dry_run: bool = False, schedule: bool = False) -> dict:
    """Post a single tweet.

    Posting priority: Browser > Typefully > API
    (Browser is primary per resolved decision 2026-03-19)
    """
    # Humanize content
    if humanize:
        content = publish(text, content_type="tweet")
        if content is None:
            return {"status": "failed", "reason": "Failed humanization (<5% AI)"}
    else:
        content = text

    # Truncate
    if len(content) > 280:
        content = content[:277] + "..."

    if dry_run:
        return {"status": "dry_run", "text": content, "length": len(content)}

    # Try browser posting first (primary method)
    try:
        from orchestrator.publish.browser_poster import browser_post_tweet
        result = browser_post_tweet(content)
        if result.get("status") == "posted":
            print(f"✅ Tweet posted via browser: {content[:60]}...")
            return result
        print(f"⚠️ Browser posting returned: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"⚠️ Browser posting failed: {e}")

    # Fallback: Typefully
    if TYPEFULLY_API_KEY:
        result = _typefully_post(content, schedule=schedule)
        if "error" not in result:
            print(f"✅ Tweet posted via Typefully: {content[:60]}...")
            result["text"] = content
            result["length"] = len(content)
            return result
        print(f"⚠️ Typefully error: {result['error']}")

    return {"status": "failed", "reason": "No posting method available"}


def post_thread(tweets: list[str], humanize: bool = True, dry_run: bool = False, schedule: bool = False) -> dict:
    """Post a thread (multiple connected tweets)."""
    # Humanize each tweet
    processed = []
    for raw_text in tweets:
        if humanize:
            content = publish(raw_text, content_type="thread")
            if content is None:
                continue
        else:
            content = raw_text

        if len(content) > 280:
            content = content[:277] + "..."
        processed.append(content)

    if not processed:
        return {"status": "failed", "reason": "No tweets passed humanization"}

    if dry_run:
        return {
            "status": "dry_run",
            "total": len(processed),
            "tweets": [{"text": t, "length": len(t)} for t in processed],
        }

    # Try browser posting first (primary method — posts individually)
    try:
        from orchestrator.publish.browser_poster import browser_post_tweet
        import time
        results = []
        for t in processed:
            r = browser_post_tweet(t)
            results.append(r)
            time.sleep(5)  # Space out posts
        posted = [r for r in results if r.get("status") == "posted"]
        if posted:
            print(f"✅ Thread posted via browser ({len(posted)}/{len(processed)} tweets)")
            return {"status": "posted", "total": len(posted), "method": "browser", "tweets": results}
    except Exception as e:
        print(f"⚠️ Browser thread posting failed: {e}")

    # Fallback: Typefully (supports threads natively)
    if TYPEFULLY_API_KEY:
        result = _typefully_post(processed[0], schedule=schedule, thread_tweets=processed)
        if "error" not in result:
            print(f"✅ Thread posted via Typefully ({len(processed)} tweets)")
            return {"status": "posted", "total": len(processed), "method": "typefully", "tweets": processed}

    return {"status": "failed", "reason": "No posting method available"}
