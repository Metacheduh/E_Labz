---
name: Product Agent 
description: Clone, configure, and operate the AI eBook/digital product generator to create sellable products for Gumroad.
---

# Product Agent Skill

## Purpose

The Product Agent creates digital products (ebooks, guides, prompt packs, templates) from research data and lists them on Gumroad for sale. Target: **4 new products/month** at an average price of **$15**.

## Setup

### Clone

```bash
cd ~/Documents/Free_Cash_Flow/agents
git clone --depth 1 https://github.com/UltronTheAI/eBook-Generator-AI-Agent.git product
cd product
pip install -r requirements.txt
```

### Required Environment Variables

```bash
GOOGLE_API_KEY=        # Gemini for content generation
GUMROAD_ACCESS_TOKEN=  # For listing products
```

## Product Types

### 1. Ebooks ($15-29)

Full-length guides (30-50 pages) on trending AI topics.

```python
ebook_config = {
    "title": "The AI Agent Playbook",
    "subtitle": "Build, Deploy, Profit — The No-BS Guide",
    "chapters": 8,
    "pages_per_chapter": 5,
    "style": "friendly",  # Clear paragraphs, honest claims, actionable steps
    "includes": ["table_of_contents", "action_items", "resource_links"],
    "format": "pdf"
}
```

### 2. Prompt Packs ($5-9)

Curated collections of 50-100 prompts for specific use cases.

```python
prompt_pack_config = {
    "title": "50 AI Agent Prompts That Actually Work",
    "categories": ["research", "writing", "coding", "business", "automation"],
    "prompts_per_category": 10,
    "format": "pdf + notion_template",
    "includes": ["use_case", "expected_output", "variations"]
}
```

### 3. Templates & Cheatsheets ($5-9)

One-page or few-page quick-reference guides.

```python
template_config = {
    "title": "AI Tools Cheatsheet 2026",
    "sections": ["free_tools", "paid_tools", "workflows", "integrations"],
    "format": "pdf",
    "design": "infographic_style"
}
```

### 4. Video Course Companions ($19-49)

Supplementary materials for video content.

```python
course_config = {
    "title": "Faceless AI Business Blueprint",
    "modules": 5,
    "includes": ["worksheets", "scripts", "config_files", "resource_list"],
    "format": "zip"  # Bundle of PDFs + templates
}
```

## Product Pipeline

```
Research Agent output
        │
        ├── Is it an ebook topic? → Generate 30-50pg PDF
        ├── Is it a tools list? → Generate cheatsheet
        ├── Is it a how-to? → Generate prompt pack
        └── Is it a system? → Generate blueprint bundle
        
        │
        ▼
  Gumroad API → List product → Get link
        │
        ▼
  Twitter Agent → Promote with thread
```

## Gumroad Integration

```python
import requests

def list_on_gumroad(product: dict) -> str:
    """List a product on Gumroad and return the product URL."""
    response = requests.post(
        "https://api.gumroad.com/v2/products",
        headers={"Authorization": f"Bearer {GUMROAD_TOKEN}"},
        data={
            "name": product["title"],
            "description": product["description"],
            "price": product["price"] * 100,  # cents
            "url": product["slug"],
            "preview_url": product["preview_url"],
        },
        files={"file": open(product["file_path"], "rb")}
    )
    return response.json()["product"]["short_url"]
```

## Autostack HQ Product Copy Rules

```
Title Formula: [Number] + [Outcome] + [Timeframe/Method]
  → "50 AI Prompts That 10x Your Output"
  → "The $0 AI Stack: Replace $500/Month in SaaS"

Subtitle: "How I [specific result] using [method]"
  → "How I built an AI swarm that creates content 24/7"

Pricing Psychology:
  - $5-9: Impulse buy. Low friction. Volume play.
  - $15-19: Sweet spot. Feels like a deal for 30+ pages.
  - $29-49: Premium. Needs strong proof + bundled bonuses.
  
Description Formula:
  1. Hook: "This isn't theory. This is the exact system I use."
  2. Pain: "You're spending hours doing [X]. I automated it."
  3. Proof: "Result: [specific number] in [timeframe]."
  4. Contents: Bullet list of exactly what they get.
  5. CTA: "Get instant access. No fluff. Just the system."
```

## Quality Checklist

Before listing on Gumroad:
- [ ] Title is clear and benefit-driven
- [ ] Content is actionable (not theory)
- [ ] PDF formatting is clean (no broken layouts)
- [ ] Table of contents is accurate
- [ ] Links in document all work
- [ ] Price is set correctly
- [ ] Preview/thumbnail is professional
- [ ] Description follows copy formula

## Self-Learning

The Product Agent tracks:
- Sales per product per week
- Revenue per product type (ebook vs. prompt pack vs. template)
- Which topics convert to sales best
- Which price points perform best
- Refund rate per product

Weekly adjustments:
- Create more products in high-performing categories
- Adjust pricing based on demand curves
- Retire products with zero sales after 30 days
- Bundle related products for higher AOV
