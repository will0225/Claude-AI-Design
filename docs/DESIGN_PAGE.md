# Why Claude's Design Page Can't Be Referenced (And What To Use Instead)

You save colors, fonts, and format on Claude's **Design page** — but Claude keeps asking anyway or produces a different layout each time. This is a known limitation, not something you're doing wrong.

---

## What the Design page actually does

| What you think happens | What actually happens |
|------------------------|----------------------|
| Design is saved permanently | Saved in **that Project or conversation context** |
| Claude "references" your design | Claude **re-reads** design from chat memory — when it remembers |
| Same format every time | Each new chat may start **without** design context |
| "Use my saved design" works | Claude has **no stable ID** to pull design from |

**Claude's Design page has no API hook.** There is no `@design` or "load design profile X" command. When you say "use my design," Claude guesses from whatever is still in context — which is why you've entered it 22 times.

---

## The fix: one file = your permanent Design page

In this repo, **`brand/brand.config.yaml`** is your Design page — but stored as a file the scripts **always inject** before Claude sees your data.

```
Claude.ai Design page          →    brand/brand.config.yaml
(colors, fonts, format)             (colors, fonts, format)
        ↓                                    ↓
   chat memory (unreliable)          system prompt (every call)
```

---

## One-time migration: copy Design page → config file

### Step 1 — Open both side by side

- **Left:** Claude Design page (your saved colors, fonts, format)
- **Right:** `brand/brand.config.yaml` (copy from example first)

```bash
cp brand/brand.config.example.yaml brand/brand.config.yaml
```

### Step 2 — Copy each value across

| Design page setting | Config file location |
|---------------------|---------------------|
| Primary color | `colors.primary: "#0f2744"` |
| Secondary / accent colors | `colors.secondary`, `colors.accent` |
| Heading font | `fonts.heading: "Libre Franklin"` |
| Body font | `fonts.body: "Source Sans 3"` |
| Report section order | `report.sections` (00–05 list) |
| Proposal section order | `proposal.sections` |
| Company name / contact | `company.name`, `contact_email`, etc. |
| Confidential banner text | `document_labels.confidential` |

Use **hex codes** for colors (e.g. `#0f2744`), not color names.

### Step 3 — Verify design loaded

```bash
cd python
python design.py show      # prints exactly what Claude receives
python design.py preview   # opens design-preview.html in brand/output/
```

If the preview matches your Design page → you're done forever.

---

## How documents reference design automatically

When you run:

```bash
python make.py report
```

This happens **before** Claude sees your downloaded notes:

```
1. Script reads brand/brand.config.yaml
2. Builds DESIGN PROFILE REFERENCE block (colors, fonts, format)
3. Sends it in the system prompt — Claude cannot miss it
4. Claude returns JSON content only (words, tables, findings)
5. Fixed HTML template applies your design — same layout every time
```

You never say "use my design." The script **references it for you** on every call.

---

## Commands

```bash
python design.py show       # What design Claude receives
python design.py export     # Save design-reference.txt (backup)
python design.py preview    # Visual proof — colors, fonts, sections

python make.py report       # Uses design automatically
python make.py proposal     # Same design, different format
```

---

## If you still use Claude.ai for other tasks

Export your design once and paste into **Project instructions**:

```bash
python design.py export
# Opens brand/output/design-reference.txt — paste into Project settings
```

Add this line at the top:

```
NEVER ask for brand colors, fonts, or document format. Design profile is below.
For reports and proposals, use the make.py script instead — it references design automatically.
```

But for **reports and proposals**, always use `make.py` — not a blank chat.

---

## Changing your design later

Edit one file:

```bash
nano brand/brand.config.yaml   # change a color or font
python design.py preview       # verify
python make.py report          # next document uses new design
```

No re-entering on Claude's Design page. No 50 questions.

---

## Quick answer for your client

> "Claude's Design page saves settings in the chat — it can't reference them like a file. We moved your colors, fonts, and format into `brand.config.yaml`. Every report command injects that design automatically. You drop in data, you get the same formatted document out."

See also: [WORKFLOW.md](./WORKFLOW.md) · [BRAND_SETUP.md](./BRAND_SETUP.md)
