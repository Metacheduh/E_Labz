"""Gov watch tools — fetch IRS newsroom, Federal Register, Congress.gov. Stdlib-only."""

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


def _fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context()) as resp:
        return resp.read().decode("utf-8", errors="replace")


@tool
def search_federal_register(query: str) -> dict:
    """Search the Federal Register API for regulatory notices, rules, and proposed rules."""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.federalregister.gov/api/v1/documents.json?conditions%5Bterm%5D={encoded}&per_page=10&order=newest"
        content = _fetch(url)
        data = json.loads(content)
        results = []
        for doc in data.get("results", []):
            results.append({
                "title": doc.get("title", ""),
                "type": doc.get("type", ""),
                "abstract": doc.get("abstract", "")[:500] if doc.get("abstract") else "",
                "publication_date": doc.get("publication_date", ""),
                "agencies": [a.get("name", "") for a in doc.get("agencies", [])],
                "url": doc.get("html_url", ""),
                "document_number": doc.get("document_number", ""),
            })
        return {
            "query": query,
            "results_count": len(results),
            "results": results,
        }
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def search_irs_newsroom(query: str) -> dict:
    """Search IRS newsroom for tax-related updates and announcements."""
    try:
        encoded = urllib.parse.quote_plus(f"site:irs.gov/newsroom {query}")
        url = f"https://www.google.com/search?q={encoded}&num=10"
        html = _fetch(url)

        results = []
        urls = re.findall(r'href="/url\?q=(https?://[^&"]+irs\.gov[^&"]*)', html)
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)

        for i, u in enumerate(urls[:10]):
            clean_url = urllib.parse.unquote(u)
            title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else ""
            results.append({"title": title, "url": clean_url})

        return {
            "query": query,
            "results_count": len(results),
            "results": results,
        }
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def search_congress(query: str) -> dict:
    """Search Congress.gov for legislation, hearings, and committee reports."""
    try:
        encoded = urllib.parse.quote_plus(f"site:congress.gov {query}")
        url = f"https://www.google.com/search?q={encoded}&num=10"
        html = _fetch(url)

        results = []
        urls = re.findall(r'href="/url\?q=(https?://[^&"]+congress\.gov[^&"]*)', html)
        titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)

        for i, u in enumerate(urls[:10]):
            clean_url = urllib.parse.unquote(u)
            title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else ""
            results.append({"title": title, "url": clean_url})

        return {
            "query": query,
            "results_count": len(results),
            "results": results,
        }
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def scrape_gov_page(url: str) -> dict:
    """Scrape a government page for its full content and key details."""
    try:
        html = _fetch(url)
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()

        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Extract dates
        dates = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', text)

        return {
            "url": url,
            "title": title,
            "content": text[:5000],
            "word_count": len(text.split()),
            "dates_mentioned": dates[:5],
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def save_alert(file_path: str, content: str) -> dict:
    """Save a regulatory alert or report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
