---
name: Research Agent
description: Clone, configure, and operate the GPT Researcher agent to find trending AI topics, market gaps, and content opportunities.
---

# Research Agent Skill

## Purpose

The Research Agent discovers trending AI topics, market opportunities, and content angles that feed the entire content pipeline. It runs daily and produces structured research reports that the Video and Product agents consume.

## Setup

### Clone

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/assafelovic/gpt-researcher.git researcher
cd researcher
pip install -r requirements.txt
```

### Required Environment Variables

```bash
OPENAI_API_KEY=        # Primary LLM for research
TAVILY_API_KEY=        # Web search (GPT Researcher's default)
```

### Configuration

Edit `config/niche.yaml` to define research focus:

```yaml
research:
  primary_niche: "AI agents and automation"
  secondary_niches:
    - "no-code AI tools"
    - "AI side hustles"
    - "prompt engineering"
  banned_topics:
    - "crypto scams"
    - "get-rich-quick"
  min_trend_score: 7  # Only report topics scoring 7+/10 on trend scale
```

## Usage

### Daily Research Task

```python
from gpt_researcher import GPTResearcher

async def daily_research(topic: str) -> dict:
    researcher = GPTResearcher(
        query=f"What are the most trending and profitable {topic} topics this week?",
        report_type="research_report"
    )
    report = await researcher.conduct_research()
    return {
        "report": report,
        "topics": extract_topics(report),
        "angles": extract_content_angles(report),
        "timestamp": datetime.now().isoformat()
    }
```

### Output Format

Research reports are saved to `output/research/YYYY-MM-DD_topic.json`:

```json
{
  "date": "2026-03-17",
  "query": "trending AI agent topics March 2026",
  "topics": [
    {
      "title": "Local AI agents replacing SaaS",
      "trend_score": 9,
      "content_angle": "Why $20/month tools are dead — run your own AI for free",
      "sources": ["url1", "url2"],
      "product_opportunity": "Guide: 'Replace Your $500/month SaaS Stack with Free AI'"
    }
  ],
  "recommended_video_hooks": [
    "Everyone's paying $500/month for AI tools. I pay $0. Here's how."
  ],
  "recommended_product_ideas": [
    {"title": "The SaaS Killer Playbook", "price": 19, "format": "ebook"}
  ]
}
```

## Integration with Pipeline

```
Research Agent → output/research/YYYY-MM-DD.json
                     │
                     ├── Video Agent reads → creates video
                     └── Product Agent reads → creates ebook
```

## Self-Learning

After each weekly review, the Research Agent adjusts based on:
- Which topics led to the most engagement
- Which product ideas led to the most sales
- Trending topic shifts detected vs previous weeks

The self-learning module updates `config/niche.yaml` weights accordingly.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No results | Check TAVILY_API_KEY is valid |
| Low quality reports | Increase `max_search_results` in researcher config |
| Repeated topics | Add previously covered topics to `banned_topics` |
| Rate limited | Reduce research frequency or add delay between queries |
