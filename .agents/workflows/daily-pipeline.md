---
description: Run the full daily content pipeline manually — research, posting, engagement, and metrics.
---

# Daily Pipeline Workflow

Run this to manually execute the full daily pipeline (normally runs automatically via scheduler).

## Steps

### 1. Activate environment

```bash
cd ~/Documents/Free_Cash_Flow
source .venv/bin/activate
export $(cat config/.env | xargs)
```

### 2. Run research

```bash
python -c "
from orchestrator.pipeline.research import research_trending_topics, research_to_tweet_ideas
results = research_trending_topics(num_queries=3)
ideas = research_to_tweet_ideas(results)
print(f'Generated {len(ideas)} tweet ideas')
"
```

### 3. Post a tweet

```bash
python -c "
from orchestrator.publish.twitter import post_tweet
post_tweet('Your tweet text here', humanize=True)
"
```

### 4. Run reply engagement

```bash
python -c "
from orchestrator.pipeline.reply_engine import run_engagement_session
run_engagement_session(dry_run=True)
"
```

### 5. Sync metrics

```bash
python -c "
from orchestrator.intelligence.sync_metrics import run_full_sync
result = run_full_sync()
print(f'Synced {result.get(\"tweets_synced\", 0)} tweets')
"
```

### 6. Run self-learning review

```bash
python -c "
from orchestrator.intelligence.self_learn import run_daily_review
run_daily_review()
"
```

## Quick Run (Full Pipeline via Scheduler)

```bash
cd ~/Documents/Free_Cash_Flow && source .venv/bin/activate
python -m orchestrator.core.scheduler
```
