---
name: Self-Learning System
description: The autonomous feedback loop that makes every agent smarter each DAY by analyzing performance data and adjusting strategies. Includes a daily newsletter to the owner.
---

# Self-Learning System Skill

## Purpose

The Self-Learning System is the brain behind the swarm's continuous improvement. It runs **every single day at midnight**, analyzes all agent performance data, identifies what's working and what isn't, and updates configurations to optimize for the $3K/month revenue target.

It also sends a **friendly daily newsletter** to the owner at `hernandezeslyn@gmail.com` summarizing the day's wins, losses, and what it changed.

## Architecture

```text
         ┌──────────────────┐
         │  Daily Trigger    │  (Every night at 23:30)
         └────────┬─────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐
│Collect │  │Collect │  │Collect │
│Twitter │  │Gumroad │  │Content │
│Metrics │  │Sales   │  │Quality │
└───┬────┘  └───┬────┘  └───┬────┘
    │           │           │
    └─────────┬─┘───────────┘
              │
       ┌──────▼──────┐
       │   Analyze    │
       │  Performance │
       └──────┬──────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│Update  ││Update  ││Update  │
│niche   ││schedule││templates│
│.yaml   ││.yaml   ││/       │
└────────┘└────────┘└────────┘
              │
    ┌─────────┼─────────────┐
    │         │             │
    ▼         ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Log    │ │ Send   │ │Notify  │
│ Report │ │ Email  │ │ Slack  │
└────────┘ └────────┘ └────────┘
```

**Supporting Agents:**
- `mindsdb_agent` — queries performance data in natural language
- `langgraph_agent` — runs conditional optimization workflows
- `slack_agent` — sends summary to Slack
- `notion_agent` — logs changes to knowledge base
- SMTP / SendGrid — sends the daily newsletter email

## Data Collection

### Twitter Metrics (via X API)

```python
def collect_twitter_metrics(day: date) -> dict:
    return {
        "posts_published": 3,
        "total_impressions": 6500,
        "total_engagements": 325,
        "engagement_rate": 5.0,
        "follower_growth": 50,
        "follower_total": 2100,
        "top_post": {
            "id": "tweet_123",
            "text": "Most people think...",
            "impressions": 4200,
            "engagement_rate": 8.2,
            "hook_type": "contrarian",
            "content_type": "video",
            "post_time": "12:00 ET"
        },
        "worst_post": {...},
        "replies_sent": 12,
        "reply_engagement_rate": 3.8
    }
```

### Gumroad Metrics

```python
def collect_gumroad_metrics(day: date) -> dict:
    return {
        "daily_revenue": 61.00,
        "daily_sales": 4,
        "products": [
            {
                "name": "AI Agent Playbook",
                "price": 19,
                "sales": 2,
                "revenue": 38,
                "refund_rate": 0.0,
            }
        ],
        "running_monthly_total": 1220.00,
        "days_remaining_in_month": 14,
        "projected_monthly": 2680.00,
    }
```

### Content Quality Metrics

```python
def collect_content_metrics(day: date) -> dict:
    return {
        "research_topics_generated": 2,
        "topics_used": 2,
        "videos_generated": 2,
        "videos_posted": 2,
        "ai_detection_scores": [0.03, 0.04, 0.02],  # Must be < 5%
        "avg_ai_score": 0.03,
        "max_ai_score": 0.04,
        "humanization_retries": 0,
        "content_flagged": 0,
    }
```

## Analysis Engine

```python
def analyze_daily_performance(twitter: dict, gumroad: dict, content: dict) -> dict:
    """Analyze today's metrics and generate actionable insights."""
    
    insights = {
        "revenue_status": {
            "today": gumroad["daily_revenue"],
            "running_monthly": gumroad["running_monthly_total"],
            "projected_monthly": gumroad["projected_monthly"],
            "target": 3000,
            "on_track": gumroad["projected_monthly"] >= 2700,
            "gap": max(0, 3000 - gumroad["projected_monthly"]),
            "daily_target": (3000 - gumroad["running_monthly_total"]) / max(1, gumroad["days_remaining_in_month"]),
        },
        
        "content_wins": {
            "best_post": twitter["top_post"],
            "best_hook_type": twitter["top_post"]["hook_type"],
            "best_time": twitter["top_post"]["post_time"],
        },
        
        "content_losses": {
            "worst_post": twitter["worst_post"],
            "what_flopped": analyze_why_flopped(twitter["worst_post"]),
        },
        
        "growth_status": {
            "followers_today": twitter["follower_growth"],
            "total": twitter["follower_total"],
            "daily_avg_needed_for_10k": (10000 - twitter["follower_total"]) / 150,
            "pace": "ahead" if twitter["follower_growth"] > 50 else "behind",
        },
        
        "ai_detection": {
            "avg_score": content["avg_ai_score"],
            "max_score": content["max_ai_score"],
            "all_under_5pct": content["max_ai_score"] < 0.05,
            "retries": content["humanization_retries"],
        },
        
        "changes_recommended": generate_daily_recommendations(twitter, gumroad, content),
    }
    
    return insights
```

## Configuration Updates (Daily)

### Micro-Adjustments (Daily — Safe Guardrails)

```python
def apply_daily_adjustments(insights: dict):
    """Small daily tweaks. Max 10% change per day, 50% per week."""
    
    config = load_yaml("config/niche.yaml")
    
    # If today's top post was a specific hook type, nudge weight up 5%
    best_hook = insights["content_wins"]["best_hook_type"]
    if best_hook in config["research"]["topic_weights"]:
        config["research"]["topic_weights"][best_hook] *= 1.05
    
    # If worst post was a specific type, nudge weight down 5%
    worst_type = insights["content_losses"]["what_flopped"].get("content_type")
    if worst_type and worst_type in config["research"]["topic_weights"]:
        config["research"]["topic_weights"][worst_type] *= 0.95
    
    # Normalize weights
    total = sum(config["research"]["topic_weights"].values())
    for k in config["research"]["topic_weights"]:
        config["research"]["topic_weights"][k] /= total
    
    save_yaml("config/niche.yaml", config)
    backup_config("niche.yaml")
```

### Macro-Adjustments (Weekly — Sunday Deep Review)

```python
def apply_weekly_adjustments(week_insights: list[dict]):
    """Bigger strategy shifts based on a full week of data."""
    
    # Aggregate all daily insights for the week
    weekly_data = aggregate_daily_insights(week_insights)
    
    # Shift posting times to best-performing windows
    update_schedule_config(weekly_data)
    
    # Update content templates with winning patterns
    update_templates(weekly_data)
    
    # Add/remove secondary niches
    update_niche_strategy(weekly_data)
    
    # Voice calibration
    calibrate_humanization(weekly_data)
```

## The Daily Newsletter 📬

**Sent to:** `hernandezeslyn@gmail.com`
**Time:** Every night at 23:45 ET
**Style:** Fun, friendly — like a friend texting you your wins

### Email Template

```python
def generate_daily_newsletter(insights: dict, day: date) -> str:
    """Generate a fun, casual daily newsletter."""
    
    subject = pick_subject_line(insights)
    
    body = f"""
Yo Eslyn —

Here's what your AI army did today ({day.strftime('%B %d')}).

💰 MONEY
{'='*30}
Today: ${insights['revenue_status']['today']:.2f}
This month so far: ${insights['revenue_status']['running_monthly']:.2f}
Projected monthly: ${insights['revenue_status']['projected_monthly']:.2f}
Target: $3,000 → {"ON TRACK ✅" if insights['revenue_status']['on_track'] else f"Need ${insights['revenue_status']['gap']:.0f} more 🔥"}

📈 GROWTH
{'='*30}
New followers today: +{insights['growth_status']['followers_today']}
Total: {insights['growth_status']['total']:,}
Pace to 10K: {insights['growth_status']['pace'].upper()}

🏆 TODAY'S WIN
{'='*30}
Best post hit {insights['content_wins']['best_post']['impressions']:,} impressions
Hook type: {insights['content_wins']['best_hook_type']}
Posted at: {insights['content_wins']['best_time']}
Engagement: {insights['content_wins']['best_post']['engagement_rate']}%

💀 TODAY'S L
{'='*30}
{insights['content_losses']['what_flopped'].get('reason', 'Nothing major flopped.')}

🤖 AI DETECTION
{'='*30}
Average score: {insights['ai_detection']['avg_score']*100:.1f}% (target: <5%)
Max score: {insights['ai_detection']['max_score']*100:.1f}%
Status: {"ALL CLEAR ✅" if insights['ai_detection']['all_under_5pct'] else "⚠️ NEEDS ATTENTION"}

🔧 WHAT THE SWARM CHANGED
{'='*30}
{chr(10).join(f"• {c}" for c in insights['changes_recommended'][:5])}

Tomorrow's game plan: Keep doing whatever made that top post work.

Your AI swarm is out here grinding while you sleep. 💪

— The Swarm
"""
    return subject, body


def pick_subject_line(insights: dict) -> str:
    """Pick a fun subject line based on the day's performance."""
    import random
    
    revenue = insights['revenue_status']['today']
    followers = insights['growth_status']['followers_today']
    
    options = [
        f"Your robots made ${revenue:.0f} today 🤖",
        f"+{followers} followers while you slept",
        f"Daily report: ${revenue:.0f} revenue, {followers} new followers",
        f"The swarm update: ${insights['revenue_status']['running_monthly']:.0f} this month so far",
        f"Today's best post hit {insights['content_wins']['best_post']['impressions']:,} impressions",
    ]
    
    if insights['revenue_status']['on_track']:
        options.append("We're on track for $3K this month 🎯")
    
    return random.choice(options)
```

### Email Delivery

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

OWNER_EMAIL = "hernandezeslyn@gmail.com"

def send_daily_newsletter(subject: str, body: str):
    """Send the daily newsletter via SMTP."""
    
    msg = MIMEMultipart()
    msg['From'] = os.getenv('SMTP_FROM', 'swarm@freecashflow.ai')
    msg['To'] = OWNER_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Option 1: SendGrid
    if os.getenv('SENDGRID_API_KEY'):
        send_via_sendgrid(msg)
    
    # Option 2: Gmail SMTP
    elif os.getenv('GMAIL_APP_PASSWORD'):
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(os.getenv('GMAIL_USER'), os.getenv('GMAIL_APP_PASSWORD'))
            server.send_message(msg)
    
    # Option 3: Slack fallback
    else:
        send_via_slack(body)
    
    log_info(f"Daily newsletter sent to {OWNER_EMAIL}")
```

## Daily Review Report

Every review generates a report saved to `data/performance/daily_review_YYYY-MM-DD.json`:

```json
{
  "date": "2026-03-17",
  "revenue": {
    "today": 61.00,
    "running_monthly": 1220.00,
    "projected_monthly": 2680.00,
    "target": 3000,
    "gap": 320,
    "on_track": false
  },
  "growth": {
    "followers_gained": 50,
    "total_followers": 2100,
    "days_to_10k": 158,
    "pace": "on_target"
  },
  "content": {
    "posts": 3,
    "avg_engagement_rate": 5.0,
    "best_hook": "contrarian",
    "best_time": "12:00 ET",
    "best_type": "video",
    "ai_detection_avg": 0.03,
    "ai_detection_max": 0.04
  },
  "changes_made": [
    "Nudged contrarian hook weight up 5% (top performer today)",
    "Noted 12:00 ET as best posting time (3rd day in a row)"
  ],
  "newsletter_sent": true,
  "newsletter_recipient": "hernandezeslyn@gmail.com"
}
```

## Safety Guardrails

- **Max daily change rate**: No single config value changes by more than 10% per day
- **Max weekly change rate**: No single config value changes by more than 50% per week
- **Minimum performance data**: At least 24 hours of data before making changes
- **Human review**: Newsletter emailed to owner DAILY (even though it's autonomous)
- **Rollback**: Previous configs are backed up before any changes
- **No structural changes**: Self-learning adjusts parameters, never code
- **AI detection threshold**: All content must score < 5% AI probability. No exceptions.

## Trigger

```python
# In orchestrator/scheduler.py
import schedule

# Daily self-learning + newsletter (every night)
schedule.every().day.at("23:30").do(run_daily_review)

# Weekly deep review (Sunday — bigger strategy shifts)
schedule.every().sunday.at("00:00").do(run_weekly_deep_review)

def run_daily_review():
    today = date.today()
    
    twitter_data = collect_twitter_metrics(today)
    gumroad_data = collect_gumroad_metrics(today)
    content_data = collect_content_metrics(today)
    
    insights = analyze_daily_performance(twitter_data, gumroad_data, content_data)
    
    # Apply micro-adjustments
    apply_daily_adjustments(insights)
    
    # Save report
    save_daily_report(insights, today)
    
    # Send newsletter to hernandezeslyn@gmail.com
    subject, body = generate_daily_newsletter(insights, today)
    send_daily_newsletter(subject, body)
    
    # Also notify Slack
    send_slack_summary(insights)
    
    # Log to Notion
    log_to_notion(insights, today)

def run_weekly_deep_review():
    # Load all 7 daily reports from this week
    week_insights = load_daily_reports(days=7)
    
    # Apply macro strategy shifts
    apply_weekly_adjustments(week_insights)
    
    # Generate comprehensive weekly report
    save_weekly_report(week_insights)
```
