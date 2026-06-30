# HAM Report Style Guide — Extracted Values

Source: `HAM_Report_Style_Guide.pdf` (Report System v1)

## Color palette

| Name | Hex | Usage |
|------|-----|-------|
| Teal | `#184C4C` | Headers, part dividers, table headers, recommendation boxes |
| Bronze | `#9C7B4D` | Eyebrows, section numbers, accents, labels |
| Ink | `#1A2731` | Primary text |
| Muted | `#54514A` | Secondary text, disclaimers |
| Cream | `#F6F1E8` | Zebra rows, callout backgrounds |
| Paper tint | `#FBF9F5` | Document background (warm white, never pure #FFF) |

### Severity (findings & ratings only — never decorative)

| Level | Hex |
|-------|-----|
| Critical | `#8F2018` |
| High | `#A23A2C` |
| Medium | `#C79A3E` |
| Positive / OK | `#3C7350` |

## Typography

| Role | Font | Weights |
|------|------|---------|
| Display / section titles / large stats | **Newsreader** | 500 |
| Body / labels / finding titles | **Public Sans** | 400, 600, 700 |
| Eyebrows / dates / dollar figures / tabular nums | **IBM Plex Mono** | 400, 500, 600 |

### Type scale

| Element | Spec |
|---------|------|
| Page title (H1) | 42–58pt Newsreader |
| Section H2 | 27pt Newsreader, 1.5px hairline above, 44px top spacing |
| Sub-label H3 | 12pt Public Sans small caps, bronze |
| Body | 14pt Public Sans, line-height 1.62 |
| Eyebrow | 10–12pt Public Sans small caps, letter-spaced, bronze |

## Layout rules

- US Letter, zero page margins; teal bands full-bleed
- Text inset: **0.85in** left and right
- Tables, callouts, charts, finding cards: **never split across pages**
- Each Part begins on a new page
- Estimates must be labeled; disclaimers muted 11.5pt at end of each part

## Color governance rules

From page 1 of the PDF:

1. **Teal and bronze carry the brand** — use them for structure, headers, accents, and labels.
2. **Severity colors are reserved for findings and ratings** — never use Critical/High/Medium/Positive as decoration.
3. **Whites are warm, never pure** — page background is Paper tint (`#FBF9F5`); pure `#FFFFFF` is allowed only on cards and table row alternates, not as the document canvas.

---

## Derived colors (not named in PDF — inferred from component examples)

These appear in the Northgate reference template and `brand/styles/document.css`. They are not separate swatches on page 1 of the PDF; they are tints and neutrals derived from the official palette.

| Name | Hex | Source | Use |
|------|-----|--------|-----|
| Border | `#DDD5C8` | Derived neutral | Hairlines, card borders, table row dividers, timeline rail |
| Card white | `#FFFFFF` | Allowed exception | Stat tiles, finding cards, odd table rows |
| Critical tint | `#F5E8E6` | ~8% Critical on white | Severity badge bg, `.flag-critical` |
| High tint | `#F5EBE8` | ~8% High on white | Severity badge bg, `.flag-high` |
| Medium tint | `#F5F0E4` | ~8% Medium on white | Severity badge bg |
| Positive tint | `#E8F0EA` | ~8% Positive on white | Severity badge bg, "within range" pills |
| On-teal text | `#FFFFFF` | Contrast on Teal | Table headers, part divider titles, recommendation body |

---

## Component color map

Maps every report building block (PDF page 3) to its colors. CSS class names match `brand/styles/document.css`.

### Document shell

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Page canvas | `body` | Paper `#FBF9F5` | Ink `#1A2731` | — |
| Body copy | default | inherit | Ink `#1A2731` | — |
| Disclaimers / secondary | `.footer-disclaimer`, `.caveat-box` | inherit / Cream | Muted `#54514A` | Border `#DDD5C8` on caveat |

### Cover & header

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Doc header rule | `header.doc-header` | — | — | Bottom Border `#DDD5C8` |
| Company name (H1) | `header.doc-header h1.company-name` | — | Ink `#1A2731` | — |
| Property address | `header.doc-header p.property-address` | — | Teal `#184C4C` | — |
| Subtitle / meta | `header.doc-header p.subtitle` | — | Muted `#54514A` | — |
| Eyebrow labels | `.eyebrow`, `.doc-type` | — | Bronze `#9C7B4D` | — |
| Confidential stamp | `header.doc-header p.confidential` | — | Critical `#8F2018` | — |
| Cover meta block | `.cover-meta` | Cream `#F6F1E8` | Ink / Muted | Border `#DDD5C8`, left Bronze `#9C7B4D` 4px |

### Section structure

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Section H2 | `section.doc-section h2` | — | Ink `#1A2731` | Top hairline Border `#DDD5C8` |
| Section number | `h2 .section-num` | — | Bronze `#9C7B4D` | — |
| Sub-label H3 | `section.doc-section h3`, `.sub-label` | — | Bronze `#9C7B4D` | — |
| Part divider band | `.part-divider` | Teal `#184C4C` | White `#FFFFFF` | Left Bronze `#9C7B4D` 4px |
| Part divider eyebrow | `.part-divider .eyebrow` | Teal | Bronze `#9C7B4D` | — |

### Data & KPI blocks

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Stat tile | `.stat-tile`, `.kpi-card` | White `#FFFFFF` | — | Border `#DDD5C8` |
| Stat value (headline) | `.stat-value`, `.kpi-value` | — | Teal `#184C4C` | — |
| Stat label | `.stat-label`, `.kpi-label` | — | Muted `#54514A` | — |
| Table header row | `table.data-table thead th` | Teal `#184C4C` | White `#FFFFFF` | — |
| Table odd rows | `tr:nth-child(odd) td` | White `#FFFFFF` | Ink `#1A2731` | Bottom Border `#DDD5C8` |
| Table even rows (zebra) | `tr:nth-child(even) td` | Cream `#F6F1E8` | Ink `#1A2731` | Bottom Border `#DDD5C8` |
| Tabular numerics | `td.num`, `.num` | inherit | Ink `#1A2731` | — |
| Bad / alert cell value | inline in table | inherit | High `#A23A2C` | — (severity text only) |

### Callouts & action boxes

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Key-finding callout | `.key-finding-callout`, `.callout` | Cream `#F6F1E8` | Ink `#1A2731` | Left Bronze `#9C7B4D` 4px |
| Recommendation box | `.recommendation-box` | Teal `#184C4C` | White `#FFFFFF` | Left Bronze `#9C7B4D` 4px |
| Recommendation label | `.recommendation-box .eyebrow` | Teal | Bronze `#9C7B4D` | — |
| Caveat / data-gaps box | `.caveat-box`, `.data-gaps` | Cream `#F6F1E8` | Muted `#54514A` | Border `#DDD5C8` |
| Caveat eyebrow | `.caveat-box .eyebrow` | Cream | Bronze `#9C7B4D` | — |

### Findings & severity

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Finding card | `.finding-card`, `.finding` | White `#FFFFFF` | Ink `#1A2731` | Border `#DDD5C8`; left stripe by severity |
| Finding index (F-01) | `.finding-index` | — | Bronze `#9C7B4D` | — |
| Finding title | `.finding-title` | — | Ink `#1A2731` | — |
| Finding action line | `.finding-action` | — | Teal `#184C4C` | — |
| Left stripe — Critical | `.finding-critical` | — | — | Left Critical `#8F2018` 5px |
| Left stripe — High | `.finding-high` | — | — | Left High `#A23A2C` 5px |
| Left stripe — Medium | `.finding-medium` | — | — | Left Medium `#C79A3E` 5px |
| Badge — Critical | `.severity-critical` | Critical tint `#F5E8E6` | Critical `#8F2018` | — |
| Badge — High | `.severity-high` | High tint `#F5EBE8` | High `#A23A2C` | — |
| Badge — Medium | `.severity-medium` | Medium tint `#F5F0E4` | Medium `#C79A3E` | — |
| Badge — Positive | `.severity-positive` | Positive tint `#E8F0EA` | Positive `#3C7350` | — |
| Inline PM flag — Critical | `.flag-critical` | Critical tint `#F5E8E6` | Critical `#8F2018` | — |
| Inline PM flag — High | `.flag-high` | High tint `#F5EBE8` | High `#A23A2C` | — |

### Timeline & footer

| Element | CSS / selector | Background | Text | Border / accent |
|---------|----------------|------------|------|-----------------|
| Timeline rail | `.timeline` | — | Ink `#1A2731` | Left Border `#DDD5C8` 2px |
| Visit date | `.timeline .visit-date` | — | Teal `#184C4C` | — |
| Footer rule | `footer.doc-footer` | — | — | Top Border `#DDD5C8` |
| Footer contact | `.footer-contact` | — | Ink `#1A2731` | — |
| Placeholder (draft) | `.fill-in` | Cream `#F6F1E8` | Ink `#1A2731` | Dashed Bronze `#9C7B4D` |

### Charts (PDF page 3 — visual only)

| Bar / status | Color |
|--------------|-------|
| Neutral / baseline | Teal `#184C4C` |
| Alert / over threshold | High `#A23A2C` |
| Within range / OK | Positive `#3C7350` |
| Chart background | Cream `#F6F1E8` or Paper `#FBF9F5` |

---

## Quick reference: which palette token when?

| Need | Use |
|------|-----|
| Page background | Paper `#FBF9F5` |
| Card / tile surface | White `#FFFFFF` |
| Soft highlight band | Cream `#F6F1E8` |
| Primary brand block | Teal `#184C4C` |
| Label / eyebrow / section # | Bronze `#9C7B4D` |
| Main reading text | Ink `#1A2731` |
| Disclaimer / secondary | Muted `#54514A` |
| Dividers & hairlines | Border `#DDD5C8` |
| Finding severity only | Critical / High / Medium / Positive hex + matching tint for pills |
