# Handoff Checklist — Verification Call

Use this checklist during your screen-share to confirm everything works on the client's machine. Target time: 30–40 minutes.

**Client priority:** Downloaded info → same proposal or report template every time. No repeated brand questions.

---

## Before the call (client prep)

Send the client this list 24 hours ahead:

- [ ] Anthropic account + API key ready
- [ ] Python 3.9+ installed
- [ ] Repo cloned
- [ ] **Brand info ready:** hex colors, font names, company contact details
- [ ] **One downloaded file** they would normally turn into a proposal or report (saved as .txt or .csv)

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

### 4. Download → proposal (7 min)

```bash
# Client drops their downloaded file into brand/inbox/
cp ~/Downloads/their-notes.txt ../brand/inbox/

python make.py proposal
```

- [ ] Script picks up newest inbox file automatically
- [ ] No questions about fonts, colors, or format
- [ ] HTML saved to `brand/output/`
- [ ] Section order matches their proposal template exactly
- [ ] Open in browser → Print preview → PDF

### 5. Download → report (5 min)

```bash
cp ../brand/samples/report-notes.txt ../brand/inbox/
python make.py report
```

- [ ] Report uses **same brand**, different fixed section order
- [ ] Layout identical to every future report — only content changes
- [ ] Inbox file moved to `brand/inbox/done/`

### 6. Client's own download (5 min)

- [ ] Client drops their real file in `brand/inbox/`
- [ ] Run `python make.py proposal` or `python make.py report`
- [ ] Output is usable with minimal edits; `[FILL IN]` only where source data was thin

### 7. "Can you rebuild without me?" test (5 min)

Client explains back:

- [ ] Where to drop downloaded files (`brand/inbox/`)
- [ ] Command for proposal vs. report (`python make.py proposal` / `report`)
- [ ] Where output saves (`brand/output/`)
- [ ] Where to edit template sections (`brand/brand.config.yaml`)

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
