#!/usr/bin/env python3
"""
Apply the Claude Design format guide (.dc.html) to this repo.

Pull live file first (requires Design OAuth):
  /design-login
  export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)
  python import_design.py

Then implement:
  python implement_format_guide.py
  python implement_format_guide.py --file "../brand/design/Standard Review - 4600 Northgate.dc.html"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from format_guide import (  # noqa: E402
    CONFIG_PATH,
    FIXED_TEMPLATE_PATH,
    STYLES_PATH,
    build_fixed_template,
    extract_body_shell,
    extract_style_block,
    load_format_guide_html,
    resolve_format_guide_path,
    sync_colors_to_config,
    templatize_css,
    templatize_footer,
    templatize_header,
    validate_section_alignment,
)


def _relative_repo_path(path: Path) -> str:
    root = CONFIG_PATH.parent.parent
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def apply_format_guide(dc_path: Path | str | None = None, *, dry_run: bool = False) -> None:
    config = {}
    if CONFIG_PATH.exists():
        config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

    dc = resolve_format_guide_path(config, dc_path)
    html = load_format_guide_html(dc, config)
    css = templatize_css(extract_style_block(html))
    header_raw, footer_raw = extract_body_shell(html)
    header = templatize_header(header_raw)
    footer = templatize_footer(footer_raw)
    template = build_fixed_template(header, footer)

    if dry_run:
        print(f"Would write {STYLES_PATH} ({len(css)} bytes)")
        print(f"Would write {FIXED_TEMPLATE_PATH} ({len(template)} bytes)")
        return

    STYLES_PATH.write_text(css, encoding="utf-8")
    FIXED_TEMPLATE_PATH.write_text(template, encoding="utf-8")
    print(f"✓ CSS synced:  {STYLES_PATH}")
    print(f"✓ Shell synced: {FIXED_TEMPLATE_PATH}")

    if CONFIG_PATH.exists():
        config = sync_colors_to_config(config, html)
        config.setdefault("claude_design", {})["local_path"] = _relative_repo_path(dc)
        config.setdefault("format_guide", {})["source"] = config["claude_design"]["local_path"]
        config["format_guide"]["role"] = "Canonical Standard Review layout from Claude Design"
        CONFIG_PATH.write_text(
            yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        print(f"✓ Config synced: {CONFIG_PATH}")

    for w in validate_section_alignment(config, html):
        print(f"⚠ {w}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Implement Claude Design .dc.html as format guide")
    parser.add_argument("--file", "-f", help="Path to .dc.html (default: brand.config claude_design.local_path)")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing files")
    args = parser.parse_args()

    dc = resolve_format_guide_path(None, args.file)
    print(f"Format guide: {dc}")
    apply_format_guide(args.file or dc, dry_run=args.dry_run)
    if not args.dry_run:
        print("\nNext: python design.py preview")


if __name__ == "__main__":
    main()
