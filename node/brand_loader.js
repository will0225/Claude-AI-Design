/**
 * Load brand.config.yaml, build prompts, render fixed templates.
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
export const FIXED_TEMPLATE_PATH = path.join(BRAND_DIR, "templates", "fixed_document.html");
export const OUTPUT_DIR = path.join(BRAND_DIR, "output");
export const INBOX_DIR = path.join(BRAND_DIR, "inbox");
export const INBOX_DONE_DIR = path.join(INBOX_DIR, "done");

const READABLE_EXTENSIONS = new Set([".txt", ".md", ".csv", ".json", ".log", ".rtf"]);

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

export function sectionSlug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "");
}

export function sectionSpecs(docType, config) {
  return (config[docType]?.sections ?? []).map((s) => ({
    name: s.name,
    slug: sectionSlug(s.name),
    description: s.description,
  }));
}

export function buildJsonSystemPrompt(config, docType) {
  const c = config.company;
  const style = config.writing_style;
  const behavior = config.behavior ?? {};
  const avoid = (style.avoid ?? []).join(", ");
  const neverAsk = (behavior.never_ask_about ?? []).join(", ");
  const missingRule =
    behavior.if_detail_missing ??
    'Use HTML: <span class="fill-in">[FILL IN: brief description]</span>';

  const docLabel = docType === "proposal" ? "Proposal" : "Report";
  const specs = sectionSpecs(docType, config);

  const sectionLines = specs
    .map((s, i) => `  ${i + 1}. ${s.name} (key: \`${s.slug}\`) — ${s.description}`)
    .join("\n");

  const jsonKeys = specs
    .map((s) => `    "${s.slug}": "HTML fragment (<p>, <ul>, <table> only — no h1/h2)"`)
    .join(",\n");

  const jsonSchema = `{
  "document_title": "Short title for this specific document",
  "sections": {
${jsonKeys}
  }
}`;

  return `You are a document writer for ${c.name}. Populate a fixed ${docLabel.toLowerCase()} template from source material.

CRITICAL RULES:
- NEVER ask the user about: ${neverAsk}.
- If project-specific detail is missing, ${missingRule} — do not ask questions.
- Writing tone: ${style.tone}. Voice: ${style.voice}. Avoid: ${avoid}.
- Paragraphs: ${style.paragraph_style ?? "2–4 sentences"}.

SECTIONS (fill every key — same keys every time, in this order):
${sectionLines}

OUTPUT: Return ONLY valid JSON matching this exact schema (no markdown fences, no extra text):
${jsonSchema}

Each section value is an HTML fragment (paragraphs, lists, tables). Do NOT include section headings — those are in the template.`;
}

export function parseJsonResponse(text) {
  let cleaned = text.trim();
  const match = cleaned.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (match) cleaned = match[1].trim();
  return JSON.parse(cleaned);
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

export function renderFixedDocument(config, docType, payload) {
  const c = config.company;
  const specs = sectionSpecs(docType, config);
  const sectionsData = payload.sections ?? {};
  const docTitle = payload.document_title ?? docType[0].toUpperCase() + docType.slice(1);

  const sectionsHtml = specs
    .map((spec) => {
      const content = sectionsData[spec.slug] ?? '<p class="fill-in">[FILL IN]</p>';
      return `    <section class="doc-section" id="${spec.slug}">\n      <h2>${spec.name}</h2>\n      <div class="section-body">${content}</div>\n    </section>`;
    })
    .join("\n");

  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  let html = fs.readFileSync(FIXED_TEMPLATE_PATH, "utf8");
  const docLabel = docType === "proposal" ? "PROPOSAL" : "REPORT";
  const styles = buildStylesheet(config);

  const replacements = {
    "{{TITLE}}": `${c.name} — ${docTitle}`,
    "{{STYLES}}": styles,
    "{{DOC_TYPE}}": docLabel,
    "{{COMPANY_NAME}}": c.name,
    "{{TAGLINE}}": c.tagline ?? "",
    "{{DOCUMENT_TITLE}}": docTitle,
    "{{DATE}}": today,
    "{{SECTIONS}}": sectionsHtml,
    "{{CONTACT_EMAIL}}": c.contact_email ?? "",
    "{{WEBSITE}}": c.website ?? "",
  };
  for (const [token, value] of Object.entries(replacements)) {
    html = html.split(token).join(value);
  }
  return html;
}

export function latestInboxFile() {
  if (!fs.existsSync(INBOX_DIR)) return null;
  const candidates = fs
    .readdirSync(INBOX_DIR)
    .map((name) => path.join(INBOX_DIR, name))
    .filter(
      (p) =>
        fs.statSync(p).isFile() &&
        READABLE_EXTENSIONS.has(path.extname(p).toLowerCase()) &&
        path.basename(p) !== "README.txt"
    );
  if (!candidates.length) return null;
  return candidates.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0];
}

export function archiveInboxFile(filePath) {
  fs.mkdirSync(INBOX_DONE_DIR, { recursive: true });
  const base = path.basename(filePath);
  let dest = path.join(INBOX_DONE_DIR, base);
  if (fs.existsSync(dest)) {
    const ext = path.extname(base);
    const stem = path.basename(base, ext);
    dest = path.join(INBOX_DONE_DIR, `${stem}-${new Date().toISOString().slice(0, 10)}${ext}`);
  }
  fs.renameSync(filePath, dest);
}

export function brandSummary(config) {
  const c = config.company;
  return `Brand loaded: ${c.name} | primary ${config.colors.primary} | fonts ${config.fonts.heading} / ${config.fonts.body}`;
}

// Backward-compatible alias
export const buildBrandSystemPrompt = buildJsonSystemPrompt;
