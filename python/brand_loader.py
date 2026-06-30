"""
Load brand.config.yaml and build system prompts that inject fonts, colors,
and document rules automatically — so Claude never asks again.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

import yaml

BRAND_DIR = Path(__file__).resolve().parent.parent / "brand"
CONFIG_PATH = BRAND_DIR / "brand.config.yaml"
EXAMPLE_PATH = BRAND_DIR / "brand.config.example.yaml"
STYLES_PATH = BRAND_DIR / "styles" / "document.css"
HTML_TEMPLATE_PATH = BRAND_DIR / "templates" / "document.html"
FIXED_TEMPLATE_PATH = BRAND_DIR / "templates" / "fixed_document.html"
OUTPUT_DIR = BRAND_DIR / "output"
INBOX_DIR = BRAND_DIR / "inbox"
INBOX_DONE_DIR = INBOX_DIR / "done"

READABLE_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".log", ".rtf"}


def load_brand_config() -> dict:
    if not CONFIG_PATH.exists():
        print(
            f"\n❌ Brand config not found: {CONFIG_PATH}\n"
            f"   Run once:\n"
            f"     cp {EXAMPLE_PATH} {CONFIG_PATH}\n"
            f"   Then edit brand.config.yaml with your company fonts, colors, and style.\n"
        )
        sys.exit(1)

    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate_brand_config(config: dict) -> list[str]:
    """Return list of warnings if placeholders are still present."""
    warnings = []
    company = config.get("company", {})
    if company.get("name", "").strip() in ("", "Your Company Name"):
        warnings.append("company.name is still the placeholder — set your real company name")
    colors = config.get("colors", {})
    for key, val in colors.items():
        if not str(val).startswith("#"):
            warnings.append(f"colors.{key} should be a hex value like #1a365d")
    return warnings


def section_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def section_specs(doc_type: str, config: dict) -> list[dict]:
    return [
        {
            "name": s["name"],
            "slug": section_slug(s["name"]),
            "description": s["description"],
            "number": s.get("number", ""),
        }
        for s in config.get(doc_type, {}).get("sections", [])
    ]


def _section_list(doc_key: str, config: dict) -> str:
    sections = config.get(doc_key, {}).get("sections", [])
    lines = []
    for i, sec in enumerate(sections, 1):
        lines.append(f"  {i}. {sec['name']} — {sec['description']}")
    return "\n".join(lines)


def export_design_reference(config: dict, doc_type: str | None = None) -> str:
    """The permanent 'design page' block — injected into every API call."""
    c = config["company"]
    colors = config["colors"]
    fonts = config["fonts"]
    labels = config.get("document_labels", {})
    design_id = config.get("design_id", c["name"])

    report_sections = section_specs("report", config)
    proposal_sections = section_specs("proposal", config)

    def fmt_sections(specs: list[dict]) -> str:
        return "\n".join(
            f"    {s.get('number', '')} {s['name']}".strip() for s in specs
        )

    active_format = ""
    if doc_type == "report":
        active_format = f"ACTIVE FORMAT: Report\n{fmt_sections(report_sections)}"
    elif doc_type == "proposal":
        active_format = f"ACTIVE FORMAT: Proposal\n{fmt_sections(proposal_sections)}"
    else:
        active_format = (
            f"Report format:\n{fmt_sections(report_sections)}\n"
            f"Proposal format:\n{fmt_sections(proposal_sections)}"
        )

    return f"""=== DESIGN PROFILE REFERENCE (ID: {design_id}) ===
This replaces the Claude.ai Design page. REFERENCE THIS ON EVERY DOCUMENT.
Do NOT ask the user for colors, fonts, or document format — they are defined here.

COMPANY
  name: {c['name']}
  tagline: {c.get('tagline', '')}
  email: {c.get('contact_email', '')}
  phone: {c.get('contact_phone', '')}
  license: {c.get('license', '')}

COLORS (exact hex — CSS must use these values)
  primary:    {colors['primary']}
  secondary:  {colors['secondary']}
  accent:     {colors['accent']}
  critical:   {colors.get('critical', '#c53030')}
  high:       {colors.get('high', '#dd6b20')}
  medium:     {colors.get('medium', '#d69e2e')}
  text:       {colors['text']}
  background: {colors['background']}
  surface:    {colors['surface']}
  border:     {colors['border']}

FONTS (exact font-family names)
  headings: {fonts['heading']}
  body:     {fonts['body']}

DOCUMENT LABELS
  report type: {labels.get('report_type', 'Report')}
  confidential: {labels.get('confidential', '')}

FIXED FORMAT (section order never changes)
{active_format}

LAYOUT RULE: HTML template applies all design. You supply section CONTENT only as JSON.
=== END DESIGN PROFILE ==="""


def build_json_system_prompt(config: dict, doc_type: str) -> str:
    """System prompt that returns structured JSON — rendered into a fixed template."""
    c = config["company"]
    style = config["writing_style"]
    behavior = config.get("behavior", {})
    avoid = ", ".join(style.get("avoid", []))
    never_ask = ", ".join(behavior.get("never_ask_about", []))
    missing_rule = behavior.get(
        "if_detail_missing",
        'Use HTML: <span class="fill-in">[FILL IN: brief description]</span>',
    )

    doc_label = "Proposal" if doc_type == "proposal" else "Report"
    specs = section_specs(doc_type, config)

    section_lines = []
    json_keys = []
    for spec in specs:
        num = f"{spec['number']} " if spec.get("number") else ""
        section_lines.append(
            f"  - {num}{spec['name']} (key: `{spec['slug']}`) — {spec['description']}"
        )
        json_keys.append(f'    "{spec["slug"]}": "HTML fragment (<p>, <ul>, <table> only — no h1/h2)"')

    sections_block = "\n".join(section_lines)

    cover_fields = ""
    json_cover = ""
    if doc_type == "report":
        cover_fields = """
Also include these cover/metadata fields extracted from source material:
  - file_number (e.g. SR-4600NOR-H1-26)
  - review_type (e.g. Standard Review)
  - property_address
  - subtitle (one-sentence scope statement)
  - prepared_for (client entity)
  - property_contact (name and phone)
  - review_period
  - issued_date
"""
        json_cover = """
  "file_number": "string",
  "review_type": "string",
  "property_address": "string",
  "subtitle": "string",
  "prepared_for": "string",
  "property_contact": "string",
  "review_period": "string",
  "issued_date": "string","""

    html_patterns = config.get("report_html_patterns", "")
    patterns_block = f"\nHTML PATTERNS:\n{html_patterns}\n" if html_patterns and doc_type == "report" else ""

    json_schema = "{\n  \"document_title\": \"Short title (usually property address)\","
    json_schema += json_cover
    json_schema += "\n  \"sections\": {\n"
    json_schema += ",\n".join(json_keys)
    json_schema += "\n  }\n}"

    design_block = export_design_reference(config, doc_type)

    return f"""{design_block}

You are a document writer for {c['name']}. Populate a fixed {doc_label.lower()} template from source material.

CRITICAL RULES:
- NEVER ask the user about: {never_ask}.
- If project-specific detail is missing, {missing_rule} — do not ask questions.
- Writing tone: {style['tone']}. Voice: {style['voice']}. Avoid: {avoid}.
- Paragraphs: {style.get('paragraph_style', '2–4 sentences')}.
- Preserve all dollar amounts, dates, suite numbers, finding IDs (F-01, F-02…), and vendor names exactly as in source.
{cover_fields}
SECTIONS (fill every key — same keys every time, in this order):
{sections_block}
{patterns_block}
OUTPUT: Return ONLY valid JSON matching this exact schema (no markdown fences, no extra text):
{json_schema}

Each section value is an HTML fragment (paragraphs, lists, tables). Do NOT include section headings — those are in the template."""


def parse_json_response(text: str) -> dict:
    text = text.strip()
    match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    return json.loads(text)


def render_fixed_document(config: dict, doc_type: str, payload: dict) -> str:
    """Render JSON content into the fixed HTML template — identical layout every time."""
    c = config["company"]
    labels = config.get("document_labels", {})
    specs = section_specs(doc_type, config)
    sections_data = payload.get("sections", {})

    parts = []
    for spec in specs:
        content = sections_data.get(spec["slug"], '<p class="fill-in">[FILL IN]</p>')
        num = spec.get("number", "")
        heading = (
            f'<span class="section-num">{num}</span>{spec["name"]}' if num else spec["name"]
        )
        parts.append(
            f'    <section class="doc-section" id="{spec["slug"]}">\n'
            f"      <h2>{heading}</h2>\n"
            f'      <div class="section-body">{content}</div>\n'
            f"    </section>"
        )
    sections_html = "\n".join(parts)

    template = FIXED_TEMPLATE_PATH.read_text(encoding="utf-8")
    styles = build_stylesheet(config)

    doc_type_label = (
        labels.get("report_type", "Forensic Report")
        if doc_type == "report"
        else labels.get("proposal_type", "Proposal")
    )

    property_address = payload.get("property_address") or payload.get("document_title", "")
    replacements = {
        "{{TITLE}}": f"{c['name']} — {property_address or doc_type.title()}",
        "{{STYLES}}": styles,
        "{{CONFIDENTIAL_LABEL}}": labels.get("confidential", "") if doc_type == "report" else "",
        "{{DOC_TYPE_LABEL}}": doc_type_label.upper(),
        "{{COMPANY_NAME}}": c["name"],
        "{{PROPERTY_ADDRESS}}": property_address,
        "{{SUBTITLE}}": payload.get("subtitle", ""),
        "{{FILE_NUMBER}}": payload.get("file_number", ""),
        "{{REVIEW_TYPE}}": payload.get("review_type", ""),
        "{{PREPARED_FOR}}": payload.get("prepared_for", ""),
        "{{PROPERTY_CONTACT}}": payload.get("property_contact", ""),
        "{{REVIEW_PERIOD}}": payload.get("review_period", ""),
        "{{ISSUED_DATE}}": payload.get("issued_date", date.today().strftime("%b %d, %Y")),
        "{{SECTIONS}}": sections_html,
        "{{FOOTER_DISCLAIMER}}": labels.get("footer_disclaimer", ""),
        "{{CONTACT_EMAIL}}": c.get("contact_email", ""),
        "{{CONTACT_PHONE}}": c.get("contact_phone", ""),
        "{{LICENSE}}": c.get("license", ""),
    }
    html = template
    for token, value in replacements.items():
        html = html.replace(token, str(value))
    return html


def latest_inbox_file() -> Path | None:
    """Newest readable file in brand/inbox/ (ignores README and done/)."""
    if not INBOX_DIR.exists():
        return None
    candidates = [
        p
        for p in INBOX_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in READABLE_EXTENSIONS
        and p.name != "README.txt"
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def read_source_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip()


def archive_inbox_file(path: Path) -> None:
    INBOX_DONE_DIR.mkdir(parents=True, exist_ok=True)
    dest = INBOX_DONE_DIR / path.name
    if dest.exists():
        dest = INBOX_DONE_DIR / f"{path.stem}-{date.today().isoformat()}{path.suffix}"
    path.rename(dest)


def build_brand_system_prompt(config: dict, doc_type: str) -> str:
    """Full system prompt: brand identity + document structure + no-questions rules."""
    c = config["company"]
    colors = config["colors"]
    fonts = config["fonts"]
    style = config["writing_style"]
    behavior = config.get("behavior", {})
    avoid = ", ".join(style.get("avoid", []))
    never_ask = ", ".join(behavior.get("never_ask_about", []))
    missing_rule = behavior.get(
        "if_detail_missing",
        "Use [FILL IN: description] — do not ask the user",
    )

    doc_label = "Proposal" if doc_type == "proposal" else "Report"
    sections = _section_list(doc_type, config)

    return f"""You are a document writer for {c['name']}. Your job is to produce a polished {doc_label.lower()} using ONLY the brand and structure defined below.

CRITICAL RULES — follow every time:
- NEVER ask the user about: {never_ask}.
- All brand details are provided below. Do NOT request colors, fonts, logos, tone, or section structure.
- If project-specific detail is missing, {missing_rule}
- Apply the writing style on every sentence without exception.

=== COMPANY (use in header and footer) ===
Name: {c['name']}
Tagline: {c.get('tagline', '')}
Website: {c.get('website', '')}
Email: {c.get('contact_email', '')}
Phone: {c.get('contact_phone', '') or 'N/A'}

=== BRAND COLORS (use these exact hex values in all styling) ===
Primary:   {colors['primary']}
Secondary: {colors['secondary']}
Accent:    {colors['accent']}
Text:      {colors['text']}
Text Light:{colors['text_light']}
Background:{colors['background']}
Surface:   {colors['surface']}
Border:    {colors['border']}

=== BRAND FONTS (use these exact font-family names) ===
Headings: {fonts['heading']} (bold, 600–700 weight)
Body:     {fonts['body']} (regular, 400–600 weight)

=== WRITING STYLE ===
Tone:       {style['tone']}
Voice:      {style['voice']}
Audience:   {style.get('audience', 'business readers')}
Paragraphs: {style.get('paragraph_style', '2–4 sentences')}
Avoid:      {avoid}

=== {doc_label.upper()} SECTIONS (include in this exact order) ===
{sections}

=== OUTPUT FORMAT ===
Return a complete HTML document (including <!DOCTYPE html>, <html>, <head>, <body>).
- Embed all CSS in a <style> block in <head>.
- Use the exact hex colors and font-family names listed above.
- Include a styled <header> with company name, tagline, document title, and today's date ({date.today().isoformat()}).
- Include a <footer> with company contact info.
- Use semantic HTML: h1/h2/h3, tables where appropriate, .callout for key points.
- Mark unknown project details with <span class="fill-in">[FILL IN: …]</span> — never ask the user in chat.
- Output ONLY the HTML document. No preamble, no markdown fences, no questions."""


def build_stylesheet(config: dict) -> str:
    """Replace placeholders in document.css with brand values."""
    css = STYLES_PATH.read_text(encoding="utf-8")
    colors = config["colors"]
    fonts = config["fonts"]
    replacements = {
        "{{PRIMARY}}": colors["primary"],
        "{{SECONDARY}}": colors["secondary"],
        "{{ACCENT}}": colors["accent"],
        "{{CRITICAL}}": colors.get("critical", "#c53030"),
        "{{HIGH}}": colors.get("high", "#dd6b20"),
        "{{MEDIUM}}": colors.get("medium", "#d69e2e"),
        "{{TEXT}}": colors["text"],
        "{{TEXT_LIGHT}}": colors["text_light"],
        "{{BACKGROUND}}": colors["background"],
        "{{SURFACE}}": colors["surface"],
        "{{BORDER}}": colors["border"],
        "{{HEADING_FONT}}": fonts["heading"],
        "{{BODY_FONT}}": fonts["body"],
        "{{HEADING_FONT_URL}}": fonts.get("heading_url", ""),
        "{{BODY_FONT_URL}}": fonts.get("body_url", ""),
    }
    for token, value in replacements.items():
        css = css.replace(token, value)
    # Remove empty @import lines if no font URL
    lines = [ln for ln in css.splitlines() if '@import url("");' not in ln]
    return "\n".join(lines)


def wrap_html(content: str, title: str, config: dict) -> str:
    """Wrap body HTML in branded shell if Claude returned a fragment."""
    stripped = content.strip()
    if stripped.lower().startswith("<!doctype") or stripped.lower().startswith("<html"):
        return stripped

    template = HTML_TEMPLATE_PATH.read_text(encoding="utf-8")
    styles = build_stylesheet(config)
    return (
        template.replace("{{TITLE}}", title)
        .replace("{{STYLES}}", styles)
        .replace("{{CONTENT}}", stripped)
    )


def brand_summary(config: dict) -> str:
    """One-line confirmation of loaded brand (for CLI output)."""
    c = config["company"]
    colors = config["colors"]
    fonts = config["fonts"]
    return (
        f"Brand loaded: {c['name']} | "
        f"primary {colors['primary']} | "
        f"fonts {fonts['heading']} / {fonts['body']}"
    )
