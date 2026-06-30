"""
Load and implement the Claude Design format guide (.dc.html).

The committed reference at brand/design/Standard Review - 4600 Northgate.dc.html
is the canonical Standard Review layout. import_design.py pulls live updates via
claude_design MCP; this module applies the file to templates and config.
"""

from __future__ import annotations

import html as html_lib
import re
from pathlib import Path

import yaml

BRAND_DIR = Path(__file__).resolve().parent.parent / "brand"
DEFAULT_DC = BRAND_DIR / "design" / "Standard Review - 4600 Northgate.dc.html"
STYLES_PATH = BRAND_DIR / "styles" / "document.css"
FIXED_TEMPLATE_PATH = BRAND_DIR / "templates" / "fixed_document.html"
CONFIG_PATH = BRAND_DIR / "brand.config.yaml"

# Map :root CSS variable names → brand_loader template tokens
CSS_VAR_TO_TOKEN = {
    "--color-teal": "{{PRIMARY}}",
    "--color-bronze": "{{ACCENT}}",
    "--color-ink": "{{TEXT}}",
    "--color-muted": "{{TEXT_LIGHT}}",
    "--color-cream": "{{SURFACE}}",
    "--color-paper": "{{BACKGROUND}}",
    "--color-critical": "{{CRITICAL}}",
    "--color-high": "{{HIGH}}",
    "--color-medium": "{{MEDIUM}}",
    "--color-positive": "{{POSITIVE}}",
    "--color-border": "{{BORDER}}",
}

FONT_IMPORT_TOKENS = [
    ("Newsreader", "{{HEADING_FONT_URL}}"),
    ("Public+Sans", "{{BODY_FONT_URL}}"),
    ("IBM+Plex+Mono", "{{MONO_FONT_URL}}"),
]

FONT_FAMILY_TOKENS = {
    "Newsreader": "{{HEADING_FONT}}",
    "Public Sans": "{{BODY_FONT}}",
    "IBM Plex Mono": "{{MONO_FONT}}",
}

# Utilities used in the Northgate format guide but not always in :root
EXTRA_CSS = """
/* ---- Format guide utilities (Standard Review) ---- */
header.doc-header p.file-number {
  font-family: var(--font-mono);
  font-size: 9pt;
  font-weight: 500;
  color: var(--color-muted);
  margin: 0.25rem 0 0;
}

.cover-meta .meta-block { display: flex; flex-direction: column; gap: 0.15rem; }

.note-text {
  font-size: 10pt;
  color: var(--color-muted);
  margin: 0.5rem 0;
}

table.data-table th.amount,
table.data-table td.amount,
th.amount, td.amount {
  text-align: right;
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

tr.total-row td {
  font-weight: 700;
  border-top: 1.5px solid var(--color-border);
}

.finding-body {
  font-size: 10pt;
  margin: 0.35rem 0;
  line-height: 1.55;
}

.pm-job {
  font-family: var(--font-mono);
  font-size: 8pt;
  color: var(--color-muted);
  margin-top: 0.25rem;
}
"""


def resolve_format_guide_path(config: dict | None = None, override: Path | str | None = None) -> Path:
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = BRAND_DIR.parent / p
        return p
    if config:
        cd = config.get("claude_design", {})
        local = cd.get("local_path") or cd.get("format_guide")
        if local:
            p = Path(local)
            return p if p.is_absolute() else BRAND_DIR.parent / p
    return DEFAULT_DC


def load_format_guide_html(path: Path | None = None, config: dict | None = None) -> str:
    dc = path or resolve_format_guide_path(config)
    if not dc.exists():
        raise FileNotFoundError(f"Format guide not found: {dc}")
    return dc.read_text(encoding="utf-8")


def extract_style_block(html: str) -> str:
    m = re.search(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    if not m:
        raise ValueError("No <style> block found in format guide")
    return m.group(1).strip()


def extract_body_shell(html: str) -> tuple[str, str]:
    """Return (header_html, footer_html) from the format guide body."""
    body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL | re.IGNORECASE)
    if not body_m:
        raise ValueError("No <body> found in format guide")
    body = body_m.group(1)

    header_m = re.search(
        r"(<header class=\"doc-header\">.*?</header>)",
        body,
        re.DOTALL,
    )
    footer_m = re.search(
        r"(<footer class=\"doc-footer\">.*?</footer>)",
        body,
        re.DOTALL,
    )
    if not header_m or not footer_m:
        raise ValueError("Format guide missing doc-header or doc-footer")
    return header_m.group(1).strip(), footer_m.group(1).strip()


def extract_sections(html: str) -> list[dict]:
    """Parse section ids, numbers, and titles from the format guide."""
    sections = []
    pattern = re.compile(
        r'<section class="doc-section" id="([^"]+)">\s*'
        r'<h2>\s*<span class="section-num">(\d+)</span>\s*([^<]+?)\s*</h2>',
        re.DOTALL,
    )
    for sid, num, name in pattern.findall(html):
        sections.append({"id": sid, "number": num, "name": html_lib.unescape(name.strip())})
    return sections


def extract_css_colors(html: str) -> dict[str, str]:
    """Read :root --color-* values from the format guide."""
    colors: dict[str, str] = {}
    style = extract_style_block(html)
    for var in CSS_VAR_TO_TOKEN:
        short = var.replace("--color-", "")
        m = re.search(rf"{re.escape(var)}\s*:\s*(#[0-9a-fA-F]{{3,8}})", style)
        if m:
            colors[short] = m.group(1)
    return colors


def templatize_css(css: str) -> str:
    """Convert hardcoded :root values and font URLs to brand_loader placeholders."""
    out = css
    for var, token in CSS_VAR_TO_TOKEN.items():
        out = re.sub(
            rf"({re.escape(var)}\s*:\s*)(#[0-9a-fA-F]{{3,8}})",
            rf"\1{token}",
            out,
        )
    for _family, token in FONT_IMPORT_TOKENS:
        out = re.sub(
            r'@import url\("https://fonts\.googleapis\.com/css2\?family=[^"]+"\);',
            f'@import url("{token}");',
            out,
            count=1,
        )
    for family, token in FONT_FAMILY_TOKENS.items():
        out = out.replace(f'"{family}"', f'"{token}"')
    if not out.startswith("/*"):
        out = "/* HAM Report Style Guide v1 — synced from Claude Design format guide */\n\n" + out
    if EXTRA_CSS.strip() not in out:
        out = out.rstrip() + "\n" + EXTRA_CSS
    return out


def templatize_header(header: str) -> str:
    """Replace Northgate sample content with fixed template tokens."""
    meta_blocks = [
        ("Prepared for", "{{PREPARED_FOR}}"),
        ("Property mgr", "{{PROPERTY_CONTACT}}"),
        ("Review period", "{{REVIEW_PERIOD}}"),
        ("Issued", "{{ISSUED_DATE}}"),
        ("Review type", "{{REVIEW_TYPE}}"),
        ("Prepared by", "{{PREPARED_BY}}"),
    ]
    meta_html = "\n".join(
        f"""      <div class="meta-block">
        <span class="meta-label">{label}</span>
        <span class="meta-value">{token}</span>
      </div>"""
        for label, token in meta_blocks
    )
    return f"""<header class="doc-header">
    <p class="confidential">{{{{CONFIDENTIAL_LABEL}}}}</p>
    <p class="doc-type">{{{{DOC_TYPE_LABEL}}}}</p>
    <h1 class="company-name">{{{{COMPANY_NAME}}}}</h1>
    <p class="file-number">File No. {{{{FILE_NUMBER}}}}</p>
    <p class="property-address">{{{{PROPERTY_ADDRESS}}}}</p>
    <p class="subtitle">{{{{SUBTITLE}}}}</p>

    <div class="cover-meta">
{meta_html}
    </div>
  </header>"""


def templatize_footer(footer: str) -> str:
    f = footer
    f = re.sub(
        r'<p class="footer-disclaimer">.*?</p>',
        '<p class="footer-disclaimer">{{FOOTER_DISCLAIMER}}</p>',
        f,
        count=1,
        flags=re.DOTALL,
    )
    f = re.sub(
        r'<p class="footer-contact">.*?</p>',
        (
            '<p class="footer-contact">{{CONTACT_EMAIL}} &nbsp;|&nbsp; '
            "{{CONTACT_PHONE}} &nbsp;|&nbsp; {{LICENSE}}</p>"
        ),
        f,
        count=1,
        flags=re.DOTALL,
    )
    return f


def build_fixed_template(header: str, footer: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{{{TITLE}}}}</title>
  <style>
{{{{STYLES}}}}
  </style>
</head>
<body>
  {header}

  <main class="doc-body">
{{{{SECTIONS}}}}
  </main>

  {footer}
</body>
</html>
"""


def format_guide_prompt_excerpt(html: str) -> str:
    """HTML patterns Claude must follow — derived from the live format guide."""
    sections = extract_sections(html)
    section_lines = "\n".join(
        f"  - {s['number']} {s['name']} (id: {s['id']})" for s in sections
    )
    return f"""FORMAT GUIDE: Standard Review - 4600 Northgate.dc.html (Claude Design)
Use these exact class names and structures inside section HTML fragments:

COVER (template handles — do not repeat in JSON):
  .doc-header, .file-number, .property-address, .cover-meta with .meta-block

SECTIONS (fixed order):
{section_lines}

EXECUTIVE SUMMARY:
  .kpi-grid > .kpi-card with .kpi-label, .kpi-value (mono for $), .kpi-sub

TABLES:
  table.data-table, thead teal, zebra tbody, th.amount / td.amount for numerics
  tr.total-row for subtotals, p.note-text for footnotes

FINDINGS (section 05):
  div.finding.finding-critical|finding-high|finding-medium
  .finding-id (e.g. "Critical · F-01"), .finding-title, .finding-body, .finding-action
  ACTION lines start with "ACTION ›"

VENDOR PM AUDIT:
  .flag-critical, .flag-high inline; .pm-job for work order refs

COMFORT:
  .timeline with .visit-date in mono

CALLOUTS:
  .key-finding-callout, .recommendation-box, .caveat-box, .data-gaps

Severity colors ONLY on findings/ratings — never decorative."""


def sync_colors_to_config(config: dict, html: str) -> dict:
    extracted = extract_css_colors(html)
    alias_map = {
        "teal": "primary",
        "bronze": "accent",
        "ink": "text",
        "muted": "text_light",
        "cream": "surface",
        "paper": "background",
    }
    colors = config.setdefault("colors", {})
    for src, dst in alias_map.items():
        if src in extracted:
            colors[dst] = extracted[src]
            colors[src] = extracted[src]
    for key in ("critical", "high", "medium", "positive", "border"):
        if key in extracted:
            colors[key] = extracted[key]
    return config


def validate_section_alignment(config: dict, html: str) -> list[str]:
    """Warn if brand.config sections differ from format guide."""
    warnings = []
    guide_sections = extract_sections(html)
    config_sections = config.get("report", {}).get("sections", [])
    for i, (guide, cfg) in enumerate(zip(guide_sections, config_sections)):
        if guide["name"] != cfg.get("name"):
            warnings.append(
                f"Section {i}: config '{cfg.get('name')}' != format guide '{guide['name']}'"
            )
    if len(guide_sections) != len(config_sections):
        warnings.append(
            f"Section count: config has {len(config_sections)}, format guide has {len(guide_sections)}"
        )
    return warnings
