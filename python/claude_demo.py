#!/usr/bin/env python3
"""
Claude API demo script.

Usage:
    cp .env.example .env          # then add your API key
    pip install -r requirements.txt
    python claude_demo.py         # run basic smoke test
    python claude_demo.py --all   # run all three example prompts
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env from this directory (works even if you run from repo root)
load_dotenv(Path(__file__).resolve().parent / ".env")

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def get_client():
    """Create an Anthropic client, failing fast if the API key is missing."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-xxx"):
        print(
            "\n❌ ANTHROPIC_API_KEY is not set.\n"
            "   1. Copy python/.env.example to python/.env\n"
            "   2. Add your key from https://console.anthropic.com/settings/keys\n"
        )
        sys.exit(1)

    from anthropic import Anthropic

    return Anthropic(api_key=api_key)


def ask(client, *, system: str, user: str, max_tokens: int = 1024) -> str:
    """Send one user message (with optional system prompt) and return text."""
    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text


def smoke_test(client) -> None:
    """Minimal call to verify the API key and network connectivity."""
    print("=" * 60)
    print("SMOKE TEST — basic Claude response")
    print("=" * 60)
    reply = ask(
        client,
        system="You are a helpful assistant. Reply in one short sentence.",
        user="Say hello and confirm you received this message.",
    )
    print(f"\nClaude ({DEFAULT_MODEL}):\n{reply}\n")


def prompt_discovery(client) -> None:
    """Example 1: Discovery call notes → client-ready proposal outline."""
    print("=" * 60)
    print("EXAMPLE 1 — Discovery call → proposal outline")
    print("=" * 60)
    notes = """
    Discovery call 2026-06-30 with Jordan (COO), Brightline Marketing, ~12 staff.
    Pain: client reporting takes 6+ hrs/week; proposal drafts inconsistent across team.
    Tried ChatGPT Team — outputs vary too much, hard to reuse prompts.
    Wants Claude wired into daily workflow; open to Python script or Zapier if simpler.
    Budget: $5–8k for setup + training. Timeline: live in 3 weeks before Q3 campaigns.
    Must loop in IT on API/data policy. Competitor quote pending from another vendor.
    Jordan asked for a scope doc by Friday; decision by next Tuesday.
    """
    reply = ask(
        client,
        system=(
            "You are a consultant turning discovery call notes into a proposal outline. "
            "Output exactly four sections: Client Snapshot (3 bullets), Stated Needs, "
            "Proposed Scope (bulleted deliverables tagged S/M/L for effort), "
            "Next Steps (owner + date). Use client-ready language; avoid internal jargon."
        ),
        user=f"Discovery call notes:\n{notes.strip()}",
        max_tokens=1536,
    )
    print(f"\nClaude:\n{reply}\n")


def prompt_status_email(client) -> None:
    """Example 2: Recurring weekly client status update."""
    print("=" * 60)
    print("EXAMPLE 2 — Weekly client status update")
    print("=" * 60)
    reply = ask(
        client,
        system=(
            "You write weekly project status emails for consulting clients. "
            "Structure exactly: Subject line, Progress This Week (3 bullets), "
            "Blockers (one bullet or 'None'), Plan for Next Week (3 bullets), "
            "Ask of Client (one sentence or 'None'). "
            "Tone: confident and transparent. Body under 150 words. No exclamation marks."
        ),
        user=(
            "Client: Northwind Digital. Project: Claude workflow setup.\n"
            "This week: completed API setup and demo script; drafted three tailored prompts; "
            "shared setup guide for their team.\n"
            "Blocker: waiting on their legal team to approve API usage policy.\n"
            "Next week: handoff screen share; customize prompts for client reporting workflow; "
            "document Zapier option for non-technical staff.\n"
            "Ask: confirm handoff call slot (Tue or Wed afternoon)."
        ),
    )
    print(f"\nClaude:\n{reply}\n")


def prompt_research_brief(client) -> None:
    """Example 3: Messy research notes → executive brief."""
    print("=" * 60)
    print("EXAMPLE 3 — Research notes → executive brief")
    print("=" * 60)
    notes = """
    Research re: AI tooling for Brightline's workflow automation RFP response.
    - Claude API: strong long-document handling; official Python + Node SDKs.
    - OpenAI GPT-4o: larger plugin ecosystem; team already has some ChatGPT seats.
    - Anthropic API data: not used for training by default — important for client data.
    - Zapier / Make: both have Anthropic connectors; good for marketing ops, ~$20+/mo.
    - Pricing: Haiku cheapest/high volume; Sonnet best balance; Opus for heavy reasoning.
    - Claude.ai Projects: may suffice for non-technical staff without API spend.
    - [UNVERIFIED] Gemini Enterprise may integrate better with Google Workspace.
    - Client priority: repeatable prompts, clear handoff docs, minimal engineering lift.
    """
    reply = ask(
        client,
        system=(
            "You synthesize raw research notes into an executive brief for a client RFP. "
            "Output: Headline (one sentence), Key Findings (5 bullets), "
            "Implications for This Client (3 bullets), Recommended Actions (numbered, max 3). "
            "Preserve [UNVERIFIED] tags on any unconfirmed claims."
        ),
        user=f"Research notes:\n{notes.strip()}",
        max_tokens=1536,
    )
    print(f"\nClaude:\n{reply}\n")


EXAMPLES = {
    "discovery": prompt_discovery,
    "status-email": prompt_status_email,
    "research-brief": prompt_research_brief,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude API demo")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run smoke test plus all three example prompts",
    )
    parser.add_argument(
        "--example",
        choices=list(EXAMPLES.keys()),
        help="Run a single example prompt",
    )
    args = parser.parse_args()

    client = get_client()
    print(f"✓ API key loaded. Model: {DEFAULT_MODEL}\n")

    smoke_test(client)

    if args.all:
        for fn in EXAMPLES.values():
            fn(client)
    elif args.example:
        EXAMPLES[args.example](client)
    else:
        print("Tip: run with --all to see three tailored example prompts.")
        print("     python claude_demo.py --example discovery\n")


if __name__ == "__main__":
    main()
