#!/usr/bin/env node
/**
 * Generate a branded proposal or report — fonts, colors, and structure applied automatically.
 *
 * Setup once:
 *   cp ../brand/brand.config.example.yaml ../brand/brand.config.yaml
 *
 * Usage:
 *   node generate_document.js proposal --input notes.txt
 *   node generate_document.js report --input data.txt
 *   node generate_document.js --show-brand
 */

import Anthropic from "@anthropic-ai/sdk";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import {
  OUTPUT_DIR,
  brandSummary,
  buildJsonSystemPrompt,
  loadBrandConfig,
  parseJsonResponse,
  renderFixedDocument,
  validateBrandConfig,
} from "./brand_loader.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, ".env") });

const DEFAULT_MODEL = process.env.CLAUDE_MODEL || "claude-sonnet-4-6";

function getClient() {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey || apiKey.startsWith("sk-ant-api03-xxx")) {
    console.error("\n❌ ANTHROPIC_API_KEY is not set.\n   Copy node/.env.example to node/.env and add your key.\n");
    process.exit(1);
  }
  return new Anthropic({ apiKey });
}

function extractHtml(text) {
  const match = text.trim().match(/```(?:html)?\s*([\s\S]*?)```/i);
  return match ? match[1].trim() : text.trim();
}

async function generate(client, config, docType, userContent) {
  const system = buildJsonSystemPrompt(config, docType);
  const response = await client.messages.create({
    model: DEFAULT_MODEL,
    max_tokens: 8192,
    system,
    messages: [
      {
        role: "user",
        content:
          `Fill the ${docType} template from the following source material. ` +
          `Use the fixed section keys. Do not ask any questions.\n\n` +
          `--- SOURCE MATERIAL ---\n${userContent}`,
      },
    ],
  });
  const payload = parseJsonResponse(response.content[0].text);
  return renderFixedDocument(config, docType, payload);
}

function saveOutput(html, docType, config) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const slug = config.company.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const timestamp = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
  const filename = `${slug}-${docType}-${timestamp}.html`;
  const outPath = path.join(OUTPUT_DIR, filename);
  const title = `${config.company.name} — ${docType[0].toUpperCase()}${docType.slice(1)}`;
  fs.writeFileSync(outPath, html, "utf8");
  return outPath;
}

async function main() {
  const args = process.argv.slice(2);
  const showBrand = args.includes("--show-brand");
  const inputIdx = args.indexOf("--input");
  const inputFile = inputIdx !== -1 ? args[inputIdx + 1] : null;
  const type = args.find((a) => a === "proposal" || a === "report");

  const config = loadBrandConfig();

  if (showBrand) {
    console.log(`✓ ${brandSummary(config)}`);
    for (const w of validateBrandConfig(config)) console.log(`  ⚠ ${w}`);
    return;
  }

  if (!type) {
    console.log(`Usage: node generate_document.js <proposal|report> [--input file.txt]`);
    process.exit(1);
  }

  for (const w of validateBrandConfig(config)) {
    console.log(`⚠ ${w}`);
  }

  const userContent = inputFile
    ? fs.readFileSync(inputFile, "utf8").trim()
    : fs.readFileSync(0, "utf8").trim();

  if (!userContent) {
    console.error("❌ No input provided.");
    process.exit(1);
  }

  const client = getClient();
  console.log(`✓ ${brandSummary(config)}`);
  console.log(`✓ Generating ${type}…\n`);

  const html = await generate(client, config, type, userContent);
  const outPath = saveOutput(html, type, config);

  console.log(`✓ Saved: ${outPath}`);
  console.log("  Open in a browser → Print → Save as PDF for a final document.\n");
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
