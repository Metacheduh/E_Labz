"""
Free Cash Flow — Metrics Sync Engine
Pulls REAL data from Twitter API + Gumroad/Stripe into the local metrics DB.
This bridges the gap: the swarm posts content but wasn't tracking the results.

Run manually:     python3 -m orchestrator.sync_metrics
Run via scheduler: Called automatically before self_learn.py each night
"""

import os
import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import requests
try:
    import tweepy
except ImportError:
    tweepy = None
from dotenv import load_dotenv

from orchestrator.metrics import (
    log_daily_metrics,
    log_post_metrics,
    _get_db,
)

# Load env
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


# ============================================================
# TWITTER SYNC — Pull real engagement data
# ============================================================

def _get_client():
    """Get authenticated Tweepy v2 client. Returns None if tweepy unavailable."""
    if tweepy is None:
        return None
    return tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
    )


def sync_twitter_profile() -> dict:
    """Pull current follower count and profile metrics from Twitter API."""
    print("[SYNC] Pulling Twitter profile metrics...")
    try:
        client = _get_client()
        if client is None:
            print("  [SKIP] tweepy not installed — skipping Twitter sync")
            return {}
        me = client.get_me(
            user_auth=True,
            user_fields=["public_metrics", "created_at", "description"],
        )
        if me and me.data:
            pm = {}
            if hasattr(me.data, "public_metrics") and me.data.public_metrics:
                pm = me.data.public_metrics
            elif hasattr(me.data, "get"):
                pm = me.data.get("public_metrics", {})

            profile = {
                "id": str(me.data.id),
                "username": me.data.username,
                "name": me.data.name,
                "followers_count": pm.get("followers_count", 0),
                "following_count": pm.get("following_count", 0),
                "tweet_count": pm.get("tweet_count", 0),
                "listed_count": pm.get("listed_count", 0),
            }
            print(f"  [OK] @{profile['username']}: {profile['followers_count']} followers, {profile['tweet_count']} posts")
            return profile
    except Exception as e:
        print(f"  [ERR] Twitter profile sync failed: {e}")
    return {}


def sync_recent_tweets(count: int = 20) -> list[dict]:
    """Pull recent tweets with engagement metrics from Twitter API."""
    print(f"[SYNC] Pulling last {count} tweets with engagement data...")
    try:
        client = _get_client()
        if client is None:
            print("  [SKIP] tweepy not installed")
            return []
        me = client.get_me(user_auth=True)
        if not me or not me.data:
            print("  [ERR] Could not get authenticated user")
            return []

        tweets = client.get_users_tweets(
            me.data.id,
            max_results=min(count, 100),
            tweet_fields=["public_metrics", "created_at", "text"],
            user_auth=True,
        )

        if not tweets or not tweets.data:
            print("  [WARN] No tweets returned from API")
            return []

        results = []
        total_impressions = 0
        total_engagements = 0

        for t in tweets.data:
            pm = t.public_metrics if hasattr(t, "public_metrics") and t.public_metrics else {}
            impressions = pm.get("impression_count", 0)
            likes = pm.get("like_count", 0)
            replies = pm.get("reply_count", 0)
            retweets = pm.get("retweet_count", 0)
            engagements = likes + replies + retweets

            total_impressions += impressions
            total_engagements += engagements

            post = {
                "id": str(t.id),
                "text": t.text if hasattr(t, "text") else "",
                "created_at": str(t.created_at) if hasattr(t, "created_at") else "",
                "impressions": impressions,
                "engagements": engagements,
                "engagement_rate": (engagements / max(impressions, 1)) * 100,
                "likes": likes,
                "replies": replies,
                "retweets": retweets,
                "content_type": _classify_content(t.text if hasattr(t, "text") else ""),
            }
            results.append(post)

            # Log each post to SQLite
            log_post_metrics(post)

        print(f"  [OK] Synced {len(results)} tweets")
        print(f"     Total impressions: {total_impressions:,}")
        print(f"     Total engagements: {total_engagements:,}")
        if total_impressions > 0:
            print(f"     Avg engagement rate: {(total_engagements/total_impressions)*100:.2f}%")

        # Save to output/tweets/ for local history
        tweets_dir = OUTPUT_DIR / "tweets"
        tweets_dir.mkdir(parents=True, exist_ok=True)
        filepath = tweets_dir / f"sync_{date.today().isoformat()}.json"
        filepath.write_text(json.dumps(results, indent=2, default=str))
        print(f"     Saved to {filepath}")

        return results

    except Exception as e:
        print(f"  [ERR] Tweet sync failed: {e}")
        return []


def _classify_content(text: str) -> str:
    """Simple content type classifier based on text patterns."""
    text_lower = text.lower()
    if "thread" in text_lower:
        return "thread"
    elif text.startswith("RT @"):
        return "retweet"
    elif text.startswith("@"):
        return "reply"
    elif len(text) < 100:
        return "short_tweet"
    else:
        return "tweet"


# ============================================================
# STORE SYNC — Pull real revenue data from Stripe
# ============================================================

def sync_stripe_revenue() -> dict:
    """Pull today's revenue from Stripe API."""
    stripe_key = os.getenv("STRIPE_SECRET_KEY", "")
    if not stripe_key:
        print("  [SKIP] No Stripe key -- skipping revenue sync")
        return {"revenue": 0.0, "sales": 0}

    print("[SYNC] Pulling Stripe revenue...")
    try:
        # Get today's charges
        today_start = datetime.combine(date.today(), datetime.min.time())
        timestamp = int(today_start.timestamp())

        resp = requests.get(
            "https://api.stripe.com/v1/charges",
            params={
                "created[gte]": timestamp,
                "limit": 100,
            },
            auth=(stripe_key, ""),
        )

        if resp.status_code == 200:
            data = resp.json()
            charges = data.get("data", [])
            successful = [c for c in charges if c.get("status") == "succeeded"]
            total_revenue = sum(c.get("amount", 0) for c in successful) / 100  # cents to dollars
            total_sales = len(successful)

            result = {"revenue": total_revenue, "sales": total_sales}
            print(f"  [OK] Stripe: ${total_revenue:.2f} from {total_sales} sales today")
            return result
        else:
            print(f"  [WARN] Stripe API error {resp.status_code}: {resp.text[:200]}")
            return {"revenue": 0.0, "sales": 0}

    except Exception as e:
        print(f"  [ERR] Stripe sync failed: {e}")
        return {"revenue": 0.0, "sales": 0}


def sync_gumroad_revenue() -> dict:
    """Pull today's revenue from Gumroad API."""
    gumroad_token = os.getenv("GUMROAD_ACCESS_TOKEN", "")
    if not gumroad_token:
        return {"revenue": 0.0, "sales": 0}

    print("[SYNC] Pulling Gumroad revenue...")
    try:
        resp = requests.get(
            "https://api.gumroad.com/v2/sales",
            params={
                "access_token": gumroad_token,
                "after": date.today().isoformat(),
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            sales = data.get("sales", [])
            total_revenue = sum(float(s.get("price", 0)) / 100 for s in sales)
            result = {"revenue": total_revenue, "sales": len(sales)}
            print(f"  [OK] Gumroad: ${total_revenue:.2f} from {len(sales)} sales today")
            return result
        return {"revenue": 0.0, "sales": 0}
    except Exception as e:
        print(f"  [ERR] Gumroad sync failed: {e}")
        return {"revenue": 0.0, "sales": 0}


# ============================================================
# PREVIOUS FOLLOWER TRACKING
# ============================================================

_FOLLOWER_CACHE = Path(__file__).parent.parent / "data" / "follower_count.json"


def _get_previous_followers() -> int:
    """Get yesterday's follower count from cache."""
    try:
        if _FOLLOWER_CACHE.exists():
            data = json.loads(_FOLLOWER_CACHE.read_text())
            return data.get("followers", 0)
    except Exception:
        pass
    return 0


def _save_follower_count(count: int) -> None:
    """Cache today's follower count for tomorrow's comparison."""
    _FOLLOWER_CACHE.parent.mkdir(parents=True, exist_ok=True)
    _FOLLOWER_CACHE.write_text(json.dumps({
        "followers": count,
        "date": date.today().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }))


# ============================================================
# FULL SYNC — Called before self-learning each night
# ============================================================

def run_full_sync() -> dict:
    """Pull all real data from APIs and write to local metrics DB.
    
    This is the missing link: content was being posted but 
    performance was never tracked back into the system.
    """
    print("\n" + "=" * 50)
    print("METRICS SYNC -- Pulling real data from APIs")
    print("=" * 50)

    # 1. Twitter profile (follower count)
    profile = sync_twitter_profile()
    current_followers = profile.get("followers_count", 0)
    previous_followers = _get_previous_followers()
    follower_growth = current_followers - previous_followers if previous_followers > 0 else 0

    # Save for tomorrow
    if current_followers > 0:
        _save_follower_count(current_followers)

    # 2. Recent tweets with engagement
    tweets = sync_recent_tweets(count=20)
    total_impressions = sum(t.get("impressions", 0) for t in tweets)
    total_engagements = sum(t.get("engagements", 0) for t in tweets)

    # Filter to today's tweets for daily count
    today_str = date.today().isoformat()
    todays_tweets = [t for t in tweets if t.get("created_at", "").startswith(today_str)]

    # 3. Revenue (try Stripe first, then Gumroad)
    store_platform = os.getenv("STORE_PLATFORM", "gumroad")
    if store_platform == "stripe":
        revenue_data = sync_stripe_revenue()
    else:
        revenue_data = sync_gumroad_revenue()
        if revenue_data["revenue"] == 0:
            revenue_data = sync_stripe_revenue()

    # 4. Write everything to local metrics DB
    engagement_rate = (total_engagements / max(total_impressions, 1)) * 100

    daily = {
        "posts_published": len(todays_tweets) if todays_tweets else profile.get("tweet_count", 0),
        "impressions": total_impressions,
        "engagements": total_engagements,
        "engagement_rate": engagement_rate,
        "follower_growth": follower_growth,
        "follower_total": current_followers,
        "revenue": revenue_data.get("revenue", 0.0),
        "sales": revenue_data.get("sales", 0),
    }

    log_daily_metrics(daily)

    # 5. Summary
    print("\n" + "-" * 50)
    print("SYNC COMPLETE")
    print(f"  Followers: {current_followers:,} ({'+' if follower_growth >= 0 else ''}{follower_growth})")
    print(f"  Posts today: {len(todays_tweets)}")
    print(f"  Impressions (last 20 tweets): {total_impressions:,}")
    print(f"  Engagements (last 20 tweets): {total_engagements:,}")
    print(f"  Engagement rate: {engagement_rate:.2f}%")
    print(f"  Revenue today: ${revenue_data.get('revenue', 0):.2f}")
    print(f"  Sales today: {revenue_data.get('sales', 0)}")
    print("-" * 50 + "\n")

    return {
        "profile": profile,
        "tweets_synced": len(tweets),
        "daily_metrics": daily,
        "revenue": revenue_data,
    }


if __name__ == "__main__":
    run_full_sync()
