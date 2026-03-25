"""
Free Cash Flow — Centralized Logging
Records EVERYTHING the swarm does: posts, syncs, errors, decisions, revenue.
Logs to both file and console. Rotates daily.
"""

import json
import logging
import logging.handlers
from datetime import date, datetime
from pathlib import Path
from orchestrator import PROJECT_ROOT
from typing import Optional

# ============================================================
# LOG DIRECTORIES
# ============================================================

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Sub-directories for structured logs
POSTS_LOG_DIR = LOG_DIR / "posts"
SYNCS_LOG_DIR = LOG_DIR / "syncs"
ERRORS_LOG_DIR = LOG_DIR / "errors"
DECISIONS_LOG_DIR = LOG_DIR / "decisions"

for d in [POSTS_LOG_DIR, SYNCS_LOG_DIR, ERRORS_LOG_DIR, DECISIONS_LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ============================================================
# PYTHON LOGGING SETUP
# ============================================================

def setup_logging() -> logging.Logger:
    """Set up the main swarm logger with file rotation and console output."""
    logger = logging.getLogger("swarm")
    
    if logger.handlers:
        return logger  # Already configured
    
    logger.setLevel(logging.DEBUG)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Console handler (INFO and above)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # Main log file — rotates daily, keeps 30 days
    main_log = LOG_DIR / "swarm.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        str(main_log),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error-only log file
    error_log = ERRORS_LOG_DIR / "errors.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        str(error_log),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


# Global logger
logger = setup_logging()


# ============================================================
# STRUCTURED EVENT LOGGING
# ============================================================

def _write_event(directory: Path, event_type: str, data: dict) -> Path:
    """Write a structured JSON event to the appropriate log directory."""
    today = date.today().isoformat()
    filepath = directory / f"{event_type}_{today}.jsonl"
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        **data,
    }
    
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, default=str) + "\n")
    
    return filepath


def log_post(text: str, method: str, status: str, post_type: str = "tweet",
             post_id: str = "", error: str = "") -> None:
    """Record every tweet/thread posted (or failed)."""
    data = {
        "text": text[:500],
        "text_length": len(text),
        "method": method,
        "status": status,
        "post_type": post_type,
        "post_id": post_id,
        "error": error,
    }
    _write_event(POSTS_LOG_DIR, "post", data)
    
    if status == "posted":
        logger.info(f"📤 POSTED [{method}] ({post_type}): {text[:80]}...")
    elif status == "scheduled":
        logger.info(f"📅 SCHEDULED [{method}] ({post_type}): {text[:80]}...")
    else:
        logger.warning(f"❌ POST FAILED [{method}] ({post_type}): {error}")


def log_thread(tweets: list, method: str, status: str,
               post_id: str = "", error: str = "") -> None:
    """Record thread posts."""
    data = {
        "tweets": [t[:280] for t in tweets],
        "tweet_count": len(tweets),
        "method": method,
        "status": status,
        "post_id": post_id,
        "error": error,
    }
    _write_event(POSTS_LOG_DIR, "thread", data)
    
    if status == "posted":
        logger.info(f"🧵 THREAD POSTED [{method}] ({len(tweets)} tweets): {tweets[0][:60]}...")
    else:
        logger.warning(f"❌ THREAD FAILED [{method}]: {error}")


def log_sync(source: str, data: dict) -> None:
    """Record every API sync (Twitter, Stripe, Gumroad)."""
    event_data = {
        "source": source,
        **data,
    }
    _write_event(SYNCS_LOG_DIR, "sync", event_data)
    logger.info(f"📡 SYNCED [{source}]: {json.dumps(data, default=str)[:200]}")


def log_metrics_snapshot(followers: int, posts: int, revenue: float,
                         follower_growth: int = 0) -> None:
    """Record daily metrics snapshot for trend analysis."""
    data = {
        "followers": followers,
        "total_posts": posts,
        "revenue_today": revenue,
        "follower_growth": follower_growth,
    }
    _write_event(SYNCS_LOG_DIR, "snapshot", data)
    logger.info(
        f"📊 SNAPSHOT: {followers} followers ({'+' if follower_growth >= 0 else ''}{follower_growth}), "
        f"{posts} posts, ${revenue:.2f} revenue"
    )


def log_decision(category: str, decision: str, reason: str,
                 old_value: str = "", new_value: str = "") -> None:
    """Record every self-learning decision and config change."""
    data = {
        "category": category,
        "decision": decision,
        "reason": reason,
        "old_value": old_value,
        "new_value": new_value,
    }
    _write_event(DECISIONS_LOG_DIR, "decision", data)
    logger.info(f"🧠 DECISION [{category}]: {decision} — {reason}")


def log_error(component: str, error: str, context: dict = None) -> None:
    """Record errors with full context."""
    data = {
        "component": component,
        "error": str(error),
        "context": context or {},
    }
    _write_event(ERRORS_LOG_DIR, "error", data)
    logger.error(f"💥 ERROR [{component}]: {error}")


def log_scheduler_event(event: str, job_name: str, details: str = "") -> None:
    """Record scheduler lifecycle events (start, stop, job run)."""
    data = {
        "event": event,
        "job_name": job_name,
        "details": details,
    }
    _write_event(LOG_DIR, "scheduler", data)
    logger.info(f"⏰ SCHEDULER [{event}]: {job_name} {details}")


def log_revenue(amount: float, source: str, product: str = "",
                customer_count: int = 0) -> None:
    """Record every revenue event."""
    data = {
        "amount": amount,
        "source": source,
        "product": product,
        "customer_count": customer_count,
    }
    _write_event(LOG_DIR, "revenue", data)
    if amount > 0:
        logger.info(f"💰 REVENUE: ${amount:.2f} from {source} ({product})")


# ============================================================
# LOG READERS (for self-learning analysis)
# ============================================================

def get_todays_posts() -> list[dict]:
    """Read all posts logged today."""
    today = date.today().isoformat()
    filepath = POSTS_LOG_DIR / f"post_{today}.jsonl"
    if not filepath.exists():
        return []
    
    posts = []
    with open(filepath, "r") as f:
        for line in f:
            try:
                posts.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return posts


def get_todays_errors() -> list[dict]:
    """Read all errors logged today."""
    today = date.today().isoformat()
    filepath = ERRORS_LOG_DIR / f"error_{today}.jsonl"
    if not filepath.exists():
        return []
    
    errors = []
    with open(filepath, "r") as f:
        for line in f:
            try:
                errors.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    return errors


def get_post_count_today() -> int:
    """Quick count of posts made today."""
    return len([p for p in get_todays_posts() if p.get("status") == "posted"])


def get_daily_summary(target_date: Optional[date] = None) -> dict:
    """Generate a summary of all activity for a given day."""
    day = (target_date or date.today()).isoformat()
    
    # Count posts
    post_file = POSTS_LOG_DIR / f"post_{day}.jsonl"
    thread_file = POSTS_LOG_DIR / f"thread_{day}.jsonl"
    error_file = ERRORS_LOG_DIR / f"error_{day}.jsonl"
    sync_file = SYNCS_LOG_DIR / f"sync_{day}.jsonl"
    decision_file = DECISIONS_LOG_DIR / f"decision_{day}.jsonl"
    
    def count_lines(fp):
        if not fp.exists():
            return 0
        return sum(1 for _ in open(fp))
    
    return {
        "date": day,
        "posts": count_lines(post_file),
        "threads": count_lines(thread_file),
        "errors": count_lines(error_file),
        "syncs": count_lines(sync_file),
        "decisions": count_lines(decision_file),
    }
