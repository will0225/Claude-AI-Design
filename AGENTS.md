# AGENTS.md

## Cursor Cloud specific instructions

This repo is the **Claude AI Setup Kit** — two standalone demo "apps" (`python/` and `node/`)
that call the Anthropic Claude API. There is no web UI, no build step, and no test suite or
linter configured; the deliverable is the demo scripts plus the docs in `docs/`.

### Running the demos

- **Required secret:** both demos need `ANTHROPIC_API_KEY` (a real key from
  https://console.anthropic.com/settings/keys). Without it the scripts exit 1 with a
  `❌ ANTHROPIC_API_KEY is not set` guard message — that is expected, not a bug.
- The key can be supplied either as an environment variable (works directly, e.g. when set as
  a Cursor secret) **or** via a `.env` file in `python/` / `node/` (`cp .env.example .env`).
  `python-dotenv` / `dotenv` do **not** override an already-exported env var, so the injected
  secret takes precedence.
- **Python:** dependencies live in the `python/.venv` virtualenv (created by the update script).
  Run with `python/.venv/bin/python python/claude_demo.py` (add `--all` or `--example <name>`).
- **Node:** run from the `node/` folder: `npm run demo` (smoke test) or `npm run demo:all`.
- Default model is `claude-sonnet-4-6`; override with the `CLAUDE_MODEL` env var.

### Notes

- `python3-venv` is a system package (already provisioned in the VM image); the update script
  only refreshes the venv + node deps, it does not install system packages.
- Network access to `api.anthropic.com` is required; a bare request returns HTTP 401 until a
  valid key is provided.
