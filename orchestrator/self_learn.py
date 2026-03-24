"""
Free Cash Flow — Self-Learning Engine
Runs daily at 23:30. Analyzes performance, makes micro-adjustments, sends newsletter via Slack.
"""

import json
import os
from datetime import date, datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

from orchestrator.metrics import (
    get_daily_metrics,
    get_growth_metrics,
    get_monthly_revenue,
    log_config_change,
    save_daily_report,
)

# Load env
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_NEWSLETTER_CHANNEL", "swarm-reports")

CONFIG_DIR = Path(__file__).parent.parent / "config"
MAX_DAILY_CHANGE = 0.10  # Max 10% config change per day


# ============================================================
# DATA COLLECTION
# ============================================================

def collect_twitter_data() -> dict:
    """Pull today's Twitter/X metrics.
    
    Note: Per-tweet engagement (impressions, likes) requires Twitter API Basic ($200/mo).
    We use follower growth as the primary optimization signal instead — it's free and 
    correlates with content quality at the current scale (167 followers).
    """
    today_metrics = get_daily_metrics()
    growth_data = get_growth_metrics(days=7)
    return {
        "impressions": today_metrics.get("impressions", 0),
        "engagements": today_metrics.get("engagements", 0),
        "engagement_rate": today_metrics.get("engagement_rate", 0.0),
        "follower_growth": today_metrics.get("follower_growth", 0),
        "follower_total": today_metrics.get("follower_total", 0),
        "posts_published": today_metrics.get("posts_published", 0),
        "avg_daily_growth_7d": growth_data.get("avg_daily", 0),
        "days_to_500": max(0, (500 - growth_data.get("current_followers", 0)) / max(growth_data.get("avg_daily", 1), 0.1)),
    }


def collect_gumroad_data() -> dict:
    """Pull today's Gumroad revenue data."""
    monthly = get_monthly_revenue()
    today_metrics = get_daily_metrics()
    return {
        "daily_revenue": today_metrics.get("revenue", 0.0),
        "daily_sales": today_metrics.get("sales", 0),
        "running_monthly_total": monthly.get("total_revenue", 0),
        "projected_monthly": monthly.get("projected_monthly", 0),
        "target": 3000,
        "on_track": monthly.get("on_track", False),
    }


def collect_content_data() -> dict:
    """Pull content quality metrics."""
    today_metrics = get_daily_metrics()
    return {
        "ai_detection_avg": today_metrics.get("ai_detection_avg", 0.0),
        "ai_detection_max": today_metrics.get("ai_detection_max", 0.0),
        "humanization_retries": today_metrics.get("humanization_retries", 0),
        "content_flagged": today_metrics.get("content_flagged", 0),
        "posts_published": today_metrics.get("posts_published", 0),
    }


# ============================================================
# ANALYSIS
# ============================================================

def analyze_daily(twitter: dict, gumroad: dict, content: dict) -> dict:
    """Analyze today's performance and generate insights."""
    insights = {
        "date": date.today().isoformat(),
        "revenue": {
            "today": gumroad["daily_revenue"],
            "monthly_total": gumroad["running_monthly_total"],
            "projected": gumroad["projected_monthly"],
            "target": 3000,
            "on_track": gumroad["on_track"],
            "gap": max(0, 3000 - gumroad["projected_monthly"]),
        },
        "growth": {
            "followers_today": twitter["follower_growth"],
            "total_followers": twitter["follower_total"],
            "engagement_rate": twitter["engagement_rate"],
            "impressions": twitter["impressions"],
            "avg_daily_growth_7d": twitter.get("avg_daily_growth_7d", 0),
            "days_to_500": twitter.get("days_to_500", 999),
        },
        "content_quality": {
            "ai_detection_avg": content["ai_detection_avg"],
            "ai_detection_max": content["ai_detection_max"],
            "retries": content["humanization_retries"],
            "flagged": content["content_flagged"],
            "all_under_5pct": content["ai_detection_max"] < 0.05,
        },
        "recommendations": [],
    }

    # Generate recommendations
    if not gumroad["on_track"]:
        insights["recommendations"].append("Revenue behind — increase product promo frequency")
    if twitter["engagement_rate"] < 3.0 and twitter["engagement_rate"] > 0:
        insights["recommendations"].append("Engagement low — try more controversial hooks")
    if content["ai_detection_max"] >= 0.05:
        insights["recommendations"].append("AI detection too high — increase aggressiveness to 1.0")
    if twitter["follower_growth"] < 20:
        insights["recommendations"].append("Growth slow — boost reply engagement rate")
    
    # Follower growth velocity recommendations (primary signal since we can't get per-tweet data)
    avg_growth = twitter.get("avg_daily_growth_7d", 0)
    days_to_500 = twitter.get("days_to_500", 999)
    total = twitter["follower_total"]
    
    if total < 500:
        if avg_growth < 3:
            insights["recommendations"].append(
                f"🔴 CRITICAL: Only +{avg_growth:.1f} followers/day avg. At this rate, 500 followers in {days_to_500:.0f} days. "
                "Try: more threads, controversial takes, reply to large accounts"
            )
        elif avg_growth < 10:
            insights["recommendations"].append(
                f"🟡 Moderate growth: +{avg_growth:.1f}/day. {days_to_500:.0f} days to 500. "
                "Try: increase posting frequency and engagement replies"
            )
        else:
            insights["recommendations"].append(
                f"🟢 Strong growth: +{avg_growth:.1f}/day. {days_to_500:.0f} days to 500 milestone. Keep current strategy."
            )
    elif total >= 500 and total < 1000:
        insights["recommendations"].append(
            f"🎯 HIT 500! Ready to launch first paid product ($29). Current: {total} followers."
        )

    return insights


# ============================================================
# MICRO-ADJUSTMENTS (Daily, max 10% change)
# ============================================================

def apply_micro_adjustments(insights: dict) -> list[str]:
    """Make small, safe config adjustments based on today's data."""
    changes = []

    if insights["growth"]["engagement_rate"] < 2.0:
        changes.append("Consider shifting topics toward higher-performing niches")

    if insights["growth"]["impressions"] < 500:
        changes.append("Low impressions — consider adjusting posting schedule")

    if not insights["content_quality"]["all_under_5pct"]:
        changes.append("AI detection breach — tightening humanization aggressiveness")

    for change in changes:
        log_config_change("auto", change, "N/A", "adjusted", "daily_self_learn")

    return changes


# ============================================================
# NEWSLETTER GENERATION (Slack format)
# ============================================================

def generate_newsletter(insights: dict) -> tuple[str, str]:
    """Generate a fun, friendly daily newsletter for Slack.
    
    Returns (title, slack_blocks_text).
    """
    today = date.today()
    rev = insights["revenue"]
    growth = insights["growth"]
    quality = insights["content_quality"]
    recs = insights.get("recommendations", [])

    # Pick vibe
    if rev["on_track"] and quality["all_under_5pct"]:
        vibe = "🔥"
        vibe_text = "CRUSHING IT"
    elif rev["on_track"]:
        vibe = "💪"
        vibe_text = "SOLID DAY"
    elif quality["all_under_5pct"]:
        vibe = "🤖"
        vibe_text = "STEALTH MODE"
    else:
        vibe = "⚡"
        vibe_text = "WORK TO DO"

    title = f"{vibe} Swarm Report: ${rev['today']:.0f} today | {growth['followers_today']} new followers | {today.strftime('%b %d')}"

    stealth_status = "✅ ALL UNDER 5%" if quality["all_under_5pct"] else "⚠️ BREACH"
    gap_indicator = "🟢" if rev["gap"] == 0 else "🔴"

    text = f"""*{vibe} {vibe_text}*
_Daily Swarm Report — {today.strftime('%A, %B %d, %Y')}_

━━━━━━━━━━━━━━━━━━━━
*💰 Revenue*
• Today: *${rev['today']:.2f}*
• Month so far: ${rev['monthly_total']:.2f}
• Projected: ${rev['projected']:.2f}
• Target: $3,000
• {gap_indicator} Gap: ${rev['gap']:.2f}

*📈 Growth*
• New followers: *+{growth['followers_today']}*
• Total followers: {growth['total_followers']:,}
• 7-day avg growth: +{growth.get('avg_daily_growth_7d', 0):.1f}/day
• Days to 500 milestone: {growth.get('days_to_500', '?')}
• Engagement rate: {growth['engagement_rate']:.1f}%
• Impressions: {growth['impressions']:,}

*🤖 Stealth Score*
• Avg AI detection: {quality['ai_detection_avg']*100:.1f}%
• Max AI detection: {quality['ai_detection_max']*100:.1f}%
• Humanization retries: {quality['retries']}
• Content flagged: {quality['flagged']}
• Status: *{stealth_status}*
━━━━━━━━━━━━━━━━━━━━"""

    if recs:
        text += "\n\n*🧠 What I Changed*\n"
        for r in recs:
            text += f"• {r}\n"

    # Cookie health check for reply engine
    try:
        from orchestrator.browser_poster import check_cookie_health
        cookie_status = check_cookie_health()
        if cookie_status["needs_refresh"]:
            text += f"\n\n*🍪 ACTION REQUIRED*\n"
            text += f"• {cookie_status['message']}\n"
            text += f"• _Reply engine is DOWN until cookies are refreshed_\n"
        else:
            text += f"\n\n*🍪 Reply Engine*\n"
            text += f"• {cookie_status['message']}\n"
    except Exception:
        text += "\n\n*🍪 Reply Engine*\n• ⚠️ Could not check cookie status\n"

    text += f"\n\n_Generated at {datetime.now().strftime('%I:%M %p')} by Free Cash Flow Swarm_"

    return title, text


# ============================================================
# SLACK DELIVERY
# ============================================================

def send_newsletter(title: str, text: str) -> bool:
    """Send the daily newsletter to Slack."""
    if not SLACK_BOT_TOKEN:
        print(f"📋 Newsletter (no Slack token):")
        print(f"   Title: {title}")
        print(text)
        return False

    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json",
            },
            json={
                "channel": SLACK_CHANNEL,
                "text": title,
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": text},
                    }
                ],
                "unfurl_links": False,
            },
        )

        data = resp.json()
        if data.get("ok"):
            print(f"✅ Newsletter posted to #{SLACK_CHANNEL}")
            return True
        else:
            error = data.get("error", "unknown")
            print(f"⚠️ Slack error: {error}")
            # If channel not found, try creating it or posting to #general
            if error == "channel_not_found":
                print(f"   Channel #{SLACK_CHANNEL} not found — trying #general")
                resp2 = requests.post(
                    "https://slack.com/api/chat.postMessage",
                    headers={
                        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "channel": "general",
                        "text": title,
                        "blocks": [
                            {
                                "type": "section",
                                "text": {"type": "mrkdwn", "text": text},
                            }
                        ],
                    },
                )
                data2 = resp2.json()
                if data2.get("ok"):
                    print(f"✅ Newsletter posted to #general (fallback)")
                    return True
                else:
                    print(f"❌ Fallback also failed: {data2.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Failed to send newsletter to Slack: {e}")
        return False


# ============================================================
# MAIN DAILY REVIEW
# ============================================================

def run_daily_review() -> dict:
    """Main entry point. Called by scheduler every night at 23:30."""
    print(f"\n🧠 Running daily self-learning review — {date.today().isoformat()}")

    # 0. SYNC REAL DATA from Twitter API + Stripe/Gumroad
    #    This is critical — without this, we're analyzing zeros.
    try:
        from orchestrator.sync_metrics import run_full_sync
        sync_result = run_full_sync()
        print(f"  ✅ Synced {sync_result.get('tweets_synced', 0)} tweets from API")
    except Exception as e:
        print(f"  ⚠️ Sync failed (using cached data): {e}")

    # 1. Collect data (now reading real synced data from DB)
    twitter_data = collect_twitter_data()
    gumroad_data = collect_gumroad_data()
    content_data = collect_content_data()

    # 2. Analyze
    insights = analyze_daily(twitter_data, gumroad_data, content_data)

    # 3. Apply micro-adjustments
    changes = apply_micro_adjustments(insights)
    insights["changes_applied"] = changes

    # 4. Save report
    report_path = save_daily_report(insights)
    print(f"📊 Report saved to {report_path}")

    # 5. Generate and send newsletter
    subject, body = generate_newsletter(insights)
    send_newsletter(subject, body)

    return insights


if __name__ == "__main__":
    run_daily_review()
