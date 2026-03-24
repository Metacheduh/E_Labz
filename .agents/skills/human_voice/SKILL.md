---
name: Human Voice Engine
description: The anti-AI-detection system that ensures all content reads as 100% human-written and passes all AI detectors, social media filters, and audience scrutiny.
---

# Human Voice Engine Skill

## Purpose

This is the most critical skill in the entire swarm. If content sounds like AI, the business dies. X will shadowban it. AI detectors will flag it. The audience will tune out. Every piece of content must pass through this system before being published.

## Current Implementation

The Human Voice Engine lives in `orchestrator/humanize.py` and uses **6 voice profiles** with **"friendly" as the default** for the Autostack HQ brand.

### Voice Profiles

| Profile | Use Case | Example |
|---------|----------|---------|
| **friendly** (default) | Tweets, replies, threads | "Honestly? This tool surprised me." |
| casual | Variety injection | "yeah tried this last week, solid" |
| warm | Supportive replies | "genuinely love this approach" |
| professional | Threads, ebooks | "in practice, the tradeoff is..." |
| technical | Tool deep-dives | "under the hood, the bottleneck is..." |
| blunt | Reserved for strong takes | "straight up, this isn't worth it" |

### Content-Voice Mapping

Voices are auto-selected by content type (with weighted randomization):
- **Tweets**: 70% friendly, 30% casual
- **Replies**: friendly > warm > casual
- **Threads**: friendly > professional
- **Ebooks**: professional > warm

## How AI Detectors Work (Know Your Enemy)

### 1. Perplexity (Word Predictability)

AI models choose the **most statistically probable next word**. This creates text with low perplexity — it's too "smooth," too predictable.

```
AI writes:    "AI is revolutionizing the way we work and live."
              → Every word is the most probable next word. Detector: AI

Human writes: "AI broke my entire workflow last Tuesday. Fixed it by Friday. Made $400 more."
              → Unexpected words, specific details. Detector: Human
```

**Fix**: Choose the 2nd or 3rd most likely word. Use slang. Be specific instead of general.

### 2. Burstiness (Sentence Length Variation)

AI writes sentences that are approximately the same length. Humans don't.

```
AI pattern:   [15 words] [14 words] [16 words] [15 words] [13 words]
              → Uniform. Detector: AI

Human pattern: [4 words] [22 words] [7 words] [3 words] [31 words] [5 words]
               → Wildly varied. Detector: Human
```

**Fix**: Follow a long sentence with a fragment. Then go long again. Break it. Deliberately.

### 3. Vocabulary Distribution

AI uses a narrow, "safe" vocabulary. It gravitates toward certain words:

```
AI favorites: "comprehensive," "robust," "leverage," "facilitate," "streamline,"
              "navigate," "landscape," "cutting-edge," "game-changing,"
              "delve," "realm," "tapestry," "embark," "foster"
              
Human alternatives: "solid," "works," "use," "make easier," "simplify,"
                     "figure out," "scene," "bleeding edge," "legit good,"
                     "dig into," "space," "mix," "start," "build"
```

### 4. Structural Patterns

AI creates perfectly organized, symmetrical content. Real humans are messier.

## The Humanization Pipeline

Every piece of content goes through 4 stages + verification before publishing:

```
Raw AI Output → Stage 1: Detox → Stage 2: Personality → Stage 3: Chaos → Stage 4: Voice Lock → Verify
```

### Stage 1: Detox (Remove AI Fingerprints)

Strips 30 categories of AI patterns: banned words, openers, closers, and structural patterns. Replaces formal vocabulary with plain alternatives.

### Stage 2: Personality Injection

Adds human personality markers from the selected voice profile (openers, transitions, markers). For short tweets, always adds at least one marker to ensure verification passes.

### Stage 3: Chaos Engineering (Burstiness + Perplexity)

Breaks AI's perfect patterns:
- Fragments long sentences
- Merges short sentences with dashes
- Adds micro-reactions ("Yep.", "So good.", "Love this.")
- Inserts rhetorical questions
- Drops natural filler words

### Stage 4: Voice Lock (Final Polish)

Forces contractions and replaces formal pronouns with conversational alternatives. This is the last pass before verification.

### Verification

Runs 6 checks:
1. **Banned words** — no AI vocabulary remaining
2. **Burstiness** — sentence length variance is high enough
3. **Vocabulary diversity** — not repeating the same words
4. **Structural symmetry** — patterns are broken
5. **Personality markers** — human voice markers are present
6. **Contractions** — conversational tone is enforced

Content must pass all checks. If it fails, the system tries a second pass with a different voice and max aggressiveness. Content is **never silently dropped** — it publishes with a warning if both passes fail.

### Pipeline Integration

```python
from orchestrator.humanize import publish

# All content goes through this before posting
result = publish(raw_content, content_type="tweet")
# content_type options: "tweet", "thread", "reply", "script", "ebook"
```

## Content Type-Specific Rules

### Tweets
- Max 280 chars
- At least 1 personality marker
- No "Here are X things/tips/ways" openers
- No 3+ hashtags
- At least one contraction

### Video Scripts
- Include natural filler words ("look," "honestly")
- Add pause markers ("...")
- Self-corrections ("wait, actually —")
- 1 rhetorical question per minute

### Ebooks
- 1+ personal story per chapter
- Include "mistakes I made" sections
- Informal section headers
- 30% variance in chapter lengths
- Author's notes and asides

## The 10 Commandments

1. **Never use a fancy word when a simple one works.** "Use" not "utilize."
2. **Vary your sentence length.** Like this. Then go long because sometimes you need to explain something in detail.
3. **Share opinions with friendly confidence.** "This works great." "Tried it, love it."
4. **Be specific.** "$247 on Tuesday" beats "significant revenue."
5. **Use contractions.** Always. No exceptions.
6. **Start sentences with "And," "But," "So."** AI rarely does this.
7. **Include one imperfection per piece.** A tangent, a correction, a "wait actually."
8. **Reference real things.** Dates. Names. Dollar amounts. Tools you actually use.
9. **Show genuine emotion.** Excitement, curiosity, surprise. AI is flat. Be alive.
10. **Read it out loud.** If it sounds like a press release, rewrite it. If it sounds like you're talking to a friend, ship it.
