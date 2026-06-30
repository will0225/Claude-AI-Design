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


def prompt_summarize(client) -> None:
    """Example 1: Structured summarization with explicit output format."""
    print("=" * 60)
    print("EXAMPLE 1 — Meeting notes → action items")
    print("=" * 60)
    notes = """
    Team sync 2026-06-30: Sarah said the landing page copy is overdue.
    Mike will deploy the staging build by Friday. We need legal review on
    the privacy policy before launch. Budget approved for one contractor
    through Q3. Next sync Tuesday 10am.
    """
    reply = ask(
        client,
        system=(
            "You extract action items from meeting notes. "
            "Output exactly three sections: Summary (2 sentences), "
            "Action Items (bulleted, owner + deadline), Open Questions."
        ),
        user=f"Meeting notes:\n{notes.strip()}",
    )
    print(f"\nClaude:\n{reply}\n")


def prompt_draft_email(client) -> None:
    """Example 2: Tone-controlled drafting with constraints."""
    print("=" * 60)
    print("EXAMPLE 2 — Draft a professional email")
    print("=" * 60)
    reply = ask(
        client,
        system=(
            "You write concise business email drafts. "
            "Use a warm but professional tone. "
            "Never use exclamation marks. Keep under 120 words."
        ),
        user=(
            "Draft an email to a client named Alex explaining that their "
            "project delivery will slip by one week due to an unexpected "
            "third-party API change. Offer a brief call to walk through options."
        ),
    )
    print(f"\nClaude:\n{reply}\n")


def prompt_code_review(client) -> None:
    """Example 3: Focused code review with severity labels."""
    print("=" * 60)
    print("EXAMPLE 3 — Code review snippet")
    print("=" * 60)
    code = '''
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
'''
    reply = ask(
        client,
        system=(
            "You are a senior engineer doing code review. "
            "List issues as: [CRITICAL], [WARNING], or [SUGGESTION]. "
            "For each issue, give a one-line fix. Max 5 items."
        ),
        user=f"Review this Python function:\n```python{code}\n```",
        max_tokens=512,
    )
    print(f"\nClaude:\n{reply}\n")


EXAMPLES = {
    "summarize": prompt_summarize,
    "email": prompt_draft_email,
    "code-review": prompt_code_review,
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
        print("     python claude_demo.py --example summarize\n")


if __name__ == "__main__":
    main()
