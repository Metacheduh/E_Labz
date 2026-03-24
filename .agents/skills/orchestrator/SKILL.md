---
name: Orchestrator
description: The central coordinator that wires all agents together, manages the daily pipeline, and serves as the only custom code in the system.
---

# Orchestrator Skill

## Purpose

The Orchestrator is the **only custom code** in the entire system. It wires together all agents into a single autonomous pipeline, manages scheduling, and coordinates the daily content → humanize → publish → engage → learn cycle.

## Architecture

```
                    ┌─────────────────┐
                    │   Orchestrator   │
                    │   (scheduler)    │
                    └────────┬────────┘
                             │
     ┌───────────┬───────────┼───────────┬───────────┐
     │           │           │           │           │
     ▼           ▼           ▼           ▼           ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Research  ││Humanize ││Twitter  ││Reply    ││Self     │
│Pipeline ││Engine   ││Poster   ││Engine   ││Learning │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

## Core Files

### orchestrator/scheduler.py

The daily automation engine. Manages:
- Tweet selection from 4 pools (value, engagement, thread starters, promo)
- Research-to-tweet pipeline integration
- Humanization of all content before posting
- Posting via browser automation (Playwright)

### orchestrator/humanize.py

Human Voice Engine v2.0. Features:
- 6 voice profiles (friendly default, casual, warm, professional, technical, blunt)
- 4-stage pipeline: Detox → Personality → Chaos → Voice Lock
- 6 verification checks
- Content never silently dropped — publishes with warning if verification fails

### orchestrator/twitter.py

Posting layer. Browser-first via Playwright (Twitter API returns 402 on writes). Falls back gracefully if browser session is unavailable.

### orchestrator/reply_engine.py

LLM-powered contextual replies:
- GPT-4o-mini generates unique, context-aware replies
- 5 tone rotation: casual, insightful, curious, helpful, supportive
- Anti-repetition tracking (rejects replies similar to last 10)
- Brand persona: Autostack HQ friendly/helpful

### orchestrator/browser_poster.py

Playwright-based browser automation for posting to X. Handles login, text entry, media upload, and posting.

### orchestrator/sync_metrics.py

Pulls real data from APIs:
- Twitter profile metrics (follower count, tweet count)
- Recent tweet engagement (impressions, likes, replies, retweets)
- Revenue from Gumroad (default) or Stripe

### orchestrator/metrics.py

Local SQLite database for storing and querying performance metrics.

### orchestrator/self_learn.py

Nightly performance review:
- Analyzes which content performed best
- Adjusts topic weights in niche.yaml
- Updates templates and posting schedule
- Generates daily report

### orchestrator/research.py

Research-to-tweet pipeline powered by Tavily API:
- Discovers trending AI topics
- Generates tweet-ready insights
- Caches results to output/research/

## Running the Orchestrator

### Development Mode

```bash
cd ~/Documents/Free_Cash_Flow
python -m orchestrator.scheduler
```

### Manual Triggers

```bash
# Post a tweet manually
python -c "from orchestrator.scheduler import post_tweet; post_tweet()"

# Run self-learning
python -c "from orchestrator.self_learn import run_daily_review; run_daily_review()"

# Sync metrics
python -m orchestrator.sync_metrics
```

## Kill Switch

To pause all agents immediately:

```bash
# In config/.env
SWARM_ENABLED=false

# Or kill the process
pkill -f "orchestrator.scheduler"
```

## Key Design Decisions

See `config/resolved-decisions.yaml` for full list:
- **Browser-first posting** — Twitter API 402 on writes
- **Friendly voice default** — not Hormozi-aggressive
- **Humanizer never drops** — publishes with warning if verification fails
- **Tweepy import guarded** — won't crash if not installed
- **agent.py deprecated** — scheduler calls modules directly
