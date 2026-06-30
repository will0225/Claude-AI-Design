#!/usr/bin/env node
/**
 * Claude API demo script (Node.js).
 *
 * Usage:
 *   cp .env.example .env          # then add your API key
 *   npm install
 *   npm run demo                  # smoke test
 *   npm run demo:all              # smoke test + three examples
 */

import Anthropic from "@anthropic-ai/sdk";
import dotenv from "dotenv";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: join(__dirname, ".env") });

const DEFAULT_MODEL = process.env.CLAUDE_MODEL || "claude-sonnet-4-6";

function getClient() {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey || apiKey.startsWith("sk-ant-api03-xxx")) {
    console.error(`
❌ ANTHROPIC_API_KEY is not set.
   1. Copy node/.env.example to node/.env
   2. Add your key from https://console.anthropic.com/settings/keys
`);
    process.exit(1);
  }
  return new Anthropic({ apiKey });
}

async function ask(client, { system, user, maxTokens = 1024 }) {
  const response = await client.messages.create({
    model: DEFAULT_MODEL,
    max_tokens: maxTokens,
    system,
    messages: [{ role: "user", content: user }],
  });
  return response.content[0].text;
}

async function smokeTest(client) {
  console.log("=".repeat(60));
  console.log("SMOKE TEST — basic Claude response");
  console.log("=".repeat(60));
  const reply = await ask(client, {
    system: "You are a helpful assistant. Reply in one short sentence.",
    user: "Say hello and confirm you received this message.",
  });
  console.log(`\nClaude (${DEFAULT_MODEL}):\n${reply}\n`);
}

async function promptDiscovery(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 1 — Discovery call → proposal outline");
  console.log("=".repeat(60));
  const notes = `
    Discovery call 2026-06-30 with Jordan (COO), Brightline Marketing, ~12 staff.
    Pain: client reporting takes 6+ hrs/week; proposal drafts inconsistent across team.
    Tried ChatGPT Team — outputs vary too much, hard to reuse prompts.
    Wants Claude wired into daily workflow; open to Python script or Zapier if simpler.
    Budget: $5–8k for setup + training. Timeline: live in 3 weeks before Q3 campaigns.
    Must loop in IT on API/data policy. Competitor quote pending from another vendor.
    Jordan asked for a scope doc by Friday; decision by next Tuesday.
  `;
  const reply = await ask(client, {
    system:
      "You are a consultant turning discovery call notes into a proposal outline. " +
      "Output exactly four sections: Client Snapshot (3 bullets), Stated Needs, " +
      "Proposed Scope (bulleted deliverables tagged S/M/L for effort), " +
      "Next Steps (owner + date). Use client-ready language; avoid internal jargon.",
    user: `Discovery call notes:\n${notes.trim()}`,
    maxTokens: 1536,
  });
  console.log(`\nClaude:\n${reply}\n`);
}

async function promptStatusEmail(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 2 — Weekly client status update");
  console.log("=".repeat(60));
  const reply = await ask(client, {
    system:
      "You write weekly project status emails for consulting clients. " +
      "Structure exactly: Subject line, Progress This Week (3 bullets), " +
      "Blockers (one bullet or 'None'), Plan for Next Week (3 bullets), " +
      "Ask of Client (one sentence or 'None'). " +
      "Tone: confident and transparent. Body under 150 words. No exclamation marks.",
    user:
      "Client: Northwind Digital. Project: Claude workflow setup.\n" +
      "This week: completed API setup and demo script; drafted three tailored prompts; " +
      "shared setup guide for their team.\n" +
      "Blocker: waiting on their legal team to approve API usage policy.\n" +
      "Next week: handoff screen share; customize prompts for client reporting workflow; " +
      "document Zapier option for non-technical staff.\n" +
      "Ask: confirm handoff call slot (Tue or Wed afternoon).",
  });
  console.log(`\nClaude:\n${reply}\n`);
}

async function promptResearchBrief(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 3 — Research notes → executive brief");
  console.log("=".repeat(60));
  const notes = `
    Research re: AI tooling for Brightline's workflow automation RFP response.
    - Claude API: strong long-document handling; official Python + Node SDKs.
    - OpenAI GPT-4o: larger plugin ecosystem; team already has some ChatGPT seats.
    - Anthropic API data: not used for training by default — important for client data.
    - Zapier / Make: both have Anthropic connectors; good for marketing ops, ~$20+/mo.
    - Pricing: Haiku cheapest/high volume; Sonnet best balance; Opus for heavy reasoning.
    - Claude.ai Projects: may suffice for non-technical staff without API spend.
    - [UNVERIFIED] Gemini Enterprise may integrate better with Google Workspace.
    - Client priority: repeatable prompts, clear handoff docs, minimal engineering lift.
  `;
  const reply = await ask(client, {
    system:
      "You synthesize raw research notes into an executive brief for a client RFP. " +
      "Output: Headline (one sentence), Key Findings (5 bullets), " +
      "Implications for This Client (3 bullets), Recommended Actions (numbered, max 3). " +
      "Preserve [UNVERIFIED] tags on any unconfirmed claims.",
    user: `Research notes:\n${notes.trim()}`,
    maxTokens: 1536,
  });
  console.log(`\nClaude:\n${reply}\n`);
}

const EXAMPLES = {
  discovery: promptDiscovery,
  "status-email": promptStatusEmail,
  "research-brief": promptResearchBrief,
};

async function main() {
  const args = process.argv.slice(2);
  const runAll = args.includes("--all");
  const exampleFlag = args.indexOf("--example");
  const exampleName =
    exampleFlag !== -1 ? args[exampleFlag + 1] : undefined;

  const client = getClient();
  console.log(`✓ API key loaded. Model: ${DEFAULT_MODEL}\n`);

  await smokeTest(client);

  if (runAll) {
    for (const fn of Object.values(EXAMPLES)) {
      await fn(client);
    }
  } else if (exampleName && EXAMPLES[exampleName]) {
    await EXAMPLES[exampleName](client);
  } else if (!runAll) {
    console.log("Tip: run with --all to see three tailored example prompts.");
    console.log("     node claude_demo.js --example discovery\n");
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
