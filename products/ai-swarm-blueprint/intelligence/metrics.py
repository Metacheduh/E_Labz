"""
Free Cash Flow — Metrics Tracker
Tracks revenue, growth, content performance, and AI detection scores.
"""

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from orchestrator import PROJECT_ROOT
from typing import Optional

DB_PATH = PROJECT_ROOT / "data" / "metrics.db"
PERFORMANCE_DIR = PROJECT_ROOT / "data" / "performance"


def _get_db() -> sqlite3.Connection:
    """Get SQLite connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS daily_metrics (
            date TEXT PRIMARY KEY,
            posts_published INTEGER DEFAULT 0,
            impressions INTEGER DEFAULT 0,
            engagements INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            follower_growth INTEGER DEFAULT 0,
            follower_total INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0.0,
            sales INTEGER DEFAULT 0,
            products_created INTEGER DEFAULT 0,
            ai_detection_avg REAL DEFAULT 0.0,
            ai_detection_max REAL DEFAULT 0.0,
            humanization_retries INTEGER DEFAULT 0,
            content_flagged INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS post_metrics (
            id TEXT PRIMARY KEY,
            date TEXT,
            text TEXT,
            content_type TEXT,
            hook_type TEXT,
            post_time TEXT,
            impressions INTEGER DEFAULT 0,
            engagements INTEGER DEFAULT 0,
            engagement_rate REAL DEFAULT 0.0,
            likes INTEGER DEFAULT 0,
            replies INTEGER DEFAULT 0,
            retweets INTEGER DEFAULT 0,
            ai_detection_score REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS product_metrics (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            price REAL,
            sales INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0.0,
            refund_rate REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS config_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            config_file TEXT,
            change_description TEXT,
            old_value TEXT,
            new_value TEXT,
            trigger TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    return conn


def log_daily_metrics(metrics: dict) -> None:
    """Log today's aggregated metrics."""
    conn = _get_db()
    today = date.today().isoformat()
    
    conn.execute("""
        INSERT OR REPLACE INTO daily_metrics 
        (date, posts_published, impressions, engagements, engagement_rate,
         follower_growth, follower_total, revenue, sales, products_created,
         ai_detection_avg, ai_detection_max, humanization_retries, content_flagged)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        today,
        metrics.get("posts_published", 0),
        metrics.get("impressions", 0),
        metrics.get("engagements", 0),
        metrics.get("engagement_rate", 0.0),
        metrics.get("follower_growth", 0),
        metrics.get("follower_total", 0),
        metrics.get("revenue", 0.0),
        metrics.get("sales", 0),
        metrics.get("products_created", 0),
        metrics.get("ai_detection_avg", 0.0),
        metrics.get("ai_detection_max", 0.0),
        metrics.get("humanization_retries", 0),
        metrics.get("content_flagged", 0),
    ))
    conn.commit()
    conn.close()


def log_post_metrics(post: dict) -> None:
    """Log individual post metrics."""
    conn = _get_db()
    conn.execute("""
        INSERT OR REPLACE INTO post_metrics
        (id, date, text, content_type, hook_type, post_time,
         impressions, engagements, engagement_rate, likes, replies, retweets,
         ai_detection_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        post["id"], date.today().isoformat(),
        post.get("text", ""), post.get("content_type", ""),
        post.get("hook_type", ""), post.get("post_time", ""),
        post.get("impressions", 0), post.get("engagements", 0),
        post.get("engagement_rate", 0.0), post.get("likes", 0),
        post.get("replies", 0), post.get("retweets", 0),
        post.get("ai_detection_score", 0.0),
    ))
    conn.commit()
    conn.close()


def get_daily_metrics(day: Optional[date] = None) -> dict:
    """Get metrics for a specific day."""
    conn = _get_db()
    target = (day or date.today()).isoformat()
    row = conn.execute(
        "SELECT * FROM daily_metrics WHERE date = ?", (target,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_monthly_revenue() -> dict:
    """Get running monthly revenue totals."""
    conn = _get_db()
    today = date.today()
    month_start = today.replace(day=1).isoformat()
    
    row = conn.execute("""
        SELECT 
            SUM(revenue) as total_revenue,
            SUM(sales) as total_sales,
            COUNT(*) as days_tracked,
            AVG(revenue) as avg_daily_revenue
        FROM daily_metrics
        WHERE date >= ?
    """, (month_start,)).fetchone()
    conn.close()
    
    if not row or row["total_revenue"] is None:
        return {"total_revenue": 0, "total_sales": 0, "days_tracked": 0, "projected": 0}
    
    days_in_month = 30
    days_remaining = days_in_month - (row["days_tracked"] or 1)
    projected = (row["total_revenue"] or 0) + (row["avg_daily_revenue"] or 0) * days_remaining
    
    return {
        "total_revenue": row["total_revenue"],
        "total_sales": row["total_sales"],
        "days_tracked": row["days_tracked"],
        "avg_daily_revenue": row["avg_daily_revenue"],
        "projected_monthly": round(projected, 2),
        "target": 3000,
        "gap": max(0, 3000 - projected),
        "on_track": projected >= 2700,
    }


def get_growth_metrics(days: int = 7) -> dict:
    """Get follower growth over recent days."""
    conn = _get_db()
    rows = conn.execute("""
        SELECT date, follower_growth, follower_total
        FROM daily_metrics
        ORDER BY date DESC
        LIMIT ?
    """, (days,)).fetchall()
    conn.close()
    
    if not rows:
        return {"total_growth": 0, "avg_daily": 0, "current_followers": 0}
    
    total_growth = sum(r["follower_growth"] for r in rows)
    current = rows[0]["follower_total"] if rows else 0
    
    return {
        "total_growth": total_growth,
        "avg_daily": total_growth / max(len(rows), 1),
        "current_followers": current,
        "days_to_10k": max(0, (10000 - current) / max(total_growth / max(len(rows), 1), 1)),
    }


def save_daily_report(insights: dict, day: Optional[date] = None) -> Path:
    """Save daily review report as JSON."""
    PERFORMANCE_DIR.mkdir(parents=True, exist_ok=True)
    target = day or date.today()
    filepath = PERFORMANCE_DIR / f"daily_review_{target.isoformat()}.json"
    
    report = {
        "date": target.isoformat(),
        "generated_at": datetime.now().isoformat(),
        **insights,
    }
    
    filepath.write_text(json.dumps(report, indent=2, default=str))
    return filepath


def log_config_change(config_file: str, description: str, 
                      old_value: str, new_value: str, trigger: str = "self_learning") -> None:
    """Log a configuration change for audit trail."""
    conn = _get_db()
    conn.execute("""
        INSERT INTO config_changes (date, config_file, change_description, old_value, new_value, trigger)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date.today().isoformat(), config_file, description, old_value, new_value, trigger))
    conn.commit()
    conn.close()
