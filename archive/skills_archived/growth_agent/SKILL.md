---
name: Growth Agent
description: Configure and operate the X growth and audience-building agent for follower acquisition and community engagement.
---

# Growth Agent Skill

## Purpose

The Growth Agent focuses exclusively on growing the X audience and building community. While the Twitter Agent handles content posting, the Growth Agent handles discovery, engagement, and follower acquisition. Target: **10K followers by Month 5**.

## Setup

### Clone

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/wassim249/xgrow.git growth
cd growth
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

## Growth Strategies

### 1. Curated AI News Posts

Post 2-3 curated AI news items daily (sourced from Research Agent):

```python
news_post_config = {
    "source": "output/research/daily_report.json",
    "format": "insight_not_news",  # Don't just share — add a take
    "template": (
        "{news_headline}\n\n"
        "What this actually means:\n"
        "{insight}\n\n"
        "The opportunity: {opportunity}\n\n"
        "Follow for daily AI breakdowns."
    ),
    "frequency": "2x/day",
    "times": ["10:30 ET", "22:00 ET"]
}
```

### 2. Strategic Engagement

```python
engagement_strategy = {
    "target_accounts": {
        "tier_1": [  # Big accounts (100K+) — reply for visibility
            "Search for: AI, automation, tech founders",
            "Goal: Get seen by their followers"
        ],
        "tier_2": [  # Medium accounts (10K-100K) — build relationships
            "Search for: solopreneurs, indie hackers, AI builders",
            "Goal: Get reposts and mutual follows"
        ],
        "tier_3": [  # Small accounts (1K-10K) — community building
            "Search for: AI learners, aspiring builders",
            "Goal: Build loyal community members"
        ]
    },
    "reply_quality_rules": [
        "Add a data point they didn't mention",
        "Share a relevant personal result",
        "Ask a specific, thoughtful question",
        "NEVER: 'Great post!' or generic engagement"
    ],
    "daily_targets": {
        "tier_1_replies": 5,
        "tier_2_replies": 10,
        "tier_3_replies": 10
    }
}
```

### 3. Topic Hijacking

Jump on trending topics with AI angles:

```python
trending_config = {
    "monitor": "Twitter Trending + Research Agent",
    "filter": "Must have a legitimate AI/automation angle",
    "response_time": "< 30 minutes of trend detection",
    "template": (
        "Everyone's talking about {trend}.\n\n"
        "Here's what nobody's saying:\n"
        "{unique_angle}\n\n"
        "{data_point}\n\n"
        "Follow for takes that cut through the noise."
    )
}
```

### 4. Collaboration Pipeline

```python
collab_config = {
    "identify": "Accounts with similar audience size + complementary content",
    "approach": "Provide value first (quote tweet, share insights)",
    "ask": "Cross-promotion, guest threads, joint products",
    "timeline": "After 2-3 value-first interactions"
}
```

## Follower Growth Targets

```
Week 1:    0 → 100     (Seeding phase — heavy engagement)
Week 2:  100 → 300     (Content + engagement compounding)
Month 1: 300 → 500     (Monetization eligible)
Month 2: 500 → 2,000   (Viral content starts hitting)
Month 3: 2K  → 5,000   (Network effects kick in)
Month 4: 5K  → 8,000   (Sponsor-ready)
Month 5: 8K  → 10,000  (Target hit — $3K/month)
```

## Engagement Quality Metrics

```python
quality_metrics = {
    "reply_engagement_rate": 0.0,    # How many replies get liked/replied to
    "follower_conversion_rate": 0.0,  # Profile visits → follows
    "content_share_rate": 0.0,        # How often our content gets reposted
    "community_sentiment": "positive", # Manual weekly check
}
```

## Audience Segmentation

```yaml
audience_segments:
  builders:
    description: "People actively building with AI"
    content: "Technical breakdowns, tool reviews, implementation guides"
    percentage_target: 40%
    
  curious:
    description: "People interested in AI but haven't started"
    content: "Beginner guides, use cases, success stories"
    percentage_target: 35%
    
  buyers:
    description: "People ready to invest in learning"
    content: "Product promotions, testimonials, ROI breakdowns"
    percentage_target: 25%
```

## Self-Learning

Weekly metrics review:
- Net follower gain rate trend
- Which engagement strategies drive the most follows
- Which content types get shared the most
- Optimal times for engagement (when target accounts are active)
- Quality of followers (engagement rate, not just count)

Adjustments:
- Shift engagement time to highest-converting windows
- Focus on engagement tiers that produce the best ROI
- Adjust content mix based on audience segment growth
- Retire strategies with low conversion rates
