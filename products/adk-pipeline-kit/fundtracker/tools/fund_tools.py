"""Fund tracker tools — search, scrape, and write discoveries to Fund_Dash DB.

Stdlib-only (TCC compliant). Writes directly to the Fund_Dash SQLite
database so the dashboard picks up new cases, articles, and alerts
automatically.

NOTE: ADK 1.27+ auto-wraps plain functions as FunctionTool.
No @tool decorator needed — just pass functions directly to tools=[].
"""

import json
import urllib.request
import urllib.parse
import re
import ssl
import os
import sqlite3
import hashlib
from datetime import datetime

# ── Path to the Fund_Dash database ────────────────────────────────────
FUND_DASH_DB = os.path.expanduser("~/Documents/Fund_Dash/data/agent_manager.db")


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


def _get_db():
    """Get a connection to the Fund_Dash database."""
    conn = sqlite3.connect(FUND_DASH_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _create_job_run(conn, job_name="adk_fundtracker"):
    """Create a job_run entry and return the ID."""
    cur = conn.execute(
        "INSERT INTO job_runs (job_name, status, attempt, started_at) "
        "VALUES (?, 'running', 1, datetime('now'))",
        (job_name,),
    )
    conn.commit()
    return cur.lastrowid


# ═══════════════════════════════════════════════════════════════════════
# SEARCH TOOLS
# ═══════════════════════════════════════════════════════════════════════

def search_court_dockets(query: str) -> dict:
    """Search for court dockets and legal filings related to a fund or case."""
    try:
        searches = [
            f"site:uscourts.gov {query}",
            f"{query} court filing docket",
            f"{query} litigation update",
        ]
        all_results = []
        seen = set()

        for sq in searches:
            encoded = urllib.parse.quote_plus(sq)
            url = f"https://www.google.com/search?q={encoded}&num=10"
            try:
                html = _fetch(url)
                urls = re.findall(r'href="/url\?q=(https?://[^&"]+)', html)
                titles = re.findall(r'<h3[^>]*>(.*?)</h3>', html, re.IGNORECASE | re.DOTALL)
                for i, u in enumerate(urls[:10]):
                    clean = urllib.parse.unquote(u)
                    if clean not in seen:
                        seen.add(clean)
                        title = re.sub(r'<[^>]+>', '', titles[i]).strip() if i < len(titles) else ""
                        all_results.append({"title": title, "url": clean})
            except:
                continue

        return {
            "query": query,
            "results_count": len(all_results),
            "results": all_results[:15],
        }
    except Exception as e:
        return {"error": str(e), "query": query}


def scrape_legal_page(url: str) -> dict:
    """Scrape a legal/court page for content and key details."""
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

        dates = re.findall(
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            text
        )
        case_numbers = re.findall(r'\b\d{1,2}[-:]\w{2,4}[-:]\d{3,6}\b', text)

        return {
            "url": url,
            "title": title,
            "content": text[:5000],
            "word_count": len(text.split()),
            "dates_found": dates[:10],
            "case_numbers": case_numbers[:10],
        }
    except Exception as e:
        return {"error": str(e), "url": url}


# ═══════════════════════════════════════════════════════════════════════
# FUND_DASH DB WRITERS
# ═══════════════════════════════════════════════════════════════════════

def ingest_article(source: str, title: str, url: str, published_date: str, keyword_hits: str) -> dict:
    """Save a discovered article to the Fund_Dash database.

    Args:
        source: Source identifier (e.g. 'doj', 'ofac', 'treasury', 'federal_register', 'court')
        title: Article title
        url: Article URL (must be unique)
        published_date: Publication date (YYYY-MM-DD format)
        keyword_hits: JSON list of matched keywords, e.g. '["iran","forfeiture","IEEPA"]'
    """
    try:
        conn = _get_db()
        run_id = _create_job_run(conn, "adk_fundtracker_article")
        ch = _content_hash(title + url)
        conn.execute(
            "INSERT OR IGNORE INTO articles "
            "(job_run_id, source, title, url, published_date, content_hash, keyword_hits) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (run_id, source, title, url, published_date, ch, keyword_hits),
        )
        conn.execute(
            "UPDATE job_runs SET status='succeeded', finished_at=datetime('now') WHERE id=?",
            (run_id,),
        )
        conn.commit()
        conn.close()
        return {"success": True, "table": "articles", "title": title}
    except Exception as e:
        return {"error": str(e)}


def ingest_case(case_name: str, category: str, stage: str, est_amount: float, docket_number: str, source_url: str, court: str, notes: str) -> dict:
    """Add or update a case in the Fund_Dash watchlist.

    Args:
        case_name: Full case name (unique identifier)
        category: Category like 'crypto', 'iran', 'syria', 'dprk', 'al_qaeda', 'hezbollah'
        stage: Pipeline stage: 'filed', 'seized', 'litigation', 'forfeited', 'liquidation', 'transfer', 'deposit', 'paid'
        est_amount: Estimated dollar value of the forfeiture
        docket_number: Court docket number
        source_url: URL to the source filing or announcement
        court: Court name (e.g. 'SDNY', 'DDC')
        notes: Any additional context
    """
    try:
        conn = _get_db()
        existing = conn.execute(
            "SELECT id, stage FROM monitored_watchlist WHERE case_name = ?",
            (case_name,),
        ).fetchone()

        if existing:
            old_stage = existing["stage"]
            conn.execute(
                "UPDATE monitored_watchlist SET category=?, stage=?, est_amount=?, "
                "docket_number=?, source_url=?, court=?, notes=?, updated_at=datetime('now') "
                "WHERE case_name=?",
                (category, stage, est_amount, docket_number, source_url, court, notes, case_name),
            )
            if old_stage != stage:
                conn.execute(
                    "INSERT INTO case_stage_history (case_name, from_stage, to_stage, source) "
                    "VALUES (?, ?, ?, 'adk_fundtracker')",
                    (case_name, old_stage, stage),
                )
            action = "updated"
        else:
            conn.execute(
                "INSERT INTO monitored_watchlist "
                "(case_name, category, stage, est_amount, docket_number, source_url, court, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (case_name, category, stage, est_amount, docket_number, source_url, court, notes),
            )
            action = "inserted"

        conn.commit()
        conn.close()
        return {"success": True, "table": "monitored_watchlist", "case_name": case_name, "action": action}
    except Exception as e:
        return {"error": str(e)}


def create_alert(rule_name: str, severity: str, message: str, evidence: str) -> dict:
    """Create an alert in the Fund_Dash dashboard.

    Args:
        rule_name: Name of the detection rule (e.g. 'new_forfeiture_filing', 'stage_change', 'deadline_approaching')
        severity: Alert severity: 'low', 'medium', 'high', or 'critical'
        message: Human-readable alert message
        evidence: JSON string with evidence details, e.g. '{"source":"DOJ","url":"...","date":"..."}'
    """
    try:
        conn = _get_db()
        conn.execute(
            "INSERT INTO alerts (rule_name, severity, message, evidence) "
            "VALUES (?, ?, ?, ?)",
            (rule_name, severity, message, evidence),
        )
        conn.commit()
        conn.close()
        return {"success": True, "table": "alerts", "severity": severity, "message": message}
    except Exception as e:
        return {"error": str(e)}


def save_tracker_report(file_path: str, content: str) -> dict:
    """Save a fund tracking report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}


def link_case_to_article(case_name: str, article_url: str) -> dict:
    """Link a case to a related article in the Fund_Dash database.

    Args:
        case_name: The case name from the watchlist
        article_url: URL of the related article
    """
    try:
        conn = _get_db()
        row = conn.execute(
            "SELECT id FROM articles WHERE url = ?", (article_url,)
        ).fetchone()
        article_id = row["id"] if row else None
        conn.execute(
            "INSERT OR IGNORE INTO case_article_links (case_name, article_url, article_id) "
            "VALUES (?, ?, ?)",
            (case_name, article_url, article_id),
        )
        conn.commit()
        conn.close()
        return {"success": True, "case_name": case_name, "article_url": article_url}
    except Exception as e:
        return {"error": str(e)}
