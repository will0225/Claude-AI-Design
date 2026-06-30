# Handoff Checklist — Verification Call

Use this checklist during your screen-share to confirm everything works on the client's machine. Target time: 20–30 minutes.

---

## Before the call (client prep)

Send the client this short list 24 hours ahead:

- [ ] Anthropic account created at [console.anthropic.com](https://console.anthropic.com)
- [ ] API key created and saved in a password manager
- [ ] Python 3.9+ **or** Node 18+ installed (`python3 --version` / `node --version`)
- [ ] Repo cloned or zip downloaded to their machine
- [ ] Terminal app ready (Terminal on Mac, PowerShell or WSL on Windows)

---

## During the call — step by step

### 1. Account and billing (5 min)

- [ ] Client can log into [console.anthropic.com](https://console.anthropic.com)
- [ ] API key visible under Settings → API Keys
- [ ] Usage limit configured (Settings → Limits) — agree on a monthly cap
- [ ] Client understands keys are secret (not shared, not committed to Git)

### 2. Environment setup (5 min)

- [ ] Navigate to `python/` or `node/` folder
- [ ] Copy `.env.example` → `.env`
- [ ] Paste API key into `.env` (you should **not** see the full key on screen — mask it)
- [ ] Confirm `.env` is not tracked: `git status` should not list `.env`

### 3. Install and smoke test (5 min)

**Python path:**

```bash
cd python
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python claude_demo.py
```

**Node path:**

```bash
cd node
npm install
npm run demo
```

- [ ] Script prints `✓ API key loaded`
- [ ] Claude returns a coherent one-sentence hello
- [ ] No 401, 429, or network errors

### 4. Example prompts (5 min)

```bash
python claude_demo.py --all    # or: npm run demo:all
```

- [ ] All three examples produce relevant output
- [ ] Walk through Example 1 (discovery → proposal) **system** vs **user** split (see [EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md))
- [ ] Client identifies which example maps closest to their daily work

### 5. "Can you rebuild without me?" test (5 min)

Ask the client to explain back:

- [ ] Where the API key lives and how to rotate it
- [ ] Which file to edit to add a new prompt
- [ ] Which env var changes the model
- [ ] Where to read if something breaks ([SETUP_GUIDE.md § Troubleshooting](./SETUP_GUIDE.md#6-troubleshooting))

---

## Common live issues and fixes

| Issue on call | Quick fix |
|---------------|-----------|
| `command not found: python` | Try `python3` instead |
| `pip: command not found` | Install Python from python.org or use `python3 -m pip` |
| Permission denied on npm | Avoid `sudo npm`; use nvm or fix npm prefix |
| Key works for you but not client | Client may have extra spaces in `.env`; re-copy key |
| Corporate firewall | IT must allow `api.anthropic.com:443` |

---

## After the call — deliverables confirmation

- [ ] Demo script produces valid Claude responses on **client's** machine (acceptance criterion)
- [ ] Client has [SETUP_GUIDE.md](./SETUP_GUIDE.md) and [EXTENSION_GUIDE.md](./EXTENSION_GUIDE.md)
- [ ] Three example prompts reviewed ([EXAMPLE_PROMPTS.md](./EXAMPLE_PROMPTS.md))
- [ ] Optional: schedule a 2-week follow-up to review first custom prompts they added

---

## Notes space

Use this section during the call for client-specific details:

| Item | Value |
|------|-------|
| Preferred stack (Python / Node) | |
| Primary use case #1 (e.g. discovery → proposals) | |
| Primary use case #2 (e.g. weekly client updates) | |
| Monthly usage budget | |
| Follow-up date | |
