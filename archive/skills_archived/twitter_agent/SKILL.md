---
name: Twitter Agent
description: Configure and operate the X (Twitter) posting, threading, and engagement automation agent.
---

# Twitter Agent Skill

## Purpose

The Twitter Agent handles all X (Twitter) operations: posting videos, writing threads, engaging with the community, and promoting products. Target: **3 posts/day** with a growth trajectory to **10K followers by Month 5**.

## Setup

### Clone

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/pippinlovesdot/dot-automation.git twitter
cd twitter
pip install -r requirements.txt
```

### Required Environment Variables

```bash
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=
```

### X Account Setup

1. Create X account with Autostack HQ profile:
   ```
   Name: Autostack HQ
   Bio: "Testing AI tools so you don't have to.
         Sharing what actually works for automation.
         ↓ Free guide in pinned tweet"
   
   Pinned: Your best-performing thread + free lead magnet
   ```

2. Apply for X Premium ($8/mo) — required for ad revenue monetization
3. Apply for X API access (Essential tier minimum)

## Post Types

### 1. Video Post (Primary — 2x/day)

```python
video_post = {
    "type": "video",
    "media_path": "output/videos/2026-03-17_video1.mp4",
    "text": (
        "Most people think you need a team to create content.\n\n"
        "I created 90 videos this month.\n\n"
        "Cost: $0.\n"
        "Time: 0 hours.\n\n"
        "The AI swarm runs itself.\n\n"
        "Full breakdown in the guide (link in bio)."
    ),
    "schedule": "12:00 ET"
}
```

### 2. Value Thread (1x/day)

```python
thread = [
    "I automated my entire content business using 5 AI agents.\n\nHere's the exact stack (free):\n\n🧵👇",
    "Agent 1: Research\n\nEvery morning at 9am, an AI scans the internet for trending AI topics.\n\nIt scores each topic on:\n- Search volume\n- Competition\n- Monetization potential\n\nOnly topics scoring 7+/10 make the cut.",
    "Agent 2: Video\n\nThe top topic gets turned into a 60-second faceless video.\n\n- AI writes the script\n- AI generates the voiceover\n- AI selects stock footage\n- AI edits and renders\n\nOutput: A ready-to-post MP4. Zero editing.",
    # ... 3 more tweets in thread
    "That's it. 5 agents. Fully autonomous.\n\nI wrote a step-by-step guide showing exactly how to set this up.\n\nIt's free for the next 48 hours.\n\nGrab it here: [gumroad link]"
]
```

### 3. Engagement Reply (Auto — throughout day)

```python
engagement_config = {
    "mode": "value_add",  # Not generic replies
    "target_accounts": [
        "AI influencers",
        "tech founders",
        "solopreneurs"
    ],
    "reply_style": "friendly",  # Helpful, share a tip or relevant experience
    "max_replies_per_hour": 5,
    "avoid": ["arguments", "politics", "crypto promotion"],
    "template": "Most people overlook {insight}. The data shows {stat}. Worth looking into."
}
```

## Daily Posting Schedule

```yaml
schedule:
  morning:
    time: "09:00 ET"
    type: "video"
    source: "output/videos/today_video1.mp4"
    
  afternoon:
    time: "14:00 ET"  
    type: "thread"
    source: "Generated from research data"
    
  evening:
    time: "18:00 ET"
    type: "video"
    source: "output/videos/today_video2.mp4"
    
  engagement:
    frequency: "every 2 hours"
    type: "reply"
    max_per_session: 5
```

## Tweet Copy Rules

```
Format Rules:
- Max 280 chars for standalone tweets
- Thread tweets: 200-250 chars each (leave room for numbers)
- Line breaks between every sentence
- No hashtags (they look desperate and trigger bot detection)
- No emojis in main copy

Hook Formulas:
1. "Most people think [X]. The data says otherwise."
2. "I [result] in [timeframe]. Here's what I didn't do."
3. "[Number] [things] that [outcome]. None of them are [expected]."
4. "Stop [common action]. Start [better action]. Difference: [number]."

CTA Formulas:
1. "Follow for the playbook."
2. "Full system in bio. No fluff."
3. "Repost this if it hit. Follow for more."
4. "Free guide → link in bio"
```

## Metrics to Track

```python
daily_metrics = {
    "posts_published": 0,        # Target: 3
    "total_impressions": 0,       # Track growth
    "total_engagements": 0,       # Likes + replies + reposts
    "engagement_rate": 0.0,       # engagements / impressions
    "link_clicks": 0,             # Gumroad link clicks
    "new_followers": 0,           # Net follower gain
    "replies_sent": 0,            # Engagement bot replies
}
```

## Safety & Compliance

- **Rate limits**: Never exceed X API rate limits. Use exponential backoff.
- **No spam**: Every post must provide genuine value. No copy-paste engagement.
- **No automation disclosure required** (X's current policy), but keep it authentic.
- **Kill switch**: `TWITTER_ENABLED=false` in `.env` pauses all posting immediately.
- **Content review**: All threads pass through quality check before posting.
- **Banned actions**: No follow/unfollow automation, no DM spam, no bought followers.

## Self-Learning

The Twitter Agent tracks:
- Best performing post times → adjust schedule
- Best performing hooks → weight toward winning formulas
- Engagement rate by content type → more videos? more threads?
- Follower growth rate → what's working?
- Click-through rate to Gumroad → optimize CTAs

Weekly adjustments:
- Shift posting times to highest engagement windows
- Increase frequency of top-performing content types
- A/B test hook styles and track results
- Adjust reply targeting based on engagement quality
