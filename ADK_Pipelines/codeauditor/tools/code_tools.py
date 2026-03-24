"""Code audit tools — read files, analyze structure. Stdlib-only."""

import os
import re
import json
from google.adk.tools import tool


@tool
def discover_codebase(directory: str, extensions: str = "py,js,html,css,ts,jsx,tsx") -> dict:
    """Auto-discover all code files in a directory."""
    try:
        path = os.path.expanduser(directory)
        if not os.path.exists(path):
            return {"error": f"Directory not found: {path}"}

        ext_list = [f".{e.strip()}" for e in extensions.split(",")]
        files = []
        total_lines = 0
        total_bytes = 0

        for root, dirs, filenames in os.walk(path):
            # Skip hidden dirs, node_modules, venv, __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.git'
            ]]
            for f in filenames:
                if any(f.endswith(ext) for ext in ext_list):
                    full = os.path.join(root, f)
                    rel = os.path.relpath(full, path)
                    size = os.path.getsize(full)
                    try:
                        with open(full, 'r', encoding='utf-8', errors='replace') as fh:
                            lines = len(fh.readlines())
                    except:
                        lines = 0
                    files.append({"path": rel, "size": size, "lines": lines})
                    total_lines += lines
                    total_bytes += size

        return {
            "directory": path,
            "file_count": len(files),
            "total_lines": total_lines,
            "total_bytes": total_bytes,
            "files": sorted(files, key=lambda x: x['lines'], reverse=True),
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def read_code_file(file_path: str) -> dict:
    """Read a code file for review."""
    try:
        path = os.path.expanduser(file_path)
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        lines = content.split('\n')
        return {
            "path": path,
            "content": content[:10000],  # Cap at 10K chars
            "lines": len(lines),
            "truncated": len(content) > 10000,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def save_audit_report(file_path: str, content: str) -> dict:
    """Save a code audit report to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
