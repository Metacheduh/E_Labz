# AutoStack ADK — Multi-Agent Pipeline System

9 autonomous AI pipelines running at `localhost:8000`, built with Google ADK.

## Quick Start

```bash
cd ~/Documents/AutoStack/adk-agents
source .venv/bin/activate
adk web --port 8000
```

Then open http://localhost:8000

## Pipelines

| # | App | Description | Status |
|---|-----|-------------|--------|
| 1 | `leadgen` | Lead generation — parallel prospecting → enrichment → outreach → scoring | ✅ Built |
| 2 | `siteaudit` | Full site QA — auto-discovers pages, parallel audit from 5 angles | 🔲 |
| 3 | `contentengine` | Content marketing — research topics → write 5 posts in parallel | 🔲 |
| 4 | `intelscout` | Competitive intelligence — scrape competitors in parallel → strategy | 🔲 |
| 5 | `govwatch` | Regulatory monitor — loop polls gov sources → alerts on changes | 🔲 |
| 6 | `emailcampaign` | Email sequences — write 3 sequences in parallel → compliance check | 🔲 |
| 7 | `fundtracker` | Litigation monitor — poll court dockets → update Fund_Dash data | 🔲 |
| 8 | `productlaunch` | Gumroad products — code + copy + docs in parallel → package | 🔲 |
| 9 | `codeauditor` | Code review — security + performance + quality in parallel | 🔲 |

## Design Principles

See [RULES.md](./RULES.md) for the full design rules. Key points:

1. **Auto-discovery** — no hardcoded inputs, every pipeline discovers dynamically
2. **Stdlib-only** — no pip install, TCC compliant
3. **Parallel-first** — use ParallelAgent wherever tasks are independent
4. **State-based** — agents pass data via `output_key`, not files
5. **Output to /tmp/** — results always saved to a known location

## Architecture

```
adk-agents/
├── .env                 # API key + model config
├── .venv/               # Python virtual environment
├── RULES.md             # Pipeline design rules
├── README.md            # This file
├── pyproject.toml       # Project config
├── leadgen/             # Pipeline 1 ✅
├── siteaudit/           # Pipeline 2
├── contentengine/       # Pipeline 3
├── intelscout/          # Pipeline 4
├── govwatch/            # Pipeline 5
├── emailcampaign/       # Pipeline 6
├── fundtracker/         # Pipeline 7
├── productlaunch/       # Pipeline 8
└── codeauditor/         # Pipeline 9
```

## How It Works

- Each folder is an ADK "app" that appears in the dashboard dropdown
- Each app has an `agent.py` with a `root_agent` that orchestrates sub-agents
- Tools are Python functions decorated with `@tool`
- Agents use Gemini LLMs for reasoning and tool calling
- ParallelAgent runs sub-agents concurrently for speed
- SequentialAgent chains steps in order for pipelines
- LoopAgent polls continuously for monitoring tasks
