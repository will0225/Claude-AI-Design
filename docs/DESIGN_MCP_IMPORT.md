# Import from Claude Design MCP

Use the official **`claude_design`** MCP to pull your Design page into this repo — so colors, fonts, and format are always referenceable.

**Design project:** [575aeb46-b224-4fc6-9f4d-29bacdbcf962](https://claude.ai/design/p/575aeb46-b224-4fc6-9f4d-29bacdbcf962)  
**Reference file:** `Standard Review - 4600 Northgate.dc.html`

---

## Why the Design page alone doesn't work

Claude's Design page **saves** your colors, fonts, and layout — but there is no `@design` command Claude can call in chat. Settings live in UI memory, not a file the API reads automatically.

This repo fixes that:

| Layer | Role |
|-------|------|
| **Claude Design** (claude.ai/design) | Where you design and iterate visually |
| **`claude_design` MCP** | Pulls the `.dc.html` file into the repo |
| **`brand/design/*.dc.html`** | Permanent reference — colors, fonts, layout |
| **`brand.config.yaml`** | Tokens extracted for `make.py` |
| **`make.py report`** | New data → same format every time |

---

## Step 1 — Authenticate (once per machine)

In **Claude Code** (not claude.ai chat):

```
/design-login
```

Complete the browser OAuth flow. Verify:

```bash
jq -r '.designOauth.accessToken' ~/.claude/.credentials.json | head -c 20
# Should print token prefix (not empty)
```

Export the token:

```bash
export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)
```

> **Note:** This is **not** your `ANTHROPIC_API_KEY`. Design uses a separate OAuth token with `user:design:read` / `user:design:write` scopes.

---

## Step 2 — MCP config

This repo includes `.mcp.json`:

```json
{
  "mcpServers": {
    "claude_design": {
      "type": "http",
      "url": "https://api.anthropic.com/v1/design/mcp"
    }
  }
}
```

In Claude Code, after `/design-login`, run `/mcp` to reconnect. You should see `claude_design` connected.

---

## Step 3 — Import the Standard Review design

```bash
cd python
export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)

# List available MCP tools
python import_design.py --list-tools

# Import from your Design project
python import_design.py \
  --project 575aeb46-b224-4fc6-9f4d-29bacdbcf962 \
  --file "Standard Review - 4600 Northgate.dc.html"
```

Output saves to: `brand/design/Standard Review - 4600 Northgate.dc.html`

---

## Step 4 — Implement as format guide

```bash
python implement_format_guide.py
# Syncs CSS + HTML shell from .dc.html → document.css + fixed_document.html
python sync_design.py
# Reads CSS variables from .dc.html → updates brand/brand.config.yaml
```

Verify:

```bash
python design.py preview
# Opens brand/output/design-preview.html
```

---

## Step 5 — Generate new reports (same format)

```bash
# Drop new property data in inbox
cp my-new-property-notes.txt ../brand/inbox/

python make.py report
# Same layout as Standard Review — new content only
```

---

## Fallback (already in repo)

If MCP import fails (auth, 404, network), a **reference implementation** is already committed:

```
brand/design/Standard Review - 4600 Northgate.dc.html
```

Built from your real SRA Northgate H1 2026 data. Open it in a browser to verify colors, fonts, and section format.

To refresh from Design when MCP works:

```bash
python import_design.py   # overwrites with live Design file
python implement_format_guide.py
python sync_design.py     # re-extract tokens
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `DESIGN_OAUTH_TOKEN not set` | Run `/design-login` in Claude Code |
| MCP 404 on `/v1/design/mcp` | Known bug — ensure Claude Code ≥ 2.1.181 and design OAuth token (not API key) is used |
| MCP 401 | Re-run `/design-login`; token expired |
| Import succeeds but layout wrong | Re-export from Design UI; run `import_design.py` again |
| "Use my saved design" in chat still fails | Use `make.py` — chat cannot reference Design page reliably |

---

## Architecture

```
Claude Design (UI)
       ↓  /design-login + import_design.py
brand/design/Standard Review - 4600 Northgate.dc.html   ← permanent reference
       ↓  sync_design.py
brand/brand.config.yaml                                 ← colors, fonts, sections
       ↓  make.py report
brand/output/*.html                                     ← new properties, same format
```

See also: [DESIGN_PAGE.md](./DESIGN_PAGE.md) · [WORKFLOW.md](./WORKFLOW.md)
