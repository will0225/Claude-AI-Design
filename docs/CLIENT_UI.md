# Report Studio — Client Guide

**No coding required.** Use the web app to upload property notes and generate branded Standard Review reports.

---

## Start the app (one time per session)

### Mac / Windows / Linux

Double-click is not set up by default — ask your IT person to run once, or open Terminal and run:

```bash
./start-app.sh
```

Your browser opens to: **http://127.0.0.1:8765**

Leave the terminal window open while using the app.

---

## What you see

```
┌─────────────────────────────────────────────────────────────┐
│  HVAC Asset Management — Report Studio          [Ready]     │
├──────────────────┬──────────────────────────────────────────┤
│  1. Upload notes │                                          │
│  2. Generate     │     Live document preview                │
│  3. Sample demo  │     (report appears here)                │
│                  │                                          │
│  Recent docs     │  [Print / Save PDF]  [Download]          │
└──────────────────┴──────────────────────────────────────────┘
```

---

## Daily workflow

### 1. Upload
Drag your property notes file (.txt, .md, or .csv) into the upload box.

### 2. Generate
Click **Generate Standard Review Report** (or **Generate Proposal**).

Wait 30–60 seconds. The report appears in the preview panel on the right.

### 3. Save as PDF
Click **Print / Save PDF** → choose "Save as PDF" in the print dialog.

---

## Buttons explained

| Button | What it does |
|--------|----------------|
| **Generate Standard Review Report** | Creates a forensic report from your uploaded notes |
| **Generate Proposal** | Creates a proposal using the same brand format |
| **Generate sample Northgate report** | Demo with included SRA Northgate data — no upload needed |
| **Brand & format preview** | Shows colors, fonts, and section layout |
| **Northgate reference report** | Opens the master format from Claude Design |
| **Recent documents** | Click any past report to preview it again |

---

## First-time setup (administrator — once)

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
cp python/.env.example python/.env    # add ANTHROPIC_API_KEY
pip install -r python/requirements.txt
```

Brand colors, fonts, and sections are already configured for HVAC Asset Management.

---

## Troubleshooting

| Message | Fix |
|---------|-----|
| Setup needed | Run the first-time setup commands above |
| API key needed | Add key to `python/.env` |
| Upload a file first | Drag property notes into Step 1 |
| Cannot connect | Make sure `./start-app.sh` is still running |

---

## For your verification call

1. Run `./start-app.sh`
2. Click **Brand & format preview** — confirm colors match your style guide
3. Click **Northgate reference report** — side-by-side with Claude Design
4. Click **Generate sample Northgate report** — full report with real data
5. **Print / Save PDF** — confirm PDF looks correct

You never need to edit code or run `python make.py` manually.
