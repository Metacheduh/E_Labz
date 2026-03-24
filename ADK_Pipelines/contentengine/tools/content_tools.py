"""Content tools — research topics, analyze trends, save articles. Stdlib-only."""

import json
import urllib.request
import urllib.parse
import re
import ssl
import os
from google.adk.tools import tool


def _ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        return resp.read().decode("utf-8", errors="replace")


@tool
def search_trending_topics(query: str, num_results: int = 10) -> dict:
    """Search Google for trending topics and content ideas in a niche."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}&num={num_results}"
    try:
        html = _fetch(url)
        # Extract titles and URLs
        results = []
        urls = re.findall(r'href="/url\?q=(https?://[^&"]+)', html)
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)

        for i, u in enumerate(urls[:num_results]):
            clean_url = urllib.parse.unquote(u)
            title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else ""
            results.append({"title": title, "url": clean_url})

        # Extract related searches
        related = re.findall(r'<div[^>]*>Related searches</div>.*?<div[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)

        return {
            "query": query,
            "results": results,
            "result_count": len(results),
        }
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def analyze_competitor_content(url: str) -> dict:
    """Analyze a competitor's content to extract topics, structure, and keyword usage."""
    try:
        html = _fetch(url)

        # Title
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()

        # Headings
        headings = re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html, re.IGNORECASE | re.DOTALL)
        headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]

        # Word count
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        word_count = len(text.split())

        return {
            "url": url,
            "title": title,
            "headings": headings[:20],
            "word_count": word_count,
            "content_preview": text[:2000],
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def save_article(file_path: str, content: str) -> dict:
    """Save an article/blog post to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}


@tool
def save_report(file_path: str, content: str) -> dict:
    """Save a summary report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
