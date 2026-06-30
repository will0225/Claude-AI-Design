#!/usr/bin/env python3
"""Extract colors/fonts from brand/design/*.dc.html into brand.config.yaml."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from format_guide import (  # noqa: E402
    CONFIG_PATH,
    DEFAULT_DC,
    extract_css_colors,
    load_format_guide_html,
    resolve_format_guide_path,
    validate_section_alignment,
)

BRAND_DIR = Path(__file__).resolve().parent.parent / "brand"


def main() -> None:
    dc = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DC
    if not dc.exists():
        print(f"❌ Not found: {dc}")
        sys.exit(1)

    config = {}
    if CONFIG_PATH.exists():
        config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}

    html = load_format_guide_html(dc, config)
    extracted = extract_css_colors(html)
    print(f"Extracted from {dc.name}:")
    for k, v in sorted(extracted.items()):
        print(f"  {k}: {v}")

    if not CONFIG_PATH.exists():
        print(f"\nCopy values into {CONFIG_PATH} manually.")
        return

    colors = config.setdefault("colors", {})
    alias = {
        "teal": "primary",
        "bronze": "accent",
        "ink": "text",
        "muted": "text_light",
        "cream": "surface",
        "paper": "background",
    }
    updated = False
    for src, dst in alias.items():
        if src in extracted and colors.get(dst) != extracted[src]:
            colors[dst] = extracted[src]
            colors[src] = extracted[src]
            updated = True
    for key in ("critical", "high", "medium", "positive", "border"):
        if key in extracted and colors.get(key) != extracted[key]:
            colors[key] = extracted[key]
            updated = True

    if updated:
        CONFIG_PATH.write_text(
            yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        print(f"✓ Updated {CONFIG_PATH}")
    else:
        print("No config color changes needed.")

    for w in validate_section_alignment(config, html):
        print(f"⚠ {w}")

    print("\nRun: python implement_format_guide.py  (sync CSS + HTML shell from .dc.html)")


if __name__ == "__main__":
    main()
