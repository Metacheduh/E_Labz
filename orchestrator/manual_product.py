#!/usr/bin/env python3
"""
Manual Product Activation Script
Run: python3 orchestrator/manual_product.py "Your Topic"
"""
import os
import sys
import json
from pathlib import Path
from orchestrator.genkit_client import generate_product_campaign

def save_output(topic: str, result: dict):
    """Save campaign output to products/ folder."""
    if not result:
        print("❌ No result generated")
        return

    safe_name = topic.lower().replace(" ", "-").replace("/", "-")
    out_dir = Path("output/products") / safe_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save ebook
    ebook = result.get("ebook", {})
    ebook_path = out_dir / f"{safe_name}-ebook.md"
    content = f"# {ebook.get('title', topic)}\n\n"
    content += f"## Introduction\n{ebook.get('introduction', '')}\n\n"
    for s in ebook.get("sections", []):
        content += f"### {s.get('heading', '')}\n{s.get('body', '')}\n\n"
    content += "## Key Takeaways\n" + "\n".join([f"- {t}" for t in ebook.get("keyTakeaways", [])]) + "\n\n"
    content += f"## Closing\n{ebook.get('closingReflection', '')}"
    ebook_path.write_text(content)

    # 2. Save blog
    blog = result.get("blog", {})
    blog_path = out_dir / f"{safe_name}-blog.md"
    blog_content = f"# {blog.get('title', topic)}\n\n{blog.get('introduction', '')}\n\n"
    for s in blog.get("sections", []):
        blog_content += f"## {s.get('heading', '')}\n{s.get('body', '')}\n\n"
    blog_path.write_text(blog_content)

    # 3. Save full JSON for reference
    (out_dir / "full_campaign.json").write_text(json.dumps(result, indent=2))
    
    print(f"\n✅ PRODUCT PACK GENERATED: {out_dir}")
    print(f"   • Ebook: {ebook_path.name}")
    print(f"   • Blog: {blog_path.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 orchestrator/manual_product.py \"Topic Name\"")
        sys.exit(1)

    topic = sys.argv[1]
    print(f"🚀 Triggering Genkit Content Engine for: {topic}...")
    result = generate_product_campaign(topic)
    save_output(topic, result)
