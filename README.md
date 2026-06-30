# Claude Brand Document Kit — HVAC Asset Management

Forensic **Standard Review** reports and proposals with a fixed template every time. Pre-configured for **HVAC Asset Management** using the real SRA Northgate H1 2026 report structure.

## Daily workflow

```
1. Drop downloaded GL notes / work orders  →  brand/inbox/
2. python make.py report
3. brand/output/*.html  →  Print → PDF
```

**Official style guide applied:** `brand/HAM_Report_Style_Guide.pdf`

| Color | Hex |
|-------|-----|
| Teal | `#184C4C` |
| Bronze | `#9C7B4D` |
| Ink | `#1A2731` |
| Paper | `#FBF9F5` |
| Critical / High / Medium | `#8F2018` / `#A23A2C` / `#C79A3E` |

Fonts: **Newsreader** (display) · **Public Sans** (body) · **IBM Plex Mono** (numerics)

## Claude Design import (MCP)

Your Design page project is configured in `brand.config.example.yaml`:

- Project: `575aeb46-b224-4fc6-9f4d-29bacdbcf962`
- File: `Standard Review - 4600 Northgate.dc.html`

**Reference implementation (committed):** `brand/design/Standard Review - 4600 Northgate.dc.html`  
Open in browser to see exact colors, fonts, and Standard Review format.

To pull live updates from Claude Design on your machine:

```bash
/design-login                                    # Claude Code
export DESIGN_OAUTH_TOKEN=$(jq -r '.designOauth.accessToken' ~/.claude/.credentials.json)
python import_design.py                          # MCP import
python sync_design.py                            # sync tokens → brand.config.yaml
```

Full guide → [docs/DESIGN_MCP_IMPORT.md](./docs/DESIGN_MCP_IMPORT.md)

## The Design page problem — solved

Claude's **Design page** saves colors/fonts/format in the UI but **cannot reference them** across chats. This repo uses `brand/brand.config.yaml` as your permanent Design page — injected automatically every time.

```bash
python design.py show      # exactly what Claude receives
python design.py preview   # visual proof in browser
```

Full explanation → [docs/DESIGN_PAGE.md](./docs/DESIGN_PAGE.md)

## One-time setup

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
cd python && cp .env.example .env   # ANTHROPIC_API_KEY
pip install -r requirements.txt
```

## Generate the Northgate report (real sample included)

```bash
cd python
python make.py report --file ../brand/samples/sra-northgate-h1-2026-source.txt
```

## Fixed report sections (always the same)

| # | Section |
|---|---------|
| 00 | Executive Summary |
| 01 | Financial & Contractual Baseline |
| 02 | Vendor Performance & Standard-of-Care Audit |
| 03 | Asset & Equipment Risk + Capital Plan |
| 04 | Comfort & Reliability — Hot / Cold Calls |
| 05 | Findings, Exposure & Recommendations |

Cover block always includes: File No., Review type, Prepared for, Property mgr, Review period, Issued date.

## Commands

```bash
python make.py report                              # newest inbox file
python make.py report --file path/to/download.txt  # specific file
python make.py proposal                            # proposal template
python generate_document.py --show-brand
```

## Docs

| Guide | Purpose |
|-------|---------|
| [docs/WORKFLOW.md](./docs/WORKFLOW.md) | Daily drop-and-run steps |
| [docs/DESIGN_MCP_IMPORT.md](./docs/DESIGN_MCP_IMPORT.md) | Import from Claude Design MCP |
| [docs/DESIGN_PAGE.md](./docs/DESIGN_PAGE.md) | Why Design page can't be referenced in chat |
| [docs/HANDOFF_CHECKLIST.md](./docs/HANDOFF_CHECKLIST.md) | Client verification call |

## Sample data

Real forensic review source: `brand/samples/sra-northgate-h1-2026-source.txt`  
(SRA Northgate · 4600 Northgate Blvd · H1 2026 · File SR-4600NOR-H1-26)

## License

MIT
