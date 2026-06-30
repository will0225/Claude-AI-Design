/**
 * Load brand.config.yaml and build system prompts with fonts, colors, and rules baked in.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const BRAND_DIR = path.resolve(__dirname, "../brand");
export const CONFIG_PATH = path.join(BRAND_DIR, "brand.config.yaml");
export const EXAMPLE_PATH = path.join(BRAND_DIR, "brand.config.example.yaml");
export const STYLES_PATH = path.join(BRAND_DIR, "styles", "document.css");
export const HTML_TEMPLATE_PATH = path.join(BRAND_DIR, "templates", "document.html");
export const OUTPUT_DIR = path.join(BRAND_DIR, "output");

export function loadBrandConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    console.error(`
❌ Brand config not found: ${CONFIG_PATH}
   Run once:
     cp ${EXAMPLE_PATH} ${CONFIG_PATH}
   Then edit brand.config.yaml with your company fonts, colors, and style.
`);
    process.exit(1);
  }
  return yaml.load(fs.readFileSync(CONFIG_PATH, "utf8"));
}

export function validateBrandConfig(config) {
  const warnings = [];
  const name = config.company?.name?.trim() ?? "";
  if (!name || name === "Your Company Name") {
    warnings.push("company.name is still the placeholder — set your real company name");
  }
  for (const [key, val] of Object.entries(config.colors ?? {})) {
    if (!String(val).startsWith("#")) {
      warnings.push(`colors.${key} should be a hex value like #1a365d`);
    }
  }
  return warnings;
}

function sectionList(docKey, config) {
  return (config[docKey]?.sections ?? [])
    .map((sec, i) => `  ${i + 1}. ${sec.name} — ${sec.description}`)
    .join("\n");
}

export function buildBrandSystemPrompt(config, docType) {
  const c = config.company;
  const colors = config.colors;
  const fonts = config.fonts;
  const style = config.writing_style;
  const behavior = config.behavior ?? {};
  const avoid = (style.avoid ?? []).join(", ");
  const neverAsk = (behavior.never_ask_about ?? []).join(", ");
  const missingRule =
    behavior.if_detail_missing ??
    "Use [FILL IN: description] — do not ask the user";

  const docLabel = docType === "proposal" ? "Proposal" : "Report";
  const sections = sectionList(docType, config);
  const today = new Date().toISOString().slice(0, 10);

  return `You are a document writer for ${c.name}. Your job is to produce a polished ${docLabel.toLowerCase()} using ONLY the brand and structure defined below.

CRITICAL RULES — follow every time:
- NEVER ask the user about: ${neverAsk}.
- All brand details are provided below. Do NOT request colors, fonts, logos, tone, or section structure.
- If project-specific detail is missing, ${missingRule}
- Apply the writing style on every sentence without exception.

=== COMPANY (use in header and footer) ===
Name: ${c.name}
Tagline: ${c.tagline ?? ""}
Website: ${c.website ?? ""}
Email: ${c.contact_email ?? ""}
Phone: ${c.contact_phone || "N/A"}

=== BRAND COLORS (use these exact hex values in all styling) ===
Primary:   ${colors.primary}
Secondary: ${colors.secondary}
Accent:    ${colors.accent}
Text:      ${colors.text}
Text Light:${colors.text_light}
Background:${colors.background}
Surface:   ${colors.surface}
Border:    ${colors.border}

=== BRAND FONTS (use these exact font-family names) ===
Headings: ${fonts.heading} (bold, 600–700 weight)
Body:     ${fonts.body} (regular, 400–600 weight)

=== WRITING STYLE ===
Tone:       ${style.tone}
Voice:      ${style.voice}
Audience:   ${style.audience ?? "business readers"}
Paragraphs: ${style.paragraph_style ?? "2–4 sentences"}
Avoid:      ${avoid}

=== ${docLabel.toUpperCase()} SECTIONS (include in this exact order) ===
${sections}

=== OUTPUT FORMAT ===
Return a complete HTML document (including <!DOCTYPE html>, <html>, <head>, <body>).
- Embed all CSS in a <style> block in <head>.
- Use the exact hex colors and font-family names listed above.
- Include a styled <header> with company name, tagline, document title, and today's date (${today}).
- Include a <footer> with company contact info.
- Use semantic HTML: h1/h2/h3, tables where appropriate, .callout for key points.
- Mark unknown project details with <span class="fill-in">[FILL IN: …]</span> — never ask the user in chat.
- Output ONLY the HTML document. No preamble, no markdown fences, no questions.`;
}

export function buildStylesheet(config) {
  let css = fs.readFileSync(STYLES_PATH, "utf8");
  const { colors, fonts } = config;
  const replacements = {
    "{{PRIMARY}}": colors.primary,
    "{{SECONDARY}}": colors.secondary,
    "{{ACCENT}}": colors.accent,
    "{{TEXT}}": colors.text,
    "{{TEXT_LIGHT}}": colors.text_light,
    "{{BACKGROUND}}": colors.background,
    "{{SURFACE}}": colors.surface,
    "{{BORDER}}": colors.border,
    "{{HEADING_FONT}}": fonts.heading,
    "{{BODY_FONT}}": fonts.body,
    "{{HEADING_FONT_URL}}": fonts.heading_url ?? "",
    "{{BODY_FONT_URL}}": fonts.body_url ?? "",
  };
  for (const [token, value] of Object.entries(replacements)) {
    css = css.split(token).join(value);
  }
  return css.split("\n").filter((ln) => !ln.includes('@import url("");')).join("\n");
}

export function wrapHtml(content, title, config) {
  const stripped = content.trim();
  if (stripped.toLowerCase().startsWith("<!doctype") || stripped.toLowerCase().startsWith("<html")) {
    return stripped;
  }
  const template = fs.readFileSync(HTML_TEMPLATE_PATH, "utf8");
  const styles = buildStylesheet(config);
  return template
    .replace("{{TITLE}}", title)
    .replace("{{STYLES}}", styles)
    .replace("{{CONTENT}}", stripped);
}

export function brandSummary(config) {
  const c = config.company;
  return `Brand loaded: ${c.name} | primary ${config.colors.primary} | fonts ${config.fonts.heading} / ${config.fonts.body}`;
}
