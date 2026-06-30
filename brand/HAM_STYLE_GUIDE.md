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

## Components

- Section header: gold serif number + "SECTION" label + title between hairlines
- Part divider: full-width teal block, gold left accent
- Data table: teal header, zebra rows (white/cream), mono for numerics
- Key-finding callout: cream bg, gold left border
- Recommendation box: teal bg, gold left border, white text
- Stat tile: white bg, large teal serif number
- Finding card: colored left stripe by severity + severity badge pill
