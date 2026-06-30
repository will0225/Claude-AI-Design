# Claude Setup Guide

This guide walks you through creating an Anthropic account, securing your API key, and running the included demo scripts on your machine. Follow the steps in order; the whole process takes about 15 minutes.

> **Primary workflow:** If you need **branded proposals and reports** (fonts, colors, format applied automatically), start with [BRAND_SETUP.md](./BRAND_SETUP.md) after completing steps 1–3 below.

---

## 1. Create an Anthropic account

1. Go to [https://console.anthropic.com](https://console.anthropic.com).
2. Click **Sign up** and create an account (email or Google).
3. Complete any verification steps Anthropic requires.
4. You land on the **Console** dashboard — this is where you manage API keys, usage, and billing.

> **Billing note:** API calls are pay-as-you-go. New accounts may receive trial credits. Check [Pricing](https://www.anthropic.com/pricing) and set a **usage limit** under Console → Settings → Limits so costs stay predictable.

---

## 2. Create and store an API key

1. In the Console, open **Settings → API Keys**  
   Direct link: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. Click **Create Key**.
3. Give it a descriptive name (e.g. `local-dev-june-2026`).
4. Copy the key immediately — Anthropic shows the full secret **only once**.
5. Store it in a password manager. **Never** commit it to Git, paste it in Slack, or embed it in client-side code.

### Key format

Keys look like:

```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

If you lose a key, revoke it in the Console and create a new one.

---

## 3. Secure the key with environment variables

Environment variables keep secrets out of source code. The demo scripts read `ANTHROPIC_API_KEY` automatically.

### Option A — `.env` file (recommended for local dev)

This repo includes `.env.example` files. Copy one and add your key:

**Python:**

```bash
cd python
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

**Node.js:**

```bash
cd node
cp .env.example .env
# Edit .env and replace the placeholder with your real key
```

The `.env` file is listed in `.gitignore` and will not be committed.

### Option B — Shell export (temporary, current terminal only)

**macOS / Linux:**

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Windows (PowerShell):**

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
```

### Option C — Persistent shell profile (advanced)

Add the `export` line to `~/.bashrc`, `~/.zshrc`, or Windows user environment variables if you want the key available in every new terminal. Only do this on a machine you control.

---

## 4. Choose Python or Node.js

Either stack works. Pick the one you already use day-to-day.

| | Python | Node.js |
|---|--------|---------|
| Folder | `python/` | `node/` |
| SDK | [anthropic](https://pypi.org/project/anthropic/) | [@anthropic-ai/sdk](https://www.npmjs.com/package/@anthropic-ai/sdk) |
| Min. version | Python 3.9+ | Node 18+ |

---

## 5. Install dependencies and run the demo

### Python

```bash
cd python

# Optional but recommended: use a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
python claude_demo.py              # smoke test
python claude_demo.py --all         # smoke test + 3 example prompts
```

### Node.js

```bash
cd node
npm install
npm run demo                        # smoke test
npm run demo:all                    # smoke test + 3 example prompts
```

### Expected output

You should see something like:

```
✓ API key loaded. Model: claude-sonnet-4-6

============================================================
SMOKE TEST — basic Claude response
============================================================

Claude (claude-sonnet-4-6):
Hello! I received your message.
```

If you see a valid Claude reply, your setup is working.

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ANTHROPIC_API_KEY is not set` | Missing or placeholder `.env` | Copy `.env.example` → `.env` and paste your key |
| `401 authentication_error` | Wrong or revoked key | Create a new key in the Console |
| `429 rate_limit_error` | Too many requests | Wait a minute; check usage limits |
| `404 model_not_found` | Model name typo or no access | Use `claude-sonnet-4-6` or check [model docs](https://docs.anthropic.com/en/docs/about-claude/models) |
| Network / SSL errors | Firewall or proxy | Allow outbound HTTPS to `api.anthropic.com` |

Enable debug logging (Python SDK):

```bash
export ANTHROPIC_LOG=debug
python claude_demo.py
```

---

## 7. No-code alternatives (optional)

If you prefer not to write code for some workflows:

| Tool | Best for | Link |
|------|----------|------|
| **Claude.ai** | Chat, Projects, Artifacts | [claude.ai](https://claude.ai) |
| **Zapier** | Connect Claude to Gmail, Slack, Sheets | [Zapier + Anthropic](https://zapier.com/apps/anthropic-claude/integrations) |
| **Make (Integromat)** | Visual multi-step automations | [Make + Anthropic](https://www.make.com/en/integrations/anthropic-claude) |
| **n8n** | Self-hosted workflows | [n8n Anthropic node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-langchain.anthropic/) |

For repeatable **API** integrations (version control, tests, custom logic), the SDK approach in this repo is the most maintainable.

---

## 8. Security checklist

- [ ] API key stored in `.env` or a secrets manager — not in source code
- [ ] `.env` is in `.gitignore` (already configured in this repo)
- [ ] Usage limit set in Anthropic Console
- [ ] Separate keys for dev vs. production (revoke old keys when rotating)
- [ ] Never expose the key in browser JavaScript or mobile app bundles

---

## Next steps

- Read [EXTENSION_GUIDE.md](./EXTENSION_GUIDE.md) to add your own prompts and integrate Claude into your projects.
- Read [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md) for three ready-to-use prompt patterns and why they work.
- Use [HANDOFF_CHECKLIST.md](./HANDOFF_CHECKLIST.md) during your verification call.
