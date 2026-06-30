"""
Load brand.config.yaml and build system prompts that inject fonts, colors,
and document rules automatically — so Claude never asks again.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

BRAND_DIR = Path(__file__).resolve().parent.parent / "brand"
CONFIG_PATH = BRAND_DIR / "brand.config.yaml"
EXAMPLE_PATH = BRAND_DIR / "brand.config.example.yaml"
STYLES_PATH = BRAND_DIR / "styles" / "document.css"
HTML_TEMPLATE_PATH = BRAND_DIR / "templates" / "document.html"
OUTPUT_DIR = BRAND_DIR / "output"


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


def _section_list(doc_key: str, config: dict) -> str:
    sections = config.get(doc_key, {}).get("sections", [])
    lines = []
    for i, sec in enumerate(sections, 1):
        lines.append(f"  {i}. {sec['name']} — {sec['description']}")
    return "\n".join(lines)


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
