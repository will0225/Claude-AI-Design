#!/usr/bin/env python3
"""
Drop downloaded info in brand/inbox/, run one command, get the same template every time.

  python make.py proposal     # newest inbox file → fixed proposal layout
  python make.py report       # newest inbox file → fixed report layout
  python make.py proposal --file ~/Downloads/notes.txt
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
sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_loader import (  # noqa: E402
    INBOX_DIR,
    OUTPUT_DIR,
    archive_inbox_file,
    brand_summary,
    build_json_system_prompt,
    latest_inbox_file,
    load_brand_config,
    parse_json_response,
    read_source_file,
    render_fixed_document,
    validate_brand_config,
)

DEFAULT_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def get_client():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key.startswith("sk-ant-api03-xxx"):
        print("\n❌ ANTHROPIC_API_KEY is not set. Copy python/.env.example to python/.env\n")
        sys.exit(1)
    from anthropic import Anthropic

    return Anthropic(api_key=api_key)


def resolve_input(path: str | None, from_inbox: bool) -> Path:
    if path:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            print(f"❌ File not found: {p}")
            sys.exit(1)
        return p

    if from_inbox:
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        latest = latest_inbox_file()
        if not latest:
            print(
                f"\n❌ No files in {INBOX_DIR}\n"
                "   Drop a .txt, .csv, or .md file there, then run again.\n"
                "   See brand/inbox/README.txt\n"
            )
            sys.exit(1)
        print(f"📥 Using inbox file: {latest.name}\n")
        return latest

    print("❌ Provide --file or use default inbox (drop files in brand/inbox/)")
    sys.exit(1)


def generate_content(client, config: dict, doc_type: str, source_text: str) -> dict:
    system = build_json_system_prompt(config, doc_type)
    doc_label = doc_type

    response = client.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=8192,
        system=system,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Fill the {doc_label} template from this downloaded/source material. "
                    f"Use the fixed section keys. Do not ask questions.\n\n"
                    f"--- SOURCE MATERIAL ---\n{source_text}"
                ),
            }
        ],
    )
    return parse_json_response(response.content[0].text)


def save_output(html: str, doc_type: str, config: dict, source_name: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    company_slug = re.sub(r"[^a-z0-9]+", "-", config["company"]["name"].lower()).strip("-")
    stem = Path(source_name).stem[:40]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{company_slug}-{doc_type}-{stem}-{timestamp}.html"
    out_path = OUTPUT_DIR / filename
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download → inbox → same proposal or report template every time"
    )
    parser.add_argument("type", choices=["proposal", "report"], help="Which fixed template to use")
    parser.add_argument("--file", "-f", help="Specific source file (default: newest in brand/inbox/)")
    parser.add_argument("--keep-inbox", action="store_true", help="Do not move source file to inbox/done/")
    args = parser.parse_args()

    config = load_brand_config()
    for w in validate_brand_config(config):
        print(f"⚠ {w}")

    client = get_client()
    print(f"✓ {brand_summary(config)}")
    print(f"✓ Building fixed {args.type} template…\n")

    source_path = resolve_input(args.file, from_inbox=not args.file)
    source_text = read_source_file(source_path)
    if not source_text:
        print("❌ Source file is empty.")
        sys.exit(1)

    payload = generate_content(client, config, args.type, source_text)
    html = render_fixed_document(config, args.type, payload)
    out_path = save_output(html, args.type, config, source_path.name)

    if not args.file and not args.keep_inbox and source_path.parent.resolve() == INBOX_DIR.resolve():
        archive_inbox_file(source_path)
        print(f"📦 Moved source to inbox/done/{source_path.name}")

    print(f"✓ Saved: {out_path}")
    print("  Same layout every time — open in browser → Print → Save as PDF\n")


if __name__ == "__main__":
    main()
