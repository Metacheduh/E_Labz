"""Search tools for finding and scraping prospects. Stdlib-only."""

import json
import urllib.request
import urllib.parse
import re
import ssl
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
def search_google(query: str, num_results: int = 10) -> dict:
    """Search Google for prospects matching a query. Returns URLs found."""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={encoded}&num={num_results}"
    try:
        html = _fetch(url)
        # Extract URLs from Google results
        urls = re.findall(r'href="/url\?q=(https?://[^&"]+)', html)
        results = []
        seen = set()
        for u in urls:
            clean = urllib.parse.unquote(u)
            domain = urllib.parse.urlparse(clean).netloc
            if domain not in seen and "google." not in domain:
                seen.add(domain)
                results.append({"url": clean, "domain": domain})
        return {"query": query, "prospects_found": len(results), "results": results[:num_results]}
    except Exception as e:
        return {"error": str(e), "query": query}


@tool
def scrape_website(url: str) -> dict:
    """Scrape a website and extract key business info: title, description, 
    contact emails, phone numbers, social links, and main content."""
    try:
        html = _fetch(url)

        # Extract basic info
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()

        meta_desc = ""
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.IGNORECASE)
        if m:
            meta_desc = m.group(1).strip()

        # Extract emails
        emails = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)))
        # Filter out common non-person emails
        emails = [e for e in emails if not any(x in e.lower() for x in ['example.com', 'sentry.io', 'wixpress'])]

        # Extract phone numbers
        phones = list(set(re.findall(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', html)))

        # Extract social links
        social = {}
        for platform in ['linkedin', 'twitter', 'facebook', 'instagram', 'youtube']:
            links = re.findall(rf'href=["\']([^"\']*{platform}\.com[^"\']*)', html, re.IGNORECASE)
            if links:
                social[platform] = links[0]

        # Extract main text content
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        return {
            "url": url,
            "title": title,
            "description": meta_desc,
            "emails": emails[:10],
            "phones": phones[:5],
            "social_links": social,
            "content_preview": text[:3000],
            "content_length": len(text),
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def analyze_company_website(url: str) -> dict:
    """Deep-analyze a company website to extract business intelligence:
    industry, services, team size indicators, tech stack, and key pages."""
    try:
        html = _fetch(url)
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        clean = re.sub(r"<[^>]+>", " ", text)
        clean = re.sub(r"\s+", " ", clean).strip().lower()

        # Detect industry signals
        industry_keywords = {
            "fintech": ["fintech", "financial technology", "payments", "banking"],
            "saas": ["saas", "software as a service", "cloud platform", "subscription"],
            "ecommerce": ["ecommerce", "e-commerce", "online store", "shopify"],
            "healthcare": ["health", "medical", "patient", "clinical", "hipaa"],
            "real_estate": ["real estate", "property", "mortgage", "realty"],
            "consulting": ["consulting", "advisory", "strategy", "management consulting"],
            "marketing": ["marketing", "advertising", "digital marketing", "seo", "agency"],
            "ai_ml": ["artificial intelligence", "machine learning", "ai-powered", "deep learning"],
        }
        detected_industries = []
        for industry, keywords in industry_keywords.items():
            if any(kw in clean for kw in keywords):
                detected_industries.append(industry)

        # Detect team size signals
        team_signals = []
        if "hiring" in clean or "careers" in clean or "join our team" in clean:
            team_signals.append("actively_hiring")
        if re.search(r"\d{2,}\s*(?:employees|team members|people)", clean):
            team_signals.append("medium_to_large")

        # Find key pages
        links = re.findall(r'href=["\']([^"\']{5,100})["\']', html, re.IGNORECASE)
        key_pages = {}
        for link in links:
            ll = link.lower()
            if "about" in ll:
                key_pages["about"] = link
            elif "contact" in ll:
                key_pages["contact"] = link
            elif "pricing" in ll:
                key_pages["pricing"] = link
            elif "team" in ll:
                key_pages["team"] = link
            elif "blog" in ll:
                key_pages["blog"] = link

        return {
            "url": url,
            "detected_industries": detected_industries,
            "team_signals": team_signals,
            "key_pages": key_pages,
            "has_blog": "blog" in clean,
            "has_pricing": "pricing" in clean,
            "has_careers": "careers" in clean or "hiring" in clean,
        }
    except Exception as e:
        return {"error": str(e), "url": url}
