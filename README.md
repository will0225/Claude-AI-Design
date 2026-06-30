# Claude Brand Document Kit

Generate **branded proposals and reports** with Claude — your company fonts, colors, and writing style applied automatically. Set up once in `brand/brand.config.yaml`; never tell Claude your brand again.

## The problem this solves

> "I've told Claude my fonts and colors 22 times and it still asks me."

Chat memory doesn't persist brand rules. This kit stores them in a **config file** and injects them into every API call automatically — zero repeated questions.

## Quick start

### 1. One-time brand setup

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
# Edit brand.config.yaml — your company name, hex colors, fonts, writing style
```

Full walkthrough → [docs/BRAND_SETUP.md](./docs/BRAND_SETUP.md)

### 2. API key

```bash
cd python && cp .env.example .env   # add ANTHROPIC_API_KEY
pip install -r requirements.txt
```

### 3. Generate a branded document

```bash
# Proposal from sample notes
python generate_document.py proposal --input ../brand/samples/proposal-notes.txt

# Report from sample data
python generate_document.py report --input ../brand/samples/report-notes.txt

# Verify brand loaded
python generate_document.py --show-brand
```

Output saves to `brand/output/*.html` → open in browser → Print → Save as PDF.

## What's included

| Deliverable | Location |
|-------------|----------|
| **Brand config (edit once)** | `brand/brand.config.example.yaml` → `brand.config.yaml` |
| **Proposal/report generator (Python)** | `python/generate_document.py` |
| **Proposal/report generator (Node.js)** | `node/generate_document.js` |
| **Brand setup guide** | [docs/BRAND_SETUP.md](./docs/BRAND_SETUP.md) |
| **API & account setup** | [docs/SETUP_GUIDE.md](./docs/SETUP_GUIDE.md) |
| **How to extend** | [docs/EXTENSION_GUIDE.md](./docs/EXTENSION_GUIDE.md) |
| **Example prompts + rationale** | [docs/EXAMPLE_PROMPTS.md](./docs/EXAMPLE_PROMPTS.md) |
| **Handoff checklist** | [docs/HANDOFF_CHECKLIST.md](./docs/HANDOFF_CHECKLIST.md) |
| **Sample input notes** | `brand/samples/proposal-notes.txt`, `report-notes.txt` |

## Commands

```bash
# Branded documents (primary workflow)
python generate_document.py proposal --input my-notes.txt
python generate_document.py report --input my-data.txt
python generate_document.py --show-brand

# API smoke test
python claude_demo.py

# Node.js equivalents
npm run brand
npm run generate:proposal
npm run generate:report
```

## Requirements

- Anthropic API key ([get one here](https://console.anthropic.com/settings/keys))
- Python 3.9+ **or** Node.js 18+
- Your brand hex colors and font names (from brand guide, Canva, or website)

## Security

- Never commit `brand/brand.config.yaml` (client-specific) or `.env` (API keys)
- Both are in `.gitignore`

## License

MIT — use and adapt freely for your projects.
