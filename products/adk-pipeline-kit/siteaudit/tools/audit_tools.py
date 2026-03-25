"""Audit tools — fetch pages, check SEO, validate links, analyze structure. Stdlib-only."""

import json
import urllib.request
import urllib.parse
import re
import ssl
import xml.etree.ElementTree as ET
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
        return resp.read().decode("utf-8", errors="replace"), resp.status


@tool
def discover_pages(url: str) -> dict:
    """Auto-discover all pages on a website by checking sitemap.xml first,
    then falling back to crawling internal links from the homepage."""
    try:
        parsed = urllib.parse.urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        pages = set()

        # Try sitemap.xml first
        sitemap_urls = [
            f"{base}/sitemap.xml",
            f"{base}/sitemap_index.xml",
        ]
        for surl in sitemap_urls:
            try:
                content, status = _fetch(surl)
                if status == 200 and "<url>" in content.lower():
                    locs = re.findall(r"<loc>(.*?)</loc>", content, re.IGNORECASE)
                    for loc in locs:
                        loc = loc.strip()
                        if loc.endswith(".xml"):
                            # Nested sitemap
                            try:
                                sub_content, _ = _fetch(loc)
                                sub_locs = re.findall(r"<loc>(.*?)</loc>", sub_content, re.IGNORECASE)
                                pages.update(l.strip() for l in sub_locs if not l.strip().endswith(".xml"))
                            except:
                                pass
                        else:
                            pages.add(loc)
            except:
                pass

        # Fallback: crawl homepage for internal links
        if not pages:
            try:
                html, _ = _fetch(url)
                links = re.findall(r'href=["\']([^"\'#]+)', html, re.IGNORECASE)
                for link in links:
                    full = urllib.parse.urljoin(url, link)
                    if base in full and not any(ext in full for ext in ['.css', '.js', '.png', '.jpg', '.svg', '.ico', '.pdf']):
                        pages.add(full)
            except:
                pass

        pages.add(url)  # Always include the given URL
        page_list = sorted(pages)

        return {
            "base_url": base,
            "pages_found": len(page_list),
            "pages": page_list,
            "discovery_method": "sitemap" if len(page_list) > 1 else "crawl",
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def audit_seo(url: str) -> dict:
    """Audit a single page for SEO: title, meta description, headings, 
    images alt text, canonical, structured data, and og tags."""
    try:
        html, status = _fetch(url)
        issues = []
        score = 100

        # Title
        title = ""
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            title = re.sub(r"\s+", " ", m.group(1)).strip()
            if len(title) < 30:
                issues.append("Title too short (< 30 chars)")
                score -= 10
            elif len(title) > 60:
                issues.append("Title too long (> 60 chars)")
                score -= 5
        else:
            issues.append("Missing <title> tag")
            score -= 20

        # Meta description
        meta_desc = ""
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)', html, re.IGNORECASE)
        if m:
            meta_desc = m.group(1).strip()
            if len(meta_desc) < 70:
                issues.append("Meta description too short (< 70 chars)")
                score -= 10
            elif len(meta_desc) > 160:
                issues.append("Meta description too long (> 160 chars)")
                score -= 5
        else:
            issues.append("Missing meta description")
            score -= 15

        # Headings
        h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
        h1_count = len(h1s)
        if h1_count == 0:
            issues.append("Missing H1 tag")
            score -= 15
        elif h1_count > 1:
            issues.append(f"Multiple H1 tags ({h1_count})")
            score -= 10

        # Images without alt
        imgs = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
        imgs_no_alt = [i for i in imgs if 'alt=' not in i.lower() or 'alt=""' in i.lower()]
        if imgs_no_alt:
            issues.append(f"{len(imgs_no_alt)} images missing alt text")
            score -= min(len(imgs_no_alt) * 3, 15)

        # Canonical
        has_canonical = bool(re.search(r'<link[^>]*rel=["\']canonical["\']', html, re.IGNORECASE))
        if not has_canonical:
            issues.append("Missing canonical tag")
            score -= 5

        # Open Graph
        has_og = bool(re.search(r'<meta[^>]*property=["\']og:', html, re.IGNORECASE))
        if not has_og:
            issues.append("Missing Open Graph tags")
            score -= 5

        # Schema/structured data
        has_schema = bool(re.search(r'"@type"', html) or re.search(r'itemtype=', html, re.IGNORECASE))

        return {
            "url": url,
            "status": status,
            "seo_score": max(score, 0),
            "title": title,
            "meta_description": meta_desc,
            "h1_count": h1_count,
            "total_images": len(imgs),
            "images_missing_alt": len(imgs_no_alt),
            "has_canonical": has_canonical,
            "has_open_graph": has_og,
            "has_structured_data": has_schema,
            "issues": issues,
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def check_links(url: str) -> dict:
    """Check all links on a page. Identifies broken links, external links,
    and redirect chains."""
    try:
        html, _ = _fetch(url)
        parsed = urllib.parse.urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        links = re.findall(r'href=["\']([^"\'#]+)', html, re.IGNORECASE)
        results = {"internal": [], "external": [], "broken": [], "mailto": []}

        checked = set()
        for link in links:
            full = urllib.parse.urljoin(url, link)
            if full in checked:
                continue
            checked.add(full)

            if link.startswith("mailto:"):
                results["mailto"].append(link)
                continue
            if link.startswith("tel:"):
                continue

            is_internal = base in full

            try:
                req = urllib.request.Request(full, method="HEAD", headers={
                    "User-Agent": "Mozilla/5.0"
                })
                with urllib.request.urlopen(req, timeout=10, context=_ssl_context()) as resp:
                    if is_internal:
                        results["internal"].append({"url": full, "status": resp.status})
                    else:
                        results["external"].append({"url": full, "status": resp.status})
            except Exception as e:
                results["broken"].append({"url": full, "error": str(e)[:100]})

            if len(checked) > 50:
                break

        return {
            "page": url,
            "total_links": len(checked),
            "internal_count": len(results["internal"]),
            "external_count": len(results["external"]),
            "broken_count": len(results["broken"]),
            "broken_links": results["broken"],
            "mailto_links": results["mailto"],
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def audit_format(url: str) -> dict:
    """Audit page formatting: inline styles, CSS classes, heading hierarchy,
    HTML structure, and accessibility basics."""
    try:
        html, _ = _fetch(url)

        # Inline styles
        inline_styles = re.findall(r'style=["\'][^"\']+', html, re.IGNORECASE)

        # Heading hierarchy
        headings = re.findall(r"<(h[1-6])[^>]*>(.*?)</\1>", html, re.IGNORECASE | re.DOTALL)
        heading_order = [int(h[0][1]) for h in headings]
        hierarchy_ok = True
        for i in range(1, len(heading_order)):
            if heading_order[i] > heading_order[i-1] + 1:
                hierarchy_ok = False
                break

        # Viewport meta
        has_viewport = bool(re.search(r'<meta[^>]*viewport', html, re.IGNORECASE))

        # Lang attribute
        has_lang = bool(re.search(r'<html[^>]*lang=', html, re.IGNORECASE))

        # Form labels
        inputs = len(re.findall(r"<input", html, re.IGNORECASE))
        labels = len(re.findall(r"<label", html, re.IGNORECASE))

        issues = []
        if inline_styles:
            issues.append(f"{len(inline_styles)} inline styles found (use CSS classes)")
        if not hierarchy_ok:
            issues.append("Heading hierarchy skips levels")
        if not has_viewport:
            issues.append("Missing viewport meta tag")
        if not has_lang:
            issues.append("Missing lang attribute on <html>")
        if inputs > 0 and labels < inputs:
            issues.append(f"Inputs without labels ({inputs} inputs, {labels} labels)")

        return {
            "url": url,
            "inline_style_count": len(inline_styles),
            "heading_hierarchy_valid": hierarchy_ok,
            "headings": [{"level": h[0], "text": re.sub(r'<[^>]+>', '', h[1]).strip()[:80]} for h in headings],
            "has_viewport": has_viewport,
            "has_lang": has_lang,
            "form_inputs": inputs,
            "form_labels": labels,
            "issues": issues,
        }
    except Exception as e:
        return {"error": str(e), "url": url}


@tool
def audit_content(url: str) -> dict:
    """Audit page content quality: word count, readability, keyword density,
    and content structure."""
    try:
        html, _ = _fetch(url)

        # Extract text
        text = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        words = text.split()
        word_count = len(words)

        # Sentence count (rough)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if len(s.strip()) > 5])

        # Average words per sentence
        avg_words = word_count / max(sentence_count, 1)

        # Paragraphs
        paragraphs = re.findall(r"<p[^>]*>.*?</p>", html, re.IGNORECASE | re.DOTALL)

        # CTAs
        ctas = re.findall(r'<(?:a|button)[^>]*>.*?(?:get started|contact|sign up|learn more|schedule|book|call|apply).*?</(?:a|button)>', html, re.IGNORECASE | re.DOTALL)

        issues = []
        if word_count < 300:
            issues.append(f"Thin content ({word_count} words, recommend 300+)")
        if avg_words > 25:
            issues.append(f"Sentences too long (avg {avg_words:.0f} words)")
        if len(paragraphs) < 3:
            issues.append("Few paragraphs — content may lack structure")
        if not ctas:
            issues.append("No clear call-to-action found")

        return {
            "url": url,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": round(avg_words, 1),
            "paragraph_count": len(paragraphs),
            "cta_count": len(ctas),
            "issues": issues,
        }
    except Exception as e:
        return {"error": str(e), "url": url}
