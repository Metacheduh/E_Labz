"""Output tools for site audit — save reports and CSV results."""

import csv
import os
import json
from google.adk.tools import tool


@tool
def save_audit_csv(file_path: str, rows: list) -> dict:
    """Save audit results to CSV. Each row is a dict with page-level scores."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not rows:
            return {"error": "No rows to save"}
        headers = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return {"success": True, "path": path, "rows_saved": len(rows)}
    except Exception as e:
        return {"error": str(e)}


@tool
def save_report(file_path: str, content: str) -> dict:
    """Save a markdown or text report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
