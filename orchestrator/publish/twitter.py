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
from datetime import datetime
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
    
    v2 flow (December 2025+):
    1. POST /v2/social-sets/{id}/drafts  → creates draft
    2. PATCH /v2/social-sets/{id}/drafts/{draft_id}  → set publish_at to schedule
    
    Auth: Authorization: Bearer KEY
    Social Set: 289361 (@JEH005432 / AutoStackHQ)
    """
    if not TYPEFULLY_API_KEY:
        return {"error": "No TYPEFULLY_API_KEY"}

    SOCIAL_SET_ID = os.getenv("TYPEFULLY_SOCIAL_SET_ID", "289361")
    BASE = f"https://api.typefully.com/v2/social-sets/{SOCIAL_SET_ID}"
    HEADERS = {
        "Authorization": f"Bearer {TYPEFULLY_API_KEY}",
        "Content-Type": "application/json",
    }

    # Build v2 draft payload (no publish_at here — v2 rejects it in create)
    if thread_tweets:
        posts = [{"text": t} for t in thread_tweets]
    else:
        posts = [{"text": text}]

    create_payload = {
        "platforms": {
            "x": {
                "enabled": True,
                "posts": posts,
            }
        },
    }

    # Step 1: Create the draft
    try:
        resp = requests.post(
            f"{BASE}/drafts",
            headers=HEADERS,
            json=create_payload,
        )
    except Exception as e:
        return {"error": f"Typefully connection failed: {e}"}

    if resp.status_code not in (200, 201):
        return {"error": f"Typefully create {resp.status_code}: {resp.text}"}

    data = resp.json()
    draft_id = data.get("id")
    if not draft_id:
        return {"error": "Typefully returned no draft ID"}

    # Step 2: Schedule/publish via PATCH with publish_at
    from datetime import timezone, timedelta
    now_utc = datetime.now(timezone.utc)

    if schedule:
        # Schedule for next hour
        publish_time = now_utc + timedelta(hours=1)
    else:
        # Publish ASAP — 90 seconds from now (API rejects past timestamps)
        publish_time = now_utc + timedelta(seconds=90)

    publish_at = publish_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    try:
        patch_resp = requests.patch(
            f"{BASE}/drafts/{draft_id}",
            headers=HEADERS,
            json={"publish_at": publish_at},
        )
        if patch_resp.status_code in (200, 201):
            patch_data = patch_resp.json()
            status = patch_data.get("status", "scheduled")
        else:
            # Draft was created but scheduling failed — still a partial success
            status = "draft_only"
            print(f"⚠️ Draft created (ID: {draft_id}) but scheduling failed: {patch_resp.text}")
    except Exception as e:
        status = "draft_only"
        print(f"⚠️ Draft created (ID: {draft_id}) but scheduling failed: {e}")

    return {
        "status": status,
        "id": draft_id,
        "text": text[:280] if not thread_tweets else thread_tweets[0][:280],
        "method": "typefully_v2",
        "publish_at": publish_at,
        "private_url": data.get("private_url", ""),
    }


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

    Posting priority: Typefully v2 > Browser > API
    (Typefully is primary — reliable scheduled publishing via API)
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

    # Try Typefully first (primary method)
    if TYPEFULLY_API_KEY:
        result = _typefully_post(content, schedule=schedule)
        if "error" not in result:
            print(f"✅ Tweet posted via Typefully: {content[:60]}...")
            result["text"] = content
            result["length"] = len(content)
            return result
        print(f"⚠️ Typefully error: {result['error']}")

    # Fallback: Browser posting
    try:
        from orchestrator.publish.browser_poster import browser_post_tweet
        result = browser_post_tweet(content)
        if result.get("status") == "posted":
            print(f"✅ Tweet posted via browser: {content[:60]}...")
            return result
        print(f"⚠️ Browser posting returned: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"⚠️ Browser posting failed: {e}")

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

    # Try Typefully first (supports threads natively)
    if TYPEFULLY_API_KEY:
        result = _typefully_post(processed[0], schedule=schedule, thread_tweets=processed)
        if "error" not in result:
            print(f"✅ Thread posted via Typefully ({len(processed)} tweets)")
            return {"status": "posted", "total": len(processed), "method": "typefully_v2", "tweets": processed}

    # Fallback: Browser posting (posts individually)
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

    return {"status": "failed", "reason": "No posting method available"}
