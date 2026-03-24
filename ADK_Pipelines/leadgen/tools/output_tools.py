"""Output tools — write leads to CSV, save reports, export data."""

import csv
import os
import json
from google.adk.tools import tool


@tool
def save_leads_csv(file_path: str, leads: list) -> dict:
    """Save a list of leads to a CSV file. Each lead should be a dict with keys
    like: company, url, industry, email, score, outreach_email."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        if not leads:
            return {"error": "No leads to save"}

        headers = list(leads[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for lead in leads:
                writer.writerow(lead)

        return {"success": True, "path": path, "leads_saved": len(leads)}
    except Exception as e:
        return {"error": str(e), "path": file_path}


@tool
def save_report(file_path: str, content: str) -> dict:
    """Save a text report (markdown, txt, etc.) to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes_written": len(content)}
    except Exception as e:
        return {"error": str(e), "path": file_path}


@tool
def read_file(file_path: str) -> dict:
    """Read a file from disk."""
    try:
        path = os.path.expanduser(file_path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"path": path, "content": content[:50000]}
    except Exception as e:
        return {"error": str(e), "path": file_path}
