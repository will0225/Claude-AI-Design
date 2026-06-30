#!/usr/bin/env python3
"""
Import a file from Claude Design via the official claude_design MCP.

Project: https://claude.ai/design/p/575aeb46-b224-4fc6-9f4d-29bacdbcf962
File:    Standard Review - 4600 Northgate.dc.html

Setup (on your machine with Claude Code):
  /design-login
  export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)

Usage:
  python import_design.py
  python import_design.py --project 575aeb46-b224-4fc6-9f4d-29bacdbcf962 --file "Standard Review - 4600 Northgate.dc.html"
  python import_design.py --list-tools
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from design_mcp_client import call_tool, initialize, list_tools  # noqa: E402

BRAND_DESIGN_DIR = Path(__file__).resolve().parent.parent / "brand" / "design"
DEFAULT_PROJECT = "575aeb46-b224-4fc6-9f4d-29bacdbcf962"
DEFAULT_FILE = "Standard Review - 4600 Northgate.dc.html"

# Tool names observed in claude_design MCP (may vary by version)
FETCH_TOOLS = [
    "get_claude_design_prompt",
    "fetch_design_file",
    "read_design_file",
    "get_design_file",
]


def try_import(project_id: str, filename: str) -> str | None:
    """Attempt known MCP tool patterns; return HTML content if successful."""
    tools = {t["name"]: t for t in list_tools()}
    print(f"Available MCP tools: {', '.join(tools.keys())}\n")

    attempts = [
        ("get_claude_design_prompt", {"url": f"https://claude.ai/design/p/{project_id}?file={filename}"}),
        ("fetch_design_file", {"projectId": project_id, "path": filename}),
        ("read_design_file", {"projectId": project_id, "file": filename}),
        ("get_design_file", {"project_id": project_id, "file_name": filename}),
    ]

    for tool_name, args in attempts:
        if tool_name not in tools:
            continue
        print(f"Trying {tool_name}…")
        result = call_tool(tool_name, args)
        content = _extract_content(result)
        if content:
            return content

    # Generic: try any tool whose name contains 'design' or 'file'
    for name, meta in tools.items():
        if any(k in name.lower() for k in ("file", "fetch", "read", "prompt")):
            print(f"Trying {name} with project/file args…")
            for args in [
                {"projectId": project_id, "path": filename},
                {"project_id": project_id, "file": filename},
                {"url": f"https://claude.ai/design/p/{project_id}?file={filename}"},
            ]:
                try:
                    result = call_tool(name, args)
                    content = _extract_content(result)
                    if content and ("<" in content or len(content) > 200):
                        return content
                except SystemExit:
                    raise
                except Exception:
                    continue
    return None


def _extract_content(result: dict) -> str | None:
    if isinstance(result, str):
        return result
    if "content" in result:
        blocks = result["content"]
        if isinstance(blocks, list):
            texts = [b.get("text", "") for b in blocks if isinstance(b, dict)]
            return "\n".join(texts) if texts else None
        return str(blocks)
    for key in ("html", "text", "data", "file", "body"):
        if key in result and result[key]:
            return str(result[key])
    return json.dumps(result) if result else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Claude Design file via MCP")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--file", default=DEFAULT_FILE)
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--out", help="Output path (default: brand/design/<filename>)")
    args = parser.parse_args()

    initialize()

    if args.list_tools:
        for t in list_tools():
            print(json.dumps(t, indent=2))
        return

    print(f"Importing project {args.project}")
    print(f"File: {args.file}\n")

    content = try_import(args.project, args.file)
    if not content:
        print(
            "❌ Could not import via MCP.\n"
            "   Ensure DESIGN_OAUTH_TOKEN is set (run /design-login in Claude Code).\n"
            "   Fallback: use the committed reference at brand/design/Standard Review - 4600 Northgate.dc.html\n"
        )
        sys.exit(1)

    BRAND_DESIGN_DIR.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else BRAND_DESIGN_DIR / args.file
    out.write_text(content, encoding="utf-8")
    print(f"✓ Saved: {out}")
    print("  Run: python sync_design.py  (to extract colors/fonts into brand.config.yaml)")


if __name__ == "__main__":
    main()
