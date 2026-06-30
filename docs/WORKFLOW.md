# Daily Workflow — Download → Same Template Every Time

Your downloaded information goes into **one of two fixed templates**. The layout, fonts, colors, and section order never change — only the content updates.

---

## The two templates

| You need… | Command | Same every time |
|-----------|---------|-----------------|
| **Proposal** | `python make.py proposal` | Executive Summary → Understanding Your Needs → Proposed Approach → Timeline & Investment → Why Work With Us → Next Steps |
| **Report** | `python make.py report` | Executive Summary → Scope & Methodology → Key Findings → Analysis → Recommendations → Appendix |

Section names and order live in `brand/brand.config.yaml`. Edit once if your company uses different headings.

---

## Daily steps (3 moves)

### 1. Download or save your information

Copy anything into `brand/inbox/`:

- Meeting notes you typed or exported
- CSV or data exports
- Copied web research
- Email thread summaries

Supported: `.txt`, `.md`, `.csv`, `.json`

### 2. Run one command

```bash
cd python

# Newest file in inbox → proposal (always same layout)
python make.py proposal

# Newest file in inbox → report (always same layout)
python make.py report
```

Or point at a specific file:

```bash
python make.py proposal --file ~/Downloads/client-notes.txt
python make.py report --file ~/Downloads/q2-metrics.csv
```

### 3. Open the output

```
brand/output/your-company-proposal-….html
```

Open in browser → **Print → Save as PDF**.

The processed inbox file moves to `brand/inbox/done/` automatically.

---

## Why it's always the same

```
Downloaded notes
      ↓
Claude fills CONTENT into fixed section keys (JSON)
      ↓
Fixed HTML template applies your fonts + colors + section order
      ↓
Identical layout every time — only words change
```

Claude does **not** redesign the document each time. It only writes the text for each section. Your template handles the rest.

---

## One-time setup (do this once)

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
# Edit: company name, hex colors, fonts, section names

cd python && cp .env.example .env
# Add ANTHROPIC_API_KEY

pip install -r requirements.txt
```

Details → [BRAND_SETUP.md](./BRAND_SETUP.md)

---

## Changing your template

Edit `brand/brand.config.yaml`:

```yaml
proposal:
  sections:
    - name: "Cover Letter"
      description: "Personalized opening"
    - name: "Scope of Work"
      description: "Deliverables list"
    # reorder, add, or remove sections
```

Next `python make.py proposal` uses the updated structure automatically.

---

## Node.js

```bash
cd node
npm install
node make.js proposal
node make.js report
```

---

## Quick reference

| Task | Command |
|------|---------|
| Drop files | Save to `brand/inbox/` |
| Make proposal | `python make.py proposal` |
| Make report | `python make.py report` |
| Specific file | `python make.py report --file path.txt` |
| Check brand loaded | `python generate_document.py --show-brand` |
| Output location | `brand/output/` |
