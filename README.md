# Claude Brand Document Kit — HVAC Asset Management

Forensic **Standard Review** reports and proposals with a fixed template every time. Pre-configured for **HVAC Asset Management** using the real SRA Northgate H1 2026 report structure.

## Daily workflow

```
1. Drop downloaded GL notes / work orders  →  brand/inbox/
2. python make.py report
3. brand/output/*.html  →  Print → PDF
```

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
| [docs/BRAND_SETUP.md](./docs/BRAND_SETUP.md) | Colors, fonts, section customization |
| [docs/HANDOFF_CHECKLIST.md](./docs/HANDOFF_CHECKLIST.md) | Client verification call |

## Sample data

Real forensic review source: `brand/samples/sra-northgate-h1-2026-source.txt`  
(SRA Northgate · 4600 Northgate Blvd · H1 2026 · File SR-4600NOR-H1-26)

## License

MIT
