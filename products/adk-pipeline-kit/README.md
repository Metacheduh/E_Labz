# ADK Agent Pipeline Kit — 9 Production-Ready AI Pipelines

> **Built with Google's Agent Development Kit (ADK). Run all 9 at `localhost:8000`.**

## What You Get

9 autonomous AI pipelines — each a self-contained ADK "app" with its own agent.py, sub-agents, and tools:

| # | Pipeline | What It Does |
|---|----------|-------------|
| 1 | **LeadGen** | Parallel prospecting → enrichment → outreach → scoring |
| 2 | **SiteAudit** | Auto-discovers pages, audits from 5 angles in parallel |
| 3 | **ContentEngine** | Research topics → write 5 posts in parallel |
| 4 | **IntelScout** | Scrape competitors in parallel → generate strategy |
| 5 | **GovWatch** | Loop-poll government sources → alert on changes |
| 6 | **EmailCampaign** | Write 3 sequences in parallel → compliance check |
| 7 | **FundTracker** | Poll court dockets → update dashboard data |
| 8 | **ProductLaunch** | Code + copy + docs in parallel → package product |
| 9 | **CodeAuditor** | Security + performance + quality audit in parallel |

## Quick Start

```bash
# 1. Clone and enter
cd adk-pipeline-kit

# 2. Set up Python
python3 -m venv .venv
source .venv/bin/activate

# 3. Configure
cp .env.example .env
# Add your GOOGLE_API_KEY (Gemini) to .env

# 4. Launch
adk web --port 8000
# Open http://localhost:8000 — all 9 pipelines appear in the dropdown
```

## Architecture

```
adk-pipeline-kit/
├── .env.example         # API key + model config
├── pyproject.toml       # Project config
├── leadgen/             # Pipeline 1 (fully built)
│   └── agent.py         # root_agent → sub-agents
├── siteaudit/           # Pipeline 2
├── contentengine/       # Pipeline 3
├── intelscout/          # Pipeline 4
├── govwatch/            # Pipeline 5
├── emailcampaign/       # Pipeline 6
├── fundtracker/         # Pipeline 7
├── productlaunch/       # Pipeline 8
└── codeauditor/         # Pipeline 9
```

## Design Rules

1. **Auto-discovery** — no hardcoded inputs, every pipeline discovers dynamically
2. **Stdlib-only** — no pip install, TCC compliant
3. **Parallel-first** — use ParallelAgent wherever tasks are independent
4. **State-based** — agents pass data via `output_key`, not files
5. **Output to /tmp/** — results always saved to a known location

## How Agents Work

- Each folder is an ADK "app" that appears in the dashboard dropdown
- Each app has an `agent.py` with a `root_agent` that orchestrates sub-agents
- Tools are Python functions decorated with `@tool`
- Agents use Gemini LLMs for reasoning and tool calling
- `ParallelAgent` runs sub-agents concurrently for speed
- `SequentialAgent` chains steps in order for pipelines
- `LoopAgent` polls continuously for monitoring tasks

## Extending

To add your own pipeline:

```python
# mypipeline/agent.py
from google.adk.agents import Agent

root_agent = Agent(
    name="my_pipeline",
    model="gemini-2.5-flash",
    description="My custom pipeline",
    instruction="...",
    tools=[my_tool_1, my_tool_2],
)
```

Then run `adk web --port 8000` — your new pipeline appears automatically.

## License

MIT — build anything, sell anything.

---

*Built by [E-Labz](https://e-labz-portfolio.netlify.app) — AI products shipped in weeks, not months.*
