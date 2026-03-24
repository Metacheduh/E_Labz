---
description: Workspace rules for the Free Cash Flow autonomous AI swarm project
---

# Workspace Rules — Free Cash Flow

## Identity

- **Project Name**: Free Cash Flow (FCF)
- **Brand**: Autostack HQ (@AutoStackHQ)
- **Mission**: Autonomous AI pipeline that generates $3,000/month via X (Twitter) and digital product sales
- **Voice**: Friendly/Helpful — the helpful friend who figured it out first and can't wait to share
- **Persona File**: `config/persona.yaml` (source of truth for all voice decisions)

---

## Architecture

The system is organized into 4 subpackages under `orchestrator/`. That's all the custom code.

### Subpackages

| Subpackage | Files | Role |
| ---------- | ----- | ---- |
| `orchestrator/pipeline/` | `research.py`, `humanize.py`, `reply_engine.py` | Content creation — research, humanization, LLM replies |
| `orchestrator/publish/` | `browser_poster.py`, `twitter.py`, `store.py` | Distribution — browser posting, Twitter API (read-only), Gumroad/Stripe |
| `orchestrator/intelligence/` | `self_learn.py`, `sync_metrics.py`, `metrics.py` | Learning & measurement — nightly review, API sync, SQLite DB |
| `orchestrator/core/` | `scheduler.py`, `swarm_logger.py`, `launch.py` | Infrastructure — cron scheduler, structured logging, entry point |

### Key Design Decisions

1. **Browser-First Posting**: Twitter API returns 402 on writes. All posting goes through Playwright.
2. **Human Voice Gate**: ALL content passes through `humanize.py` before publishing. No exceptions.
3. **AI Detection Threshold**: ALL content must score < 5% AI probability. Under 5% or it doesn't ship.
4. **Resolved Decisions**: Check `config/resolved-decisions.yaml` before re-flagging any issue.
5. **PROJECT_ROOT**: All modules use `from orchestrator import PROJECT_ROOT` for path resolution.

---

## Code Standards

- **Language**: Python 3.11+
- **Config**: All secrets in `.env`, all tunable settings in `config/*.yaml`
- **Import Safety**: All optional imports (tweepy, etc.) wrapped in try/except
- **Type Hints**: Required on all function signatures
- **Docstrings**: Google-style docstrings on public functions
- **No Emojis in Code**: Use `[OK]`, `[ERR]`, `[WARN]`, `[SKIP]` tags in print/log statements

---

## Content Rules (Autostack HQ Voice)

### Personality

Autostack HQ is the helpful friend who figured stuff out and can't wait to share. Not a guru. Not a coach. Not an authority figure. Just someone who tests AI tools obsessively and genuinely wants to help.

**Do:**

- Share discoveries excitedly: "Honestly? Claude surprised me this week."
- Be specific: "$70/month" not "affordable"
- Use contractions always: "can't", "won't", "I've"
- Ask genuine questions to start conversations
- Celebrate other people's wins
- Acknowledge when something doesn't work
- Say "I found" not "You need"

**Don't:**

- Never challenge aggressively ("Fight me", "Change my mind")
- Never use guru/authority positioning
- Never start with "Stop doing X" commands
- Never use "comprehensive", "leverage", "utilize", "streamline"
- Never sound like a course seller or coach
- Never use emojis or hashtags in tweets

### Voice Profiles (humanize.py)

The humanizer has 6 voice profiles. **"friendly" is the default** for Autostack HQ.

| Profile | Use Case | Example |
| ------- | -------- | ------- |
| **friendly** (default) | Tweets, replies, threads | "Honestly? This tool surprised me." |
| casual | Variety injection | "yeah tried this last week, solid" |
| warm | Supportive replies | "genuinely love this approach" |
| professional | Threads, ebooks | "in practice, the tradeoff is..." |
| technical | Tool deep-dives | "under the hood, the bottleneck is..." |
| blunt | Reserved for strong takes | "straight up, this isn't worth it" |

**Content-Voice Mapping** (auto-selected by content type):

- Tweets: 70% friendly, 30% casual
- Replies: friendly > warm > casual
- Threads: friendly > professional
- Ebooks: professional > warm

---

## RULE #1: NEVER SOUND LIKE AI (Non-Negotiable)

**Every piece of content must read as if a real human typed it.** If AI detectors, social media platforms, or the audience can tell it's AI-generated, we have FAILED.

### Banned Phrases — NEVER use these:

- "In today's rapidly evolving landscape..."
- "It's worth noting that..."
- "Let's dive in" / "Let's break this down"
- "In conclusion" / "To summarize"
- "Leverage" / "Utilize" / "Facilitate" / "Streamline"
- "Comprehensive" / "Robust" / "Cutting-edge" / "Game-changer"
- "Landscape" / "Paradigm" / "Ecosystem" / "Synergy"
- "Navigate" (when not talking about directions)
- "Delve" / "Delve into" / "Realm" / "Tapestry" / "Embark"
- "Foster" / "Cultivate" / "Harness"
- "It's important to note" / "It's crucial to understand"
- Any sentence starting with "As a..."
- "I hope this helps!"

### Banned Structural Patterns:

- Perfectly parallel sentence structures
- Every paragraph the same length
- Lists where every item follows the exact same grammatical pattern
- Opening with a broad, sweeping statement about the state of the world
- Closing with a tidy summary that wraps everything up in a bow

### What Human Content Looks Like (DO THIS):

1. **Vary sentence length wildly.** Mix 3-word punches with longer explanations.
2. **Be specific and personal.** "$247 on Tuesday" beats "significant revenue growth."
3. **Use contractions.** "Don't" not "do not." Always.
4. **Include imperfections.** Incomplete thoughts. "And" or "But" to start sentences. Ending with "...right?" or "...honestly."
5. **Share real opinions.** "This works" not "This might potentially be beneficial."
6. **Use natural, friendly language.** "That's really cool." "Honestly kind of wild." "No joke."
7. **Reference real, specific things.** Dates, dollar amounts, tool names, personal experiences.
8. **Show genuine emotion.** Excitement about discoveries. Frustration when tools don't work. Surprise at results.

### Mandatory Humanization Pipeline (humanize.py)

Every piece of content goes through 4 stages:

1. **Detox** — Strip 30 categories of AI patterns
2. **Personality** — Inject voice markers from the selected profile
3. **Chaos** — Add burstiness (sentence length variance) + perplexity (unexpected word choices)
4. **Voice Lock** — Force contractions, kill formal pronouns

Then verified against 6 checks. Must pass all to publish without warning.

### AI Detection Countermeasures

| Detector Signal | How We Beat It |
| --------------- | -------------- |
| **Low perplexity** | Unexpected words, friendly slang, creative phrasing |
| **Low burstiness** | Wildly vary sentence length. Fragment. Then a longer run-on. |
| **Repetitive structure** | Break patterns. Skip transitions. Jump between ideas. |
| **Hedge language** | Commit with friendly confidence. "This works." "Tried it, love it." |
| **Perfect grammar** | Casual grammar. Start with "And." Fragments everywhere. |
| **Emotional flatness** | Show genuine excitement, surprise, curiosity |
| **Generic openings** | Start mid-thought. "So I tried this thing..." |

---

## File Organization

```text
Free_Cash_Flow/
├── .agents/
│   ├── rules.md              ← THIS FILE
│   ├── skills/
│   │   ├── human_voice/      ← Humanizer documentation
│   │   └── orchestrator/     ← Pipeline documentation
│   └── workflows/
│       ├── content-voice-rules.md  ← /content-voice-rules
│       ├── daily-pipeline.md       ← /daily-pipeline
│       ├── kill-switch.md          ← /kill-switch
│       ├── revenue-check.md        ← /revenue-check
│       └── x-login-rules.md        ← /x-login-rules
├── orchestrator/              ← ALL custom code (12 files, ~4,300 LOC)
│   ├── scheduler.py
│   ├── humanize.py
│   ├── browser_poster.py
│   ├── reply_engine.py
│   ├── research.py
│   ├── twitter.py
│   ├── sync_metrics.py
│   ├── metrics.py
│   ├── self_learn.py
│   ├── store.py
│   ├── swarm_logger.py
│   └── __init__.py
├── config/
│   ├── .env                   ← API keys (gitignored)
│   ├── persona.yaml           ← Autostack HQ personality
│   ├── niche.yaml             ← Content niche + topics
│   ├── schedule.yaml          ← Daily posting schedule
│   └── resolved-decisions.yaml
├── output/                    ← Generated content
├── data/                      ← Performance data + templates
├── logs/                      ← Post + engagement logs
└── archive/                   ← Preserved repos + docs (not active)
```

---

## Revenue Tracking

All revenue-related metrics are logged to SQLite via `metrics.py`:

- Daily: tweets posted, engagement rate, Gumroad sales
- Weekly: follower growth, conversion rate, revenue total
- Monthly: revenue vs. $3K target, top-performing content

**Store Platform**: Gumroad (active), LemonSqueezy (pending identity verification)

---

## Safety & Compliance

- **Rate Limits**: Respect all API rate limits. Use exponential backoff.
- **X Terms of Service**: No spam. Provide value. Engage authentically.
- **Content Moderation**: All generated content passes `humanize.py` quality check before posting.
- **No Misleading Claims**: Numbers must be real or clearly hypothetical.
- **Kill Switch**: `config/schedule.yaml` has a manual override to pause all agents.

---

## Self-Learning Protocol

1. Every night, `sync_metrics.py` pulls real data from APIs
2. Then `self_learn.py` analyzes performance:
   - Which tweets got the most engagement?
   - Which products sold?
   - What topics trended?
   - What content flopped?
3. It updates:
   - `config/niche.yaml` — shift topic weights
   - `data/templates/` — refine content templates
   - `config/schedule.yaml` — adjust posting times
4. Logs changes to `data/performance/`

---

## Key Resolved Decisions (see config/resolved-decisions.yaml for full list)

- **Posting**: Browser-first via Playwright. Twitter API is read-only.
- **Revenue**: Gumroad active ($19 AI Playbook), LemonSqueezy pending verification.
- **Persona**: Autostack HQ — friendly/helpful.
- **Voice**: "friendly" profile is default. 6 total profiles available.
- **Humanizer**: Never drops content. Publishes with warning if verification fails.
- **Reply Engine**: GPT-4o-mini with 5 tone rotation (casual, insightful, curious, helpful, supportive).
