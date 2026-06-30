"""
Minimal client for Anthropic's official claude_design MCP server.

Requires Design OAuth token from `/design-login` in Claude Code (NOT the API key).

  export DESIGN_OAUTH_TOKEN="..."   # from ~/.claude/.credentials.json → designOauth.accessToken
  python import_design.py --project 575aeb46-b224-4fc6-9f4d-29bacdbcf962 --file "Standard Review - 4600 Northgate.dc.html"
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

MCP_URL = "https://api.anthropic.com/v1/design/mcp"


def _post(payload: dict, token: str) -> dict:
    req = urllib.request.Request(
        MCP_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "claude-design-import/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body[:500]}")
        if e.code in (401, 404):
            print(
                "\nDesign MCP auth failed. On your machine:\n"
                "  1. Open Claude Code\n"
                "  2. Run /design-login\n"
                "  3. export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)\n"
                "  4. Re-run this import\n"
            )
        sys.exit(1)


def get_token() -> str:
    token = os.getenv("DESIGN_OAUTH_TOKEN", "").strip()
    if not token:
        print(
            "\n❌ DESIGN_OAUTH_TOKEN not set.\n"
            "   Run /design-login in Claude Code, then:\n"
            "   export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)\n"
        )
        sys.exit(1)
    return token


def mcp_call(method: str, params: dict | None = None, *, req_id: int = 1) -> dict:
    token = get_token()
    payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}}
    result = _post(payload, token)
    if "error" in result:
        print(f"MCP error: {result['error']}")
        sys.exit(1)
    return result.get("result", {})


def initialize() -> dict:
    return mcp_call(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "hvac-design-import", "version": "1.0.0"},
        },
    )


def list_tools() -> list[dict]:
    result = mcp_call("tools/list", req_id=2)
    return result.get("tools", [])


def call_tool(name: str, arguments: dict) -> dict:
    return mcp_call("tools/call", {"name": name, "arguments": arguments}, req_id=3)


if __name__ == "__main__":
    print("Initializing claude_design MCP…")
    info = initialize()
    print(json.dumps(info, indent=2))
    print("\nTools:")
    for t in list_tools():
        print(f"  - {t.get('name')}: {t.get('description', '')[:80]}")
