---
name: Video Agent
description: Clone, configure, and operate the faceless video generator to create 60-second AI content videos for X.
---

# Video Agent Skill

## Purpose

The Video Agent creates faceless 60-second videos with engaging, friendly delivery. It takes topics from the Research Agent and produces ready-to-post MP4 files optimized for X (Twitter).

## Setup

### Clone

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/jacky-xbb/faceless-video-generator.git video
cd video
pip install -r requirements.txt
```

### Required Environment Variables

```bash
GOOGLE_API_KEY=        # Gemini for script generation
ELEVENLABS_API_KEY=    # Premium AI voiceover (recommended)
PEXELS_API_KEY=        # Stock footage (free alternative to custom images)
```

## Video Format (60 Seconds)

Every video follows this structure:

```
┌─────────────────────────────────────────┐
│  HOOK (0-5s)                            │
│  "Most people think [X]. They're wrong."│
│  Bold text on screen. Dramatic pause.   │
├─────────────────────────────────────────┤
│  BODY (5-50s)                           │
│  3 punchy points with numbers.          │
│  Each point: Problem → Fix → Number     │
│  B-roll or AI-generated visuals         │
├─────────────────────────────────────────┤
│  CTA (50-60s)                           │
│  "Follow for more."                     │
│  "Link in bio for the full guide."      │
│  Product name on screen                 │
└─────────────────────────────────────────┘
```

## Script Templates

### Template: Contrarian Take

```python
script_template = """
HOOK: "Everyone tells you to {common_advice}. That's exactly why you're stuck."

POINT 1: "{problem_1}. Instead, {fix_1}. Result: {number_1}."

POINT 2: "{problem_2}. The fix is {fix_2}. That's {number_2} saved."

POINT 3: "The real secret? {insight}. I've seen {number_3} people prove this."

CTA: "Follow for the playbook. Link in bio for the full system."
"""
```

### Template: How-To

```python
script_template = """
HOOK: "I built {result} in {timeframe}. Zero {thing}. Here's how."

STEP 1: "{step_1}. Takes {time_1}. {result_1}."

STEP 2: "{step_2}. This is where most people quit. Don't."

STEP 3: "{step_3}. {result_3}."

CTA: "Full guide in bio. No fluff. Just the system."
"""
```

## Usage

```python
from video_generator import create_video

async def generate_daily_video(research_data: dict) -> str:
    topic = research_data["topics"][0]
    
    video_config = {
        "script": generate_script(topic),
        "voice": "elevenlabs",  # or "gtts" for free
        "voice_style": "confident, fast-paced, authoritative",
        "resolution": "1080x1920",  # Vertical for X/TikTok
        "duration_target": 60,
        "background_music": "subtle-ambient",
        "text_style": {
            "font": "Impact",
            "color": "white",
            "outline": "black",
            "position": "center",
            "max_words_on_screen": 8
        }
    }
    
    output_path = f"output/videos/{date.today()}_video.mp4"
    await create_video(video_config, output_path)
    return output_path
```

## Output

Videos saved to `output/videos/`:
- `YYYY-MM-DD_video1.mp4` — morning post
- `YYYY-MM-DD_video2.mp4` — evening post
- `YYYY-MM-DD_video1_thumbnail.png` — auto-generated thumbnail

## Quality Checklist

Before a video is cleared for posting:
- [ ] Duration between 55-65 seconds
- [ ] Hook in first 3 seconds is attention-grabbing
- [ ] All text is legible (no clipping)
- [ ] Audio is clear and properly leveled
- [ ] CTA mentions product/follow
- [ ] No copyrighted music or images
- [ ] File size under 512MB (X limit)

## Self-Learning

The Video Agent tracks:
- View count per video
- Engagement rate (likes + replies + reposts / views)
- Which hook styles perform best
- Optimal posting times

Weekly, it adjusts:
- Hook template weights (use more of what works)
- Video length (shorter? longer?)
- Visual style preferences
- Posting schedule
