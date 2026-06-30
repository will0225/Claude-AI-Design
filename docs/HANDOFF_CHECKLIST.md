# Handoff Checklist — Verification Call

Use this checklist during your screen-share to confirm everything works on the client's machine. Target time: 30–40 minutes.

**Client priority:** Branded proposals and reports without repeating fonts, colors, or format every time.

---

## Before the call (client prep)

Send the client this list 24 hours ahead:

- [ ] Anthropic account created at [console.anthropic.com](https://console.anthropic.com)
- [ ] API key created and saved in a password manager
- [ ] Python 3.9+ **or** Node 18+ installed
- [ ] Repo cloned or zip downloaded
- [ ] **Brand info ready:** hex color codes, font names, company contact details (from brand guide or existing proposal PDF)
- [ ] One sample set of raw notes they would normally turn into a proposal or report

---

## During the call — step by step

### 1. Explain why chat failed (3 min)

- [ ] Client understands: chat memory ≠ permanent brand storage
- [ ] Show `brand/brand.config.yaml` as the single source of truth
- [ ] Confirm: "You edit this file once, not tell Claude 22 times"

### 2. Brand setup — live (10 min)

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
```

- [ ] Client fills in **company name**, **hex colors**, **fonts**, **writing style**
- [ ] Run: `python generate_document.py --show-brand`
- [ ] Output shows their company name and colors — no ⚠ placeholder warnings

### 3. API key (5 min)

- [ ] Copy `python/.env.example` → `python/.env`
- [ ] Paste API key (mask on screen)
- [ ] `pip install -r requirements.txt`

### 4. Generate branded proposal (7 min)

```bash
python generate_document.py proposal --input ../brand/samples/proposal-notes.txt
```

- [ ] Script runs without asking about fonts or colors
- [ ] HTML saved to `brand/output/`
- [ ] Open in browser — client's colors and fonts visible in header/sections
- [ ] Print preview → PDF looks on-brand

### 5. Generate branded report (5 min)

```bash
python generate_document.py report --input ../brand/samples/report-notes.txt
```

- [ ] Report uses same brand automatically (no re-entry)
- [ ] Section order matches `report.sections` in config

### 6. Client's own content (5 min)

- [ ] Client pastes their real notes into a text file
- [ ] Run: `python generate_document.py proposal --input their-notes.txt`
- [ ] Output is usable with minimal edits; `[FILL IN]` only where their notes were thin

### 7. "Can you rebuild without me?" test (5 min)

Client explains back:

- [ ] Where brand lives (`brand/brand.config.yaml`) and how to update colors/fonts
- [ ] Command to generate a proposal vs. a report
- [ ] Where output files save (`brand/output/`)
- [ ] How to sync brand to Claude.ai Project instructions (optional no-code path — see [BRAND_SETUP.md](./BRAND_SETUP.md))

---

## Acceptance criteria

- [ ] Branded HTML proposal generated on **client's machine** without Claude asking brand questions
- [ ] Client can edit `brand.config.yaml` and see changes on next generation
- [ ] Client knows how to go from HTML → PDF

---

## Common live issues

| Issue | Fix |
|-------|-----|
| Claude asks about colors anyway | Using blank claude.ai chat — must use `generate_document.py` or Project with synced config |
| Fonts wrong in PDF | Add Google Fonts URLs to config, or install custom fonts locally |
| All `[FILL IN]` placeholders | Input notes too thin — add client name, budget, dates |
| `Brand config not found` | Forgot `cp brand.config.example.yaml brand.config.yaml` |

---

## Notes space

| Item | Value |
|------|-------|
| Company name | |
| Primary color (hex) | |
| Heading / body fonts | |
| Proposal sections they want | |
| Report sections they want | |
| Follow-up date | |
