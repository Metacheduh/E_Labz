# Free Cash Flow — AI Content Swarm

Autonomous AI pipeline that generates $3K/month via X (Twitter) and digital product sales.

**Brand:** Autostack HQ (@AutoStackHQ)  
**Account:** @JEH005432  
**Voice:** Friendly/Helpful — the helpful friend who figured it out first

## Quick Start

```bash
cd ~/Documents/Free_Cash_Flow
source .venv/bin/activate
python -m orchestrator.core.scheduler
```

## Architecture

```
orchestrator/
├── pipeline/        # Content creation (research, humanize, replies)
├── publish/         # Distribution (browser posting, Twitter API, store)
├── intelligence/    # Learning & measurement (self-learn, metrics, sync)
└── core/            # Infrastructure (scheduler, logging)
```

## Key Commands

```bash
# Start the swarm (runs on schedule)
python -m orchestrator.core.scheduler

# Post a tweet manually
python -c "from orchestrator.publish.twitter import post_tweet; post_tweet('text', humanize=True)"

# Run engagement replies
python -c "from orchestrator.pipeline.reply_engine import run_engagement_session; run_engagement_session()"

# Sync metrics from Twitter API + Stripe
python -c "from orchestrator.intelligence.sync_metrics import run_full_sync; run_full_sync()"

# Run self-learning review
python -c "from orchestrator.intelligence.self_learn import run_daily_review; run_daily_review()"

# Refresh X cookies (semi-manual)
python scripts/refresh_x_cookies.py

# Kill switch
echo "SWARM_ENABLED=false" >> config/.env
```

## Docs

- [SWARM_STATUS.md](docs/SWARM_STATUS.md) — Full status report
- [.agents/rules.md](.agents/rules.md) — Workspace rules, voice guide, banned phrases
- [.agents/skills/human_voice/SKILL.md](.agents/skills/human_voice/SKILL.md) — Humanization engine docs
- [.agents/skills/orchestrator/SKILL.md](.agents/skills/orchestrator/SKILL.md) — Orchestrator architecture

## Workflows

- `/daily-pipeline` — Manual pipeline run
- `/kill-switch` — Emergency shutdown
- `/revenue-check` — Revenue dashboard
- `/content-voice-rules` — Writing guidelines
- `/x-login-rules` — X login procedures
