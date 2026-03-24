import os
import json
import re
from pathlib import Path
from orchestrator.store import get_store

# Config
PORTFOLIO_DIR = Path(__file__).parent.parent / "portfolio"
INDEX_HTML = PORTFOLIO_DIR / "index.html"

# Product Catalog
PRODUCTS = [
    {"name": "👑 The Faceless Empire", "price": 39.00, "desc": "Build a revenue-generating AI content business without showing your face. Full system blueprint."},
    {"name": "📕 The AI Swarm Playbook", "price": 19.00, "desc": "The complete guide to building autonomous AI agent swarms. 6-agent framework, orchestration patterns."},
    {"name": "⚡ AI Automation Playbook", "price": 29.00, "desc": "40+ automation recipes, prompt templates, and tool configs. Copy, paste, deploy."},
    {"name": "📗 AI Swarm — User Guide", "price": 29.00, "desc": "From startup to income. Step-by-step guide to running your autonomous content swarm with Genkit + ADK."},
    {"name": "🤖 AI Chatbot Kit", "price": 29.00, "desc": "Drop-in chatbot with customizable personality & knowledge base."},
    {"name": "📈 SEO Audit Agent", "price": 49.00, "desc": "5 parallel agents crawl & audit your site from every angle."},
    {"name": "🔄 Content Repurposer", "price": 19.00, "desc": "Transform one piece of content into threads, posts, and newsletters."},
    {"name": "📝 Invoice Follow-Up", "price": 19.00, "desc": "n8n workflow for automatic invoice tracking & escalation."},
    {"name": "⚙️ Content Pipeline", "price": 39.00, "desc": "Research → Draft → Humanize → Post. Full automation workflow."},
    {"name": "⚙️ Lead Gen Workflow", "price": 49.00, "desc": "Auto-find, qualify, and reach leads with AI-powered outreach."},
    {"name": "💬 Jay Shetty Voice Pack", "price": 9.00, "desc": "System prompts for wisdom-driven, story-first AI content."},
    {"name": "💬 Anti-AI Detection Pack", "price": 19.00, "desc": "30-category humanization system. Under 5% AI detection."},
    {"name": "📄 SaaS Starter Kit", "price": 79.00, "desc": "Auth, billing, AI features, cloud infra. Launch-ready."},
    {"name": "📄 AI Dashboard Template", "price": 39.00, "desc": "Real-time analytics dashboard with AI-powered insights."},
    {"name": "🚀 Lemon Squeezy Launch Kit", "price": 19.00, "desc": "Complete launch strategy for digital products on Lemon Squeezy. Pricing, positioning, and checklist."},
    {"name": "📊 Marketing & SEO Playbook", "price": 19.00, "desc": "Drive organic traffic to your digital products. Keyword strategy, content plan, and growth hacks."},
]

def sync_store():
    print("🚀 Starting Store Sync (Lemon Squeezy)...")
    store = get_store()
    if not store or store.__class__.__name__ != "LemonSqueezyStore":
        print("❌ Store not configured for Lemon Squeezy. Check .env")
        return

    # 1. Fetch or Create Products
    existing = {p["name"]: p["url"] for p in store.list_products()}
    links = {}

    for p_info in PRODUCTS:
        name = p_info["name"]
        if name in existing:
            print(f"ℹ️ Found existing: {name} → {existing[name]}")
            links[name] = existing[name]
        else:
            print(f"🆕 Creating: {name}...")
            new_p = store.create_product(name, p_info["price"], p_info["desc"])
            if "checkout_url" in new_p:
                links[name] = new_p["checkout_url"]
            else:
                links[name] = "https://app.lemonsqueezy.com" # Fallback

    # 2. Update index.html
    if not INDEX_HTML.exists():
        print(f"❌ Could not find {INDEX_HTML}")
        return

    content = INDEX_HTML.read_text()
    
    # Replace Gumroad links with our new specific links
    # We look for the <h3>[Name]</h3> section and replace the href in the following <a> tag
    for name, url in links.items():
        # Match pattern: <h3>...Name...</h3>.*?href=".*?"
        # Using a slightly fuzzy match for the name since it might have emojis
        safe_name = re.escape(name)
        pattern = rf'<h3>{safe_name}</h3>.*?href="([^"]*)"'
        
        # We find all matches and replace them
        matches = re.finditer(pattern, content, re.DOTALL)
        for match in matches:
            old_url = match.group(1)
            content = content.replace(f'href="{old_url}"', f'href="{url}"', 1)
            print(f"🔗 Linked: {name} -> {url}")

    # Global footer link rename
    content = content.replace("Browse All Products on Gumroad", "Browse All Products on Lemon Squeezy")
    content = content.replace("aut0stack.gumroad.com", "aut0stack.lemonsqueezy.com")
    content = content.replace("Gumroad Launch Kit", "Lemon Squeezy Launch Kit")

    INDEX_HTML.write_text(content)
    print("✅ Store Sync Complete! Portfolio updated.")

if __name__ == "__main__":
    sync_store()
