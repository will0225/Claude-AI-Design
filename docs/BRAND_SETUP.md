# Brand Setup — Stop Repeating Your Fonts and Colors

Your client told Claude their brand **22 times** and it still asks. This guide explains why that happens and how this repo fixes it permanently.

---

## Why Claude keeps asking (even in Projects)

| Approach | What goes wrong |
|----------|-----------------|
| **New chat each time** | No memory. Every session starts blank. |
| **"Remember my brand" in chat** | Not reliable. Long chats truncate earlier context. |
| **Claude Projects (Custom Instructions)** | Better, but easy to overwrite, hard to version, and still drifts across conversations. |
| **Pasting brand info into every prompt** | Works once, tedious forever. |

**Root cause:** Brand rules live in *conversation memory* instead of a *config file* that is injected automatically on every call.

**The fix:** Put fonts, colors, tone, and document structure in `brand/brand.config.yaml` **once**. Every script reads it and sends it to Claude in the **system prompt** — before Claude sees your notes. Claude never needs to ask.

---

## One-time setup (15 minutes)

### Step 1 — Copy the brand config

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
```

Open `brand/brand.config.yaml` in any text editor.

### Step 2 — Fill in your company details

```yaml
company:
  name: "Brightline Marketing"
  tagline: "Strategy that scales"
  website: "https://brightline.example.com"
  contact_email: "hello@brightline.example.com"
```

### Step 3 — Add your exact colors (hex codes)

Get hex values from your brand guide, Canva brand kit, or a designer. Example:

```yaml
colors:
  primary: "#0B3D5C"      # your main brand color
  secondary: "#14748F"
  accent: "#E8913A"
  text: "#1A1A1A"
  text_light: "#6B7280"
  background: "#FFFFFF"
  surface: "#F3F4F6"
  border: "#E5E7EB"
```

> **Tip:** Use a color picker on your existing proposal PDF or website logo to grab exact hex values.

### Step 4 — Add your fonts

```yaml
fonts:
  heading: "Montserrat"
  body: "Open Sans"
  heading_url: "https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&display=swap"
  body_url: "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap"
```

If you use **custom/licensed fonts** (e.g. from Adobe Fonts), set the font name and leave URLs blank — install the fonts on your computer so they render when you print to PDF.

### Step 5 — Set your writing style (no more tone questions)

```yaml
writing_style:
  tone: "professional, confident, approachable"
  voice: 'Use first-person plural ("we", "our")'
  avoid:
    - "jargon"
    - "exclamation marks"
  paragraph_style: "2–4 sentences per paragraph"
  audience: "business decision-makers"
```

### Step 6 — Verify

```bash
cd python
python generate_document.py --show-brand
```

You should see:

```
✓ Brand loaded: Brightline Marketing | primary #0B3D5C | fonts Montserrat / Open Sans
```

Fix any ⚠ warnings before generating documents.

---

## Generate a proposal or report (zero brand questions)

### Proposal from discovery notes

```bash
cd python
python generate_document.py proposal --input ../brand/samples/proposal-notes.txt
```

### Report from data/notes

```bash
python generate_document.py report --input ../brand/samples/report-notes.txt
```

### Output

HTML files save to `brand/output/`. Open in Chrome/Safari → **Print → Save as PDF**.

Every output automatically includes:
- Your company name, tagline, contact info
- Your exact hex colors in headers, tables, accents
- Your heading and body fonts
- Your proposal or report section structure
- Your writing tone and voice

**Claude will not ask** about fonts, colors, or format. If a project detail is missing (e.g. exact budget), it inserts `[FILL IN: …]` placeholders instead of 50 questions.

---

## What gets sent to Claude (behind the scenes)

Every generation call looks like this:

```
SYSTEM PROMPT (automatic — from brand.config.yaml):
  Company: Brightline Marketing
  Colors: primary #0B3D5C, secondary #14748F, …
  Fonts: Montserrat / Open Sans
  Writing style: professional, no exclamation marks, …
  Proposal sections: Executive Summary → Understanding Your Needs → …
  RULE: Never ask about brand. Use [FILL IN] for missing project details.

USER MESSAGE (you provide):
  Create a proposal from these notes: [your pasted content]
```

You only provide **project content**. Brand is handled automatically.

---

## Also works in Claude.ai (no-code path)

If the client prefers the Claude website over scripts:

1. Go to [claude.ai](https://claude.ai) → **Projects** → Create project: "Proposals & Reports"
2. Open **Project instructions**
3. Copy the entire contents of their filled-in `brand.config.yaml` into the instructions
4. Add this line at the top:

   ```
   NEVER ask the user for brand colors, fonts, company name, or document structure.
   These are defined below. Use [FILL IN: …] for missing project details only.
   ```

5. Always start proposals/reports **inside this Project** — not a blank chat.

The YAML file is still the master copy. When brand changes, update the file **and** sync Project instructions.

---

## Updating your brand later

Edit one file:

```bash
# Change a color or font
nano brand/brand.config.yaml

# Verify
python generate_document.py --show-brand

# Next document automatically uses the new brand
python generate_document.py proposal --input my-notes.txt
```

No retraining. No telling Claude again.

---

## Customizing proposal vs. report sections

Edit the `proposal.sections` or `report.sections` lists in `brand.config.yaml`:

```yaml
proposal:
  sections:
    - name: "Cover Letter"
      description: "Personalized opening paragraph"
    - name: "Scope of Work"
      description: "Detailed deliverables with acceptance criteria"
    # add, remove, or reorder as needed
```

The next generated document follows the new structure automatically.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Claude still asks brand questions | Ensure you're using `generate_document.py`, not a blank claude.ai chat |
| Wrong colors in output | Check hex values in `brand.config.yaml`; re-run `--show-brand` |
| Fonts look wrong in PDF | Install fonts locally, or use Google Fonts URLs in config |
| `[FILL IN: …]` everywhere | Add more detail to your input notes file — brand is fine, content is thin |
| `Brand config not found` | Run `cp brand/brand.config.example.yaml brand/brand.config.yaml` |

---

## Handoff talking point

> "You told Claude your brand 22 times because chat memory doesn't persist rules reliably. We moved your fonts, colors, tone, and document structure into one config file. From now on, you paste your project notes and get a branded proposal or report — no questions about design."

See [HANDOFF_CHECKLIST.md](./HANDOFF_CHECKLIST.md) for the verification call agenda.
