"""Intel tools — search competitors, scrape profiles, analyze markets. Stdlib-only."""

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
def discover_competitors(query: str, num_results: int = 10) -> dict:
    """Search Google to auto-discover competitors in a market or niche."""
    try:
        searches = [
            f"{query} companies",
            f"best {query} services",
            f"top {query} firms",
            f"{query} competitors",
        ]
        all_results = []
        seen_domains = set()

        for sq in searches:
            encoded = urllib.parse.quote_plus(sq)
            url = f"https://www.google.com/search?q={encoded}&num={num_results}"
            try:
                html = _fetch(url)
                urls = re.findall(r'href="/url\?q=(https?://[^&"]+)', html)
                for u in urls:
                    clean = urllib.parse.unquote(u)
                    parsed = urllib.parse.urlparse(clean)
                    domain = parsed.netloc.replace("www.", "")
                    if domain not in seen_domains and not any(skip in domain for skip in [
                        "google.", "youtube.", "facebook.", "twitter.", "linkedin.",
                        "wikipedia.", "instagram.", "reddit.", "yelp."
                    ]):
                        seen_domains.add(domain)
                        all_results.append({"url": clean, "domain": domain})
            except:
                continue

        return {
            "query": query,
            "competitors_found": len(all_results),
            "competitors": all_results[:15],
        }
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def scrape_competitor(url: str) -> dict:
    """Scrape a competitor's website for key business intelligence."""
    try:
        html = _fetch(url)

        # Title
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r'<[^>]+>', '', m.group(1)).strip()

        # Meta description
        desc = ""
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.IGNORECASE)
        if m:
            desc = m.group(1).strip()

        # Headings (value proposition clues)
        h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        h2s = re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.IGNORECASE | re.DOTALL)
        h1s = [re.sub(r'<[^>]+>', '', h).strip() for h in h1s]
        h2s = [re.sub(r'<[^>]+>', '', h).strip() for h in h2s]

        # Pricing indicators
        has_pricing = bool(re.search(r'pric|cost|plan|subscription|\$\d', html, re.IGNORECASE))

        # CTAs
        ctas = re.findall(r'<(?:a|button)[^>]*>(.*?)</(?:a|button)>', html, re.IGNORECASE | re.DOTALL)
        ctas = [re.sub(r'<[^>]+>', '', c).strip() for c in ctas if len(c.strip()) > 2 and len(c.strip()) < 50]
        ctas = list(set(ctas))[:10]

        # Tech stack clues
        tech = []
        if "react" in html.lower() or "__NEXT" in html:
            tech.append("React/Next.js")
        if "vue" in html.lower():
            tech.append("Vue.js")
        if "wordpress" in html.lower() or "wp-" in html.lower():
            tech.append("WordPress")
        if "shopify" in html.lower():
            tech.append("Shopify")
        if "hubspot" in html.lower():
            tech.append("HubSpot")
        if "google-analytics" in html.lower() or "gtag" in html.lower():
            tech.append("Google Analytics")

        # Extract text for content analysis
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return {
            "url": url,
            "title": title,
            "description": desc,
            "h1": h1s[:3],
            "h2": h2s[:10],
            "has_pricing_page": has_pricing,
            "ctas": ctas,
            "tech_stack": tech,
            "word_count": len(text.split()),
            "content_preview": text[:3000],
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def save_intel_report(file_path: str, content: str) -> dict:
    """Save an intelligence report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
