#!/usr/bin/env python3
"""
Design page commands — view, export, and preview your permanent design profile.

Claude.ai's Design page saves colors/fonts/format in the UI but cannot reference
them across chats. brand/brand.config.yaml IS your design page — this tool
shows exactly what gets injected on every document.

Usage:
    python design.py show       # print design profile (what Claude receives)
    python design.py export     # save to brand/output/design-reference.txt
    python design.py preview    # HTML preview with your colors/fonts/format
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand_loader import (  # noqa: E402
    OUTPUT_DIR,
    export_design_reference,
    load_brand_config,
    render_fixed_document,
    section_specs,
    validate_brand_config,
)


def cmd_show(config: dict) -> None:
    print(export_design_reference(config))
    warnings = validate_brand_config(config)
    if warnings:
        print("\n⚠ Warnings:")
        for w in warnings:
            print(f"  - {w}")


def cmd_export(config: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "design-reference.txt"
    out.write_text(export_design_reference(config) + "\n", encoding="utf-8")
    print(f"✓ Design reference exported: {out}")
    print("  Paste into a Claude Project ONCE as backup — but use make.py for documents.")


def cmd_preview(config: dict) -> None:
    specs = section_specs("report", config)
    payload = {
        "document_title": "Design Preview — 000 Sample Boulevard",
        "file_number": "SR-PREVIEW-00",
        "review_type": "Design Preview",
        "property_address": "000 Sample Boulevard · Preview City, CA",
        "subtitle": "This page shows your saved colors, fonts, and section format.",
        "prepared_for": "Design Preview Client",
        "property_contact": "Preview Contact · 000-000-0000",
        "review_period": "Preview Period",
        "issued_date": "Preview Date",
        "sections": {
            s["slug"]: (
                f'<p><strong>Design loaded.</strong> Section <em>{s["name"]}</em> '
                f"uses your saved fonts and colors automatically.</p>"
                f'<div class="kpi-grid">'
                f'<div class="kpi-card"><div class="kpi-label">Sample KPI</div>'
                f'<div class="kpi-value">$0</div></div></div>'
                if s["slug"] == "executive_summary"
                else f"<p>Preview content for {s['name']}.</p>"
            )
            for s in specs
        },
    }
    if any(s["slug"] == "findings_exposure_recommendations" for s in specs):
        payload["sections"]["findings_exposure_recommendations"] = """
<p class="finding finding-critical">
  <span class="finding-id">CRITICAL · F-00</span>
  <div class="finding-title">Sample critical finding — uses your critical color</div>
  <div class="finding-action">ACTION › Sample action line</div>
</p>
<p class="finding finding-high">
  <span class="finding-id">HIGH · F-00</span>
  <div class="finding-title">Sample high finding — uses your high color</div>
</p>"""

    html = render_fixed_document(config, "report", payload)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUTPUT_DIR / "design-preview.html"
    out.write_text(html, encoding="utf-8")
    print(f"✓ Design preview saved: {out}")
    print("  Open in browser to verify colors, fonts, and section format match your Design page.")


def main() -> None:
    parser = argparse.ArgumentParser(description="View/export your permanent design profile")
    parser.add_argument("command", choices=["show", "export", "preview"], nargs="?", default="show")
    args = parser.parse_args()

    config = load_brand_config()
    design_id = config.get("design_id", config["company"]["name"])
    print(f"Design ID: {design_id}\n")

    if args.command == "show":
        cmd_show(config)
    elif args.command == "export":
        cmd_export(config)
    elif args.command == "preview":
        cmd_preview(config)


if __name__ == "__main__":
    main()
