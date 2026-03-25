# AI Content Swarm Blueprint — The Exact System Behind @AutoStackHQ

> **The full orchestrator source code, deployment configs, and step-by-step guide to run your own autonomous content swarm.**

## What You Get

The complete, production-tested orchestrator that powers the E-Labz business:

### Core Modules
- **Research Agent** — Tavily + Brave Search for trending topic discovery
- **Content Agent** — AI draft generation with context-aware templates
- **Human Voice Engine** — 5-stage humanization pipeline that passes ALL AI detectors
- **Publishing Agent** — Auto-post to Twitter/X via Typefully API v2
- **Revenue Agent** — Stripe/Lemon Squeezy sales tracking
- **Engagement Agent** — Auto-reply to mentions and quote tweets
- **Self-Learning Agent** — Daily performance review + strategy adjustment
- **Memory Service** — Persistent vector memory across all agents

### Infrastructure
- **Google Cloud Run deployment** (Dockerfile + cloudbuild.yaml)
- **Scheduler** — APScheduler with configurable daily posting schedule
- **Platform Adapters** — LinkedIn, Medium, Dev.to, Newsletter formatters
- **Swarm Logger** — Structured logging with Slack webhook integration

## Quick Start

```bash
# 1. Clone and enter
cd ai-swarm-blueprint

# 2. Install deps
pip install -r requirements.txt

# 3. Configure
cp config/.env.example config/.env
# Add your API keys: GEMINI, TYPEFULLY, TAVILY, etc.

# 4. Run locally
python -m orchestrator.scheduler

# 5. Deploy to Cloud Run
gcloud run deploy my-swarm --source .
```

## Architecture

```
orchestrator/
├── __init__.py              # Package root
├── core/
│   ├── scheduler.py         # APScheduler daily pipeline
│   └── task_router.py       # Route tasks to correct agent
├── research/
│   ├── topic_engine.py      # Trending topic discovery
│   └── trend_analyzer.py    # Engagement prediction
├── pipeline/
│   ├── content_agent.py     # Draft generation
│   └── humanize.py          # 5-stage voice engine
├── publish/
│   ├── twitter.py           # Typefully v2 + browser fallback
│   ├── browser_poster.py    # Playwright-based posting
│   └── store.py             # Product store management
├── intelligence/
│   ├── revenue_agent.py     # Stripe/Lemon Squeezy tracking
│   ├── engagement_agent.py  # Reply engine
│   └── self_learn.py        # Daily performance review
├── memory_service.py        # Vector memory (Pinecone/local)
├── platform_adapters.py     # LinkedIn, Medium, Dev.to
├── swarm_logger.py          # Structured logging
└── config/
    ├── .env.example         # All required API keys
    └── voice_profiles.json  # Human voice configurations
```

## The Human Voice Engine

The secret weapon. A 5-stage pipeline that transforms AI-generated content into text that reads as 100% human:

1. **Stage 1: Anti-Pattern Removal** — Strip "Furthermore," "Moreover," "In conclusion"
2. **Stage 2: Voice Injection** — Add personal observations, hot takes, real opinions
3. **Stage 3: Controlled Imperfections** — Em dashes, fragments, unconventional phrasing
4. **Stage 4: Rhythm Breaking** — Vary sentence length, mix short punches with flowing sentences
5. **Stage 5: Nuclear Rewrite** — Full scratch rewrite preserving key insights

Result: Content that passes ZeroGPT, GPTZero, Originality.ai, and Twitter's internal AI filters.

## Daily Schedule (Default)

```
6:00 AM  — Research trending AI topics
7:00 AM  — Generate 3 tweet drafts
7:15 AM  — Humanize through 5-stage engine
8:00 AM  — Post Tweet #1
12:00 PM — Post Tweet #2
5:00 PM  — Post Tweet #3
9:00 PM  — Run engagement replies
11:00 PM — Self-learning daily review
```

## License

MIT — build your own swarm, sell your own products.

---

*Built by [E-Labz](https://e-labz-portfolio.netlify.app) — AI products shipped in weeks, not months.*
