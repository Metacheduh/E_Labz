"""Product launch tools — file generation, packaging, saving. Stdlib-only."""

import os
import json
from google.adk.tools import tool


@tool
def save_product_file(file_path: str, content: str) -> dict:
    """Save any product file (code, docs, copy, config) to disk."""
    try:
        path = os.path.expanduser(file_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": path, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}


@tool
def list_product_files(directory: str) -> dict:
    """List all files in a product directory."""
    try:
        path = os.path.expanduser(directory)
        if not os.path.exists(path):
            return {"error": f"Directory not found: {path}"}
        files = []
        for root, dirs, filenames in os.walk(path):
            for f in filenames:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, path)
                files.append({"path": rel, "size": os.path.getsize(full)})
        return {"directory": path, "file_count": len(files), "files": files}
    except Exception as e:
        return {"error": str(e)}


@tool
def read_file(file_path: str) -> dict:
    """Read a file's content."""
    try:
        path = os.path.expanduser(file_path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"path": path, "content": content, "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}
