# Claude Brand Document Kit

**Download information → drop in inbox → get the same proposal or report every time.**

Your fonts, colors, and section layout are set once. After that, you only provide the raw content.

## Daily workflow (3 steps)

```
1. Save/download info  →  brand/inbox/
2. Run one command     →  python make.py proposal   OR   python make.py report
3. Open output         →  brand/output/*.html  →  Print → PDF
```

Full guide → [docs/WORKFLOW.md](./docs/WORKFLOW.md)

## One-time setup

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
# Edit: company name, hex colors, fonts, section names

cd python && cp .env.example .env   # add ANTHROPIC_API_KEY
pip install -r requirements.txt
```

## Commands

```bash
cd python

python make.py proposal              # inbox → fixed proposal template
python make.py report                # inbox → fixed report template
python make.py proposal --file notes.txt

python generate_document.py --show-brand   # verify brand config
```

From repo root:

```bash
chmod +x make-proposal.sh make-report.sh
./make-proposal.sh
./make-report.sh
```

## Two fixed templates

| Template | Sections (always same order) |
|----------|------------------------------|
| **Proposal** | Executive Summary → Understanding Your Needs → Proposed Approach → Timeline & Investment → Why Work With Us → Next Steps |
| **Report** | Executive Summary → Scope & Methodology → Key Findings → Analysis → Recommendations → Appendix |

Customize sections in `brand/brand.config.yaml`.

## What's included

| Deliverable | Location |
|-------------|----------|
| **Drop folder for downloads** | `brand/inbox/` |
| **One-command generator** | `python/make.py`, `node/make.js` |
| **Brand config (edit once)** | `brand/brand.config.yaml` |
| **Daily workflow guide** | [docs/WORKFLOW.md](./docs/WORKFLOW.md) |
| **Brand setup guide** | [docs/BRAND_SETUP.md](./docs/BRAND_SETUP.md) |
| **Handoff checklist** | [docs/HANDOFF_CHECKLIST.md](./docs/HANDOFF_CHECKLIST.md) |

## The problem this solves

> "I've told Claude my fonts and colors 22 times and it still asks."

> "When I download information I need it in a report or proposal that are always the same."

Brand rules and document structure live in a **config file + fixed HTML template** — injected automatically. Claude only fills in the content for each section.

## Requirements

- Anthropic API key ([get one here](https://console.anthropic.com/settings/keys))
- Python 3.9+ or Node.js 18+

## License

MIT
