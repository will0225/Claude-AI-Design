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

async function promptSummarize(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 1 — Meeting notes → action items");
  console.log("=".repeat(60));
  const notes = `
    Team sync 2026-06-30: Sarah said the landing page copy is overdue.
    Mike will deploy the staging build by Friday. We need legal review on
    the privacy policy before launch. Budget approved for one contractor
    through Q3. Next sync Tuesday 10am.
  `;
  const reply = await ask(client, {
    system:
      "You extract action items from meeting notes. " +
      "Output exactly three sections: Summary (2 sentences), " +
      "Action Items (bulleted, owner + deadline), Open Questions.",
    user: `Meeting notes:\n${notes.trim()}`,
  });
  console.log(`\nClaude:\n${reply}\n`);
}

async function promptDraftEmail(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 2 — Draft a professional email");
  console.log("=".repeat(60));
  const reply = await ask(client, {
    system:
      "You write concise business email drafts. " +
      "Use a warm but professional tone. " +
      "Never use exclamation marks. Keep under 120 words.",
    user:
      "Draft an email to a client named Alex explaining that their " +
      "project delivery will slip by one week due to an unexpected " +
      "third-party API change. Offer a brief call to walk through options.",
  });
  console.log(`\nClaude:\n${reply}\n`);
}

async function promptCodeReview(client) {
  console.log("=".repeat(60));
  console.log("EXAMPLE 3 — Code review snippet");
  console.log("=".repeat(60));
  const code = `
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
`;
  const reply = await ask(client, {
    system:
      "You are a senior engineer doing code review. " +
      "List issues as: [CRITICAL], [WARNING], or [SUGGESTION]. " +
      "For each issue, give a one-line fix. Max 5 items.",
    user: `Review this Python function:\n\`\`\`python${code}\n\`\`\``,
    maxTokens: 512,
  });
  console.log(`\nClaude:\n${reply}\n`);
}

const EXAMPLES = {
  summarize: promptSummarize,
  email: promptDraftEmail,
  "code-review": promptCodeReview,
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
    console.log("     node claude_demo.js --example summarize\n");
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
