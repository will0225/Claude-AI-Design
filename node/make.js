#!/usr/bin/env node
/**
 * Drop downloaded info in brand/inbox/, run one command, get the same template every time.
 *
 *   node make.js proposal
 *   node make.js report
 *   node make.js proposal --file ~/Downloads/notes.txt
 */

import Anthropic from "@anthropic-ai/sdk";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import {
  INBOX_DIR,
  OUTPUT_DIR,
  archiveInboxFile,
  brandSummary,
  buildJsonSystemPrompt,
  latestInboxFile,
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
    console.error("\n❌ ANTHROPIC_API_KEY is not set.\n");
    process.exit(1);
  }
  return new Anthropic({ apiKey });
}

function resolveInput(fileArg) {
  if (fileArg) {
    const p = path.resolve(fileArg.replace(/^~/, process.env.HOME ?? ""));
    if (!fs.existsSync(p)) {
      console.error(`❌ File not found: ${p}`);
      process.exit(1);
    }
    return { path: p, fromInbox: false };
  }
  fs.mkdirSync(INBOX_DIR, { recursive: true });
  const latest = latestInboxFile();
  if (!latest) {
    console.error(`\n❌ No files in ${INBOX_DIR}\n   Drop a .txt, .csv, or .md file there.\n`);
    process.exit(1);
  }
  console.log(`📥 Using inbox file: ${path.basename(latest)}\n`);
  return { path: latest, fromInbox: true };
}

async function generateContent(client, config, docType, sourceText) {
  const system = buildJsonSystemPrompt(config, docType);
  const response = await client.messages.create({
    model: DEFAULT_MODEL,
    max_tokens: 8192,
    system,
    messages: [
      {
        role: "user",
        content:
          `Fill the ${docType} template from this downloaded/source material. ` +
          `Use the fixed section keys. Do not ask questions.\n\n` +
          `--- SOURCE MATERIAL ---\n${sourceText}`,
      },
    ],
  });
  return parseJsonResponse(response.content[0].text);
}

function saveOutput(html, docType, config, sourceName) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const slug = config.company.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const stem = path.basename(sourceName, path.extname(sourceName)).slice(0, 40);
  const ts = new Date().toISOString().replace(/[-:T]/g, "").slice(0, 14);
  const filename = `${slug}-${docType}-${stem}-${ts}.html`;
  const outPath = path.join(OUTPUT_DIR, filename);
  fs.writeFileSync(outPath, html, "utf8");
  return outPath;
}

async function main() {
  const args = process.argv.slice(2);
  const type = args.find((a) => a === "proposal" || a === "report");
  const fileIdx = args.indexOf("--file");
  const fileArg = fileIdx !== -1 ? args[fileIdx + 1] : null;
  const keepInbox = args.includes("--keep-inbox");

  if (!type) {
    console.log("Usage: node make.js <proposal|report> [--file path.txt]");
    process.exit(1);
  }

  const config = loadBrandConfig();
  for (const w of validateBrandConfig(config)) console.log(`⚠ ${w}`);

  const { path: sourcePath, fromInbox } = resolveInput(fileArg);
  const sourceText = fs.readFileSync(sourcePath, "utf8").trim();
  if (!sourceText) {
    console.error("❌ Source file is empty.");
    process.exit(1);
  }

  const client = getClient();
  console.log(`✓ ${brandSummary(config)}`);
  console.log(`✓ Building fixed ${type} template…\n`);

  const payload = await generateContent(client, config, type, sourceText);
  const html = renderFixedDocument(config, type, payload);
  const outPath = saveOutput(html, type, config, path.basename(sourcePath));

  if (fromInbox && !keepInbox) {
    archiveInboxFile(sourcePath);
    console.log(`📦 Moved source to inbox/done/${path.basename(sourcePath)}`);
  }

  console.log(`✓ Saved: ${outPath}`);
  console.log("  Same layout every time — open in browser → Print → Save as PDF\n");
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
