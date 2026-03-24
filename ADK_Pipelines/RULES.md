# AutoStack ADK — Pipeline Design Rules

> Every pipeline built in this repo MUST follow these rules.

---

## Rule 1: Auto-Discovery

**No pipeline may hardcode counts, page numbers, company lists, or fixed inputs.**

Every pipeline MUST auto-discover its inputs from the user's prompt:
- Site audit → discovers pages from the URL's sitemap or by crawling
- Lead gen → discovers prospects based on the search query
- Content engine → discovers topics from research, not a fixed list
- Intel scout → discovers competitors from the market, not a predefined set
- Gov watch → discovers new filings, doesn't assume specific agencies
- Email campaign → adapts to whatever audience segment is given
- Fund tracker → discovers new dockets, not hardcoded case numbers
- Product launch → adapts to whatever product type is specified
- Code auditor → discovers files from the codebase path given

**If a pipeline can only work with hardcoded inputs, it's broken.**

---

## Rule 2: Stdlib-Only Python Tools

All tools must use Python standard library only. No pip install.
This is a TCC compliance requirement on macOS.

Allowed: `urllib`, `json`, `csv`, `os`, `re`, `ssl`, `html`, `subprocess`
Not allowed: `requests`, `beautifulsoup4`, `scrapy`, `pandas`, `numpy`

---

## Rule 3: Pipeline Architecture Pattern

Every pipeline follows this structure:

```
pipeline_name/
├── __init__.py          # exports root_agent
├── agent.py             # full pipeline architecture
└── tools/
    ├── __init__.py
    └── *.py             # tool modules
```

The `__init__.py` must contain exactly:
```python
from .agent import root_agent
```

---

## Rule 4: Shared State via output_key

Agents pass data between pipeline steps using `output_key`:

```python
step1 = LlmAgent(name="Step1", output_key="step1_data")
step2 = LlmAgent(name="Step2", instruction="Use data from {step1_data}")
```

Never use file-based communication between agents. Use state.

---

## Rule 5: Output to /tmp/

All pipeline outputs (CSV, reports, summaries) go to `/tmp/`:
- `/tmp/{pipeline}-results.csv`
- `/tmp/{pipeline}-report.md`
- `/tmp/{pipeline}-summary.md`

Users can then find results easily. I (the AI assistant) can read
these files for further analysis.

---

## Rule 6: ADK Patterns — Use the Right One

| Pattern | When to use |
|---------|-------------|
| `ParallelAgent` | 2+ independent tasks that don't depend on each other |
| `SequentialAgent` | Steps that must happen in order (data flows forward) |
| `LoopAgent` | Polling, retrying, iterating until a condition is met |
| `LlmAgent` | Any step that needs AI reasoning with tools |

Never use LlmAgent routing (sub_agents with transfer) when a 
SequentialAgent or ParallelAgent would work. Those are deterministic.

---

## Rule 7: Model Selection

All agents use `gemini-2.5-flash` unless they need advanced reasoning:
```python
model = "gemini-2.5-flash"      # default for all agents
model = "gemini-2.5-pro"        # only for complex analysis/strategy
```

---

## Rule 8: Error Handling in Tools

Every tool function must:
1. Return a dict (never raise exceptions to the agent)
2. Include an "error" key on failure
3. Include meaningful context in the error message

```python
@tool
def my_tool(url: str) -> dict:
    try:
        # do the work
        return {"success": True, "data": result}
    except Exception as e:
        return {"error": str(e), "url": url}
```

---

## Rule 9: Pipeline Naming

Pipeline folder names are lowercase, no underscores, no hyphens:
- `leadgen` ✅
- `siteaudit` ✅
- `contentengine` ✅
- `lead_gen` ❌
- `site-audit` ❌

These folder names become the app names in the ADK dashboard dropdown.

---

## Rule 10: Documentation

Every pipeline's `agent.py` must start with a docstring that explains:
1. What the pipeline does
2. Which ADK patterns it uses
3. The step-by-step flow
4. What outputs it produces
5. Example prompts
