"""Email tools — generate sequences, check compliance, save campaigns. Stdlib-only."""

import os
import json
import re
from google.adk.tools import tool


@tool
def save_email_sequence(file_path: str, content: str) -> dict:
    """Save an email sequence to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}


@tool
def check_compliance(email_text: str) -> dict:
    """Check an email for SEC/FINRA compliance issues and CAN-SPAM compliance."""
    issues = []
    warnings = []

    # CAN-SPAM checks
    if not re.search(r'unsubscribe', email_text, re.IGNORECASE):
        issues.append("Missing unsubscribe link (CAN-SPAM requirement)")
    if not re.search(r'physical.{0,20}address|mailing.{0,20}address|\d+\s+\w+\s+(street|st|ave|avenue|blvd|rd|road)', email_text, re.IGNORECASE):
        warnings.append("Consider adding physical mailing address (CAN-SPAM)")

    # SEC/FINRA checks for financial services
    guarantee_words = re.findall(r'\b(guarantee|guaranteed|risk.?free|no.?risk|certain return|assured|promise)\b', email_text, re.IGNORECASE)
    if guarantee_words:
        issues.append(f"SEC violation: performance guarantees found ({', '.join(guarantee_words)})")

    # Past performance
    if re.search(r'\b(past performance|historical returns?|we.{0,20}earned|we.{0,20}returned|our.{0,20}track record)\b', email_text, re.IGNORECASE):
        warnings.append("Past performance claims require 'Past performance does not guarantee future results' disclaimer")

    # Urgency/pressure tactics
    pressure = re.findall(r'\b(act now|limited time|don.t miss|last chance|expires|urgent|must act)\b', email_text, re.IGNORECASE)
    if pressure:
        warnings.append(f"High-pressure language detected ({', '.join(pressure)}) — may trigger spam filters")

    # All caps
    caps_words = re.findall(r'\b[A-Z]{4,}\b', email_text)
    if len(caps_words) > 3:
        warnings.append(f"Excessive ALL CAPS ({len(caps_words)} words) — spam filter risk")

    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "issue_count": len(issues),
        "warning_count": len(warnings),
    }


@tool
def save_report(file_path: str, content: str) -> dict:
    """Save a campaign report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
