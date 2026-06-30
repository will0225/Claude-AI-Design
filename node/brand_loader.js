/**
 * Load brand.config.yaml, build prompts, render fixed forensic templates.
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
    if (String(key).startsWith("_")) continue;
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
    number: s.number ?? "",
  }));
}

export function exportDesignReference(config, docType = null) {
  const c = config.company;
  const colors = config.colors;
  const fonts = config.fonts;
  const labels = config.document_labels ?? {};
  const designId = config.design_id ?? c.name;
  const fmtSections = (specs) =>
    specs.map((s) => `    ${s.number ? s.number + " " : ""}${s.name}`.trim()).join("\n");
  const reportSections = sectionSpecs("report", config);
  const proposalSections = sectionSpecs("proposal", config);
  let activeFormat;
  if (docType === "report") {
    activeFormat = `ACTIVE FORMAT: Report\n${fmtSections(reportSections)}`;
  } else if (docType === "proposal") {
    activeFormat = `ACTIVE FORMAT: Proposal\n${fmtSections(proposalSections)}`;
  } else {
    activeFormat = `Report format:\n${fmtSections(reportSections)}\nProposal format:\n${fmtSections(proposalSections)}`;
  }
  return `=== DESIGN PROFILE REFERENCE (ID: ${designId}) ===
This replaces the Claude.ai Design page. REFERENCE THIS ON EVERY DOCUMENT.
Do NOT ask the user for colors, fonts, or document format — they are defined here.

COLORS (exact hex)
  primary: ${colors.primary}  secondary: ${colors.secondary}  accent: ${colors.accent}
  text: ${colors.text}  background: ${colors.background}

FONTS
  headings: ${fonts.heading}  body: ${fonts.body}

FIXED FORMAT
${activeFormat}

LAYOUT RULE: HTML template applies design. You supply section CONTENT only as JSON.
=== END DESIGN PROFILE ===`;
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
    .map((s) => {
      const num = s.number ? `${s.number} ` : "";
      return `  - ${num}${s.name} (key: \`${s.slug}\`) — ${s.description}`;
    })
    .join("\n");

  const jsonKeys = specs
    .map((s) => `    "${s.slug}": "HTML fragment (<p>, <ul>, <table> only — no h1/h2)"`)
    .join(",\n");

  let coverFields = "";
  let jsonCover = "";
  if (docType === "report") {
    coverFields = `
Also include these cover/metadata fields extracted from source material:
  - file_number, review_type, property_address, subtitle
  - prepared_for, property_contact, review_period, issued_date`;
    jsonCover = `
  "file_number": "string",
  "review_type": "string",
  "property_address": "string",
  "subtitle": "string",
  "prepared_for": "string",
  "property_contact": "string",
  "review_period": "string",
  "issued_date": "string",`;
  }

  const htmlPatterns = config.report_html_patterns ?? "";
  const patternsBlock =
    htmlPatterns && docType === "report" ? `\nHTML PATTERNS:\n${htmlPatterns}\n` : "";

  const jsonSchema = `{
  "document_title": "Short title (usually property address)",${jsonCover}
  "sections": {
${jsonKeys}
  }
}`;

  const designBlock = exportDesignReference(config, docType);

  return `${designBlock}

You are a document writer for ${c.name}. Populate a fixed ${docLabel.toLowerCase()} template from source material.

CRITICAL RULES:
- NEVER ask the user about: ${neverAsk}.
- If project-specific detail is missing, ${missingRule} — do not ask questions.
- Writing tone: ${style.tone}. Voice: ${style.voice}. Avoid: ${avoid}.
- Preserve all dollar amounts, dates, suite numbers, finding IDs, and vendor names exactly.
${coverFields}

SECTIONS (fill every key — same keys every time, in this order):
${sectionLines}
${patternsBlock}
OUTPUT: Return ONLY valid JSON matching this exact schema (no markdown fences, no extra text):
${jsonSchema}

Each section value is an HTML fragment. Do NOT include section headings — those are in the template.`;
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
    "{{SECONDARY}}": colors.secondary ?? colors.primary,
    "{{ACCENT}}": colors.accent,
    "{{CRITICAL}}": colors.critical ?? "#8F2018",
    "{{HIGH}}": colors.high ?? "#A23A2C",
    "{{MEDIUM}}": colors.medium ?? "#C79A3E",
    "{{POSITIVE}}": colors.positive ?? "#3C7350",
    "{{TEXT}}": colors.text,
    "{{TEXT_LIGHT}}": colors.text_light,
    "{{BACKGROUND}}": colors.background,
    "{{SURFACE}}": colors.surface,
    "{{BORDER}}": colors.border,
    "{{HEADING_FONT}}": fonts.heading,
    "{{BODY_FONT}}": fonts.body,
    "{{MONO_FONT}}": fonts.mono ?? "IBM Plex Mono",
    "{{HEADING_FONT_URL}}": fonts.heading_url ?? "",
    "{{BODY_FONT_URL}}": fonts.body_url ?? "",
    "{{MONO_FONT_URL}}": fonts.mono_url ?? "",
  };
  for (const [token, value] of Object.entries(replacements)) {
    css = css.split(token).join(value);
  }
  return css.split("\n").filter((ln) => !ln.includes('@import url("");')).join("\n");
}

export function renderFixedDocument(config, docType, payload) {
  const c = config.company;
  const labels = config.document_labels ?? {};
  const specs = sectionSpecs(docType, config);
  const sectionsData = payload.sections ?? {};

  const sectionsHtml = specs
    .map((spec) => {
      const content = sectionsData[spec.slug] ?? '<p class="fill-in">[FILL IN]</p>';
      const heading = spec.number
        ? `<span class="section-num">${spec.number}</span>${spec.name}`
        : spec.name;
      return `    <section class="doc-section" id="${spec.slug}">\n      <h2>${heading}</h2>\n      <div class="section-body">${content}</div>\n    </section>`;
    })
    .join("\n");

  const docTypeLabel =
    docType === "report"
      ? labels.report_type ?? "Forensic Report"
      : labels.proposal_type ?? "Proposal";

  const propertyAddress = payload.property_address || payload.document_title || "";
  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  let html = fs.readFileSync(FIXED_TEMPLATE_PATH, "utf8");
  const styles = buildStylesheet(config);

  const replacements = {
    "{{TITLE}}": `${c.name} — ${propertyAddress || docType}`,
    "{{STYLES}}": styles,
    "{{CONFIDENTIAL_LABEL}}": docType === "report" ? labels.confidential ?? "" : "",
    "{{DOC_TYPE_LABEL}}": docTypeLabel.toUpperCase(),
    "{{COMPANY_NAME}}": c.name,
    "{{PROPERTY_ADDRESS}}": propertyAddress,
    "{{SUBTITLE}}": payload.subtitle ?? "",
    "{{FILE_NUMBER}}": payload.file_number ?? "",
    "{{REVIEW_TYPE}}": payload.review_type ?? "",
    "{{PREPARED_FOR}}": payload.prepared_for ?? "",
    "{{PROPERTY_CONTACT}}": payload.property_contact ?? "",
    "{{REVIEW_PERIOD}}": payload.review_period ?? "",
    "{{ISSUED_DATE}}": payload.issued_date ?? today,
    "{{SECTIONS}}": sectionsHtml,
    "{{FOOTER_DISCLAIMER}}": labels.footer_disclaimer ?? "",
    "{{CONTACT_EMAIL}}": c.contact_email ?? "",
    "{{CONTACT_PHONE}}": c.contact_phone ?? "",
    "{{LICENSE}}": c.license ?? "",
  };
  for (const [token, value] of Object.entries(replacements)) {
    html = html.split(token).join(String(value));
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

export const buildBrandSystemPrompt = buildJsonSystemPrompt;
