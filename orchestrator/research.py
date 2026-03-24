"""
Free Cash Flow — Research Agent
Finds trending AI topics, content opportunities, and market gaps.
Uses Tavily for search + Brave as fallback.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

from orchestrator.humanize import publish

# Load env
ENV_PATH = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(ENV_PATH, override=True)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "research"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# SEARCH ENGINES
# ============================================================

def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Search using Tavily (optimized for AI agents)."""
    if not TAVILY_API_KEY:
        print("⚠️ No Tavily key — falling back to Brave")
        return search_brave(query, max_results)
    
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results,
                "include_answer": True,
            },
        )
        data = resp.json()
        
        results = []
        if data.get("answer"):
            results.append({
                "title": "AI Summary",
                "content": data["answer"],
                "url": "",
                "source": "tavily_answer",
            })
        
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
                "source": "tavily",
            })
        
        return results
    except Exception as e:
        print(f"❌ Tavily error: {e}")
        return search_brave(query, max_results)


def search_brave(query: str, max_results: int = 5) -> list[dict]:
    """Search using Brave Search API."""
    if not BRAVE_API_KEY:
        print("❌ No Brave API key configured")
        return []
    
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": max_results},
        )
        data = resp.json()
        
        results = []
        for r in data.get("web", {}).get("results", []):
            results.append({
                "title": r.get("title", ""),
                "content": r.get("description", ""),
                "url": r.get("url", ""),
                "source": "brave",
            })
        
        return results
    except Exception as e:
        print(f"❌ Brave search error: {e}")
        return []


# ============================================================
# TOPIC RESEARCH
# ============================================================

RESEARCH_QUERIES = [
    "trending AI tools {year}",
    "AI automation side hustle",
    "best AI agents for business",
    "make money with AI online",
    "AI content creation tools viral",
    "ChatGPT alternatives trending",
    "AI SaaS ideas profitable",
    "no-code AI tools making money",
]


def research_trending_topics(num_queries: int = 3) -> list[dict]:
    """Find trending AI topics for content creation."""
    year = datetime.now().year
    all_results = []
    
    for query_template in RESEARCH_QUERIES[:num_queries]:
        query = query_template.replace("{year}", str(year))
        print(f"  🔍 Researching: {query}")
        results = search_tavily(query, max_results=3)
        all_results.extend(results)
    
    return all_results


TWEET_TEMPLATES = [
    "Tried {tool} yesterday. {insight} Wild how fast this space moves.",
    "Hot take: {insight} Most people won't do this though. Their loss.",
    "Everyone's sleeping on {tool}. {insight} I've been testing it for a week and yeah... it works.",
    "Unpopular opinion — {insight} But here's the thing. The numbers don't lie.",
    "{insight} Been saying this for months. Finally people are catching on.",
    "Just ran the numbers on {tool}. {insight} Not financial advice, just math.",
    "Ok so {tool} is actually insane. {insight} Took me 20 mins to set up.",
    "The AI space rn is bonkers. {insight} And we're still early.",
]


def research_to_tweet_ideas(results: list[dict], count: int = 5) -> list[str]:
    """Convert research results into casual, human-sounding tweet drafts.
    
    Rewrites raw research into opinionated, personality-driven tweets
    that will pass the Human Voice Engine.
    """
    import random
    ideas = []
    
    for r in results:
        content = r.get("content", "")
        title = r.get("title", "")
        if len(content) < 50:
            continue
        
        # Extract the core insight (first sentence or key phrase)
        sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 20]
        if not sentences:
            continue
        
        insight = sentences[0].strip()
        if len(insight) > 120:
            insight = insight[:117] + "..."
        
        # Extract tool name from title or content
        tool = title.split("-")[0].strip().split("|")[0].strip() if title else "this AI tool"
        if len(tool) > 30:
            tool = "this"
        
        # Pick a random template and fill it
        template = random.choice(TWEET_TEMPLATES)
        tweet = template.format(tool=tool, insight=insight)
        
        # Keep under 280 chars
        if len(tweet) > 270:
            tweet = tweet[:267] + "..."
        
        ideas.append(tweet)
        if len(ideas) >= count:
            break
    
    return ideas


def run_daily_research() -> dict:
    """Main research pipeline — runs daily."""
    print("\n🔬 Running daily research...")
    
    results = research_trending_topics(num_queries=3)
    ideas = research_to_tweet_ideas(results, count=5)
    
    # Save research output
    output = {
        "date": datetime.now().isoformat(),
        "results_count": len(results),
        "tweet_ideas": ideas,
        "raw_results": results,
    }
    
    output_file = OUTPUT_DIR / f"research_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"  📄 Saved {len(results)} results, {len(ideas)} tweet ideas → {output_file.name}")
    
    return output
