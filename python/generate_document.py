#!/usr/bin/env python3
"""
Generate a branded proposal or report — fonts, colors, and structure applied automatically.

Setup once:
    cp ../brand/brand.config.example.yaml ../brand/brand.config.yaml
    # Edit brand.config.yaml with your company fonts, colors, and style

Usage:
    python generate_document.py proposal --input notes.txt
    python generate_document.py report --input data.txt
    python generate_document.py proposal              # paste notes, Ctrl-D to finish
    python generate_document.py --show-brand          # verify config loaded
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# Allow imports from python/ when run from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_loader import (  # noqa: E402
    OUTPUT_DIR,
    brand_summary,
    build_brand_system_prompt,
    load_brand_config,
    validate_brand_config,
    wrap_html,
)

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-xxx"):
        print(
            "\n❌ ANTHROPIC_API_KEY is not set.\n"
            "   Copy python/.env.example to python/.env and add your key.\n"
        )
        sys.exit(1)
    from anthropic import Anthropic

    return Anthropic(api_key=api_key)


def read_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8").strip()
    print("Paste your notes below. Press Ctrl-D (Mac/Linux) or Ctrl-Z+Enter (Windows) when done:\n")
    return sys.stdin.read().strip()


def extract_html(text: str) -> str:
    """Strip markdown fences if Claude wraps HTML anyway."""
    text = text.strip()
    match = re.search(r"```(?:html)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def generate(client, config: dict, doc_type: str, user_content: str) -> str:
    system = build_brand_system_prompt(config, doc_type)
    doc_label = "proposal" if doc_type == "proposal" else "report"

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=8192,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create a {doc_label} from the following source material. "
                    f"Apply our brand automatically. Do not ask any questions.\n\n"
                    f"--- SOURCE MATERIAL ---\n{user_content}"
                ),
            }
        ],
    )
    return extract_html(response.content[0].text)


def save_output(html: str, doc_type: str, config: dict) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    company_slug = re.sub(r"[^a-z0-9]+", "-", config["company"]["name"].lower()).strip("-")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{company_slug}-{doc_type}-{timestamp}.html"
    out_path = OUTPUT_DIR / filename
    title = f"{config['company']['name']} — {doc_type.title()}"
    out_path.write_text(wrap_html(html, title, config), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate branded proposals/reports (no repeated font/color questions)"
    )
    parser.add_argument(
        "type",
        nargs="?",
        choices=["proposal", "report"],
        help="Document type to generate",
    )
    parser.add_argument("--input", "-i", help="Text file with source notes/data")
    parser.add_argument(
        "--show-brand",
        action="store_true",
        help="Print loaded brand config and exit",
    )
    args = parser.parse_args()

    config = load_brand_config()

    if args.show_brand:
        print(f"✓ {brand_summary(config)}")
        for w in validate_brand_config(config):
            print(f"  ⚠ {w}")
        return

    if not args.type:
        parser.print_help()
        sys.exit(1)

    warnings = validate_brand_config(config)
    if warnings:
        print("⚠ Brand config warnings (edit brand/brand.config.yaml):")
        for w in warnings:
            print(f"  - {w}")
        print()

    client = get_client()
    print(f"✓ {brand_summary(config)}")
    print(f"✓ Generating {args.type}…\n")

    user_content = read_input(args.input)
    if not user_content:
        print("❌ No input provided.")
        sys.exit(1)

    html = generate(client, config, args.type, user_content)
    out_path = save_output(html, args.type, config)

    print(f"✓ Saved: {out_path}")
    print("  Open in a browser → Print → Save as PDF for a final document.\n")


if __name__ == "__main__":
    main()
