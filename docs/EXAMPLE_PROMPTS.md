# Three Example Prompts (and Why They Work)

These examples match the client's core need: **branded proposals and reports without repeating fonts, colors, or format**.

The recommended workflow is `generate_document.py`, which loads `brand/brand.config.yaml` automatically. The patterns below explain *why* that design works — and how to tune it.

---

## Example 1 — Branded proposal from discovery notes

### Use case

Turn discovery call notes into a fully styled proposal HTML file — company colors, fonts, and section structure applied with zero brand questions.

### How to run

```bash
python generate_document.py proposal --input ../brand/samples/proposal-notes.txt
```

### What Claude receives (automatic)

**System prompt (from `brand.config.yaml` — you never paste this):**

```
Company: [your company]
Colors: primary #..., secondary #..., accent #...
Fonts: [heading] / [body]
Writing style: professional, no exclamation marks, …
Proposal sections: Executive Summary → Understanding Your Needs → …
NEVER ask about brand colors, fonts, or structure.
```

**User message (you provide):**

```
Create a proposal from the following source material…
--- SOURCE MATERIAL ---
[paste discovery notes]
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Config file as system prompt** | Brand rules are sent on *every* call — not stored in chat memory that gets lost. |
| **Explicit "never ask" rules** | Stops the "50 questions" loop about colors and fonts. |
| **`[FILL IN]` for missing project data** | Only project-specific gaps get placeholders — not brand basics. |
| **Fixed section schema in YAML** | Proposal structure lives in config; reorder sections without rewriting prompts. |

### When to adapt

- Edit `proposal.sections` in `brand.config.yaml` to match their real proposal template.
- Add pricing tiers or terms sections as needed.

---

## Example 2 — Branded quarterly report

### Use case

Turn raw performance data and bullet notes into a client-ready report with the same brand as proposals — no second setup.

### How to run

```bash
python generate_document.py report --input ../brand/samples/report-notes.txt
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Shared brand config** | Proposals and reports pull from the same `brand.config.yaml` — one source of truth. |
| **Separate section templates** | `report.sections` defines report-specific structure without duplicating colors/fonts. |
| **HTML + embedded CSS output** | Browser-rendered document with exact hex values; Print → PDF for delivery. |
| **Consistent writing_style block** | Tone and voice identical across all document types. |

### When to adapt

- Customize `report.sections` for monthly vs. quarterly vs. audit reports.
- Increase `max_tokens` in `generate_document.py` for very long data sets.

---

## Example 3 — Claude.ai Project (no-code backup)

### Use case

For clients who prefer the Claude website: sync the brand config into a Project so web chats also stop asking.

### Setup (one time)

1. Create Project: **"Proposals & Reports"**
2. Paste into **Project instructions**:

```
NEVER ask the user for brand colors, fonts, company name, or document structure.
Use [FILL IN: …] for missing project details only.

[paste entire contents of brand.config.yaml]
```

3. Always start document work **inside this Project**.

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Project-level instructions** | Persists across conversations within the Project (better than blank chat). |
| **Same YAML content** | Client maintains one file; copy updates to Project when brand changes. |
| **Explicit never-ask header** | Blocks the repeated "what are your brand colors?" questions. |

### Limitation

Project instructions can drift if edited manually. The **API + config file** approach in `generate_document.py` is more reliable for production use.

---

## Why telling Claude 22 times didn't work

```
❌ Blank chat → paste brand → ask for proposal → new chat → brand gone
❌ Long chat → early brand info truncated → Claude asks again
❌ Projects without strict rules → Claude still clarifies "just to confirm your colors…"

✅ brand.config.yaml → injected every API call → brand always present
```

---

## Prompt design cheat sheet (for brand documents)

1. **Brand in system prompt** — colors, fonts, tone, sections (loaded from YAML).
2. **Content in user message** — only project-specific notes and data.
3. **Never-ask list** — explicitly block questions about design and format.
4. **Placeholder rule** — `[FILL IN: …]` instead of clarifying questions.
5. **Output format** — HTML with embedded CSS using exact hex and font names.

---

## Run commands

```bash
python generate_document.py --show-brand
python generate_document.py proposal --input my-notes.txt
python generate_document.py report --input my-data.txt
```

See [BRAND_SETUP.md](./BRAND_SETUP.md) for the full one-time setup walkthrough.
