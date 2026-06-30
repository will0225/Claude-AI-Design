# Three Example Prompts (and Why They Work)

These prompts are built into `claude_demo.py` / `claude_demo.js`. Run them with:

```bash
python claude_demo.py --all
# or
npm run demo:all
```

Each example follows a repeatable pattern you can copy for your own use cases.

---

## Example 1 — Meeting notes → structured action items

### Use case

Turn messy meeting notes into a consistent brief your team can act on without re-reading the raw transcript.

### System prompt

```
You extract action items from meeting notes.
Output exactly three sections: Summary (2 sentences),
Action Items (bulleted, owner + deadline), Open Questions.
```

### User prompt (sample input)

```
Meeting notes:
Team sync 2026-06-30: Sarah said the landing page copy is overdue.
Mike will deploy the staging build by Friday. We need legal review on
the privacy policy before launch. Budget approved for one contractor
through Q3. Next sync Tuesday 10am.
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Fixed output schema** | "Exactly three sections" prevents rambling or inconsistent formats run-to-run. |
| **Role assignment** | "Extract action items" focuses Claude on decisions, not narrative retelling. |
| **Explicit fields** | "owner + deadline" on each bullet forces accountability metadata. |
| **Separation of concerns** | System = rules; user = raw data. You can swap meeting notes without rewriting rules. |

### When to adapt

- Add a **Priority** column for engineering standups.
- Change "Open Questions" to "Decisions Made" for board meetings.
- Increase `max_tokens` if notes are longer than ~2 pages.

---

## Example 2 — Tone-controlled email draft

### Use case

Draft client or internal emails quickly while keeping a consistent voice and length.

### System prompt

```
You write concise business email drafts.
Use a warm but professional tone.
Never use exclamation marks. Keep under 120 words.
```

### User prompt

```
Draft an email to a client named Alex explaining that their
project delivery will slip by one week due to an unexpected
third-party API change. Offer a brief call to walk through options.
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Tone constraints** | "Warm but professional" narrows the style space better than "write an email." |
| **Hard limits** | "Under 120 words" and "no exclamation marks" reduce editing time. |
| **Concrete scenario** | Naming the client, reason, and ask gives Claude enough context for a usable first draft. |
| **Negative constraints** | "Never use exclamation marks" is clearer than "be professional." |

### When to adapt

- Add your company sign-off block to the system prompt.
- Include bullet points of facts Claude must mention (dates, ticket numbers).
- For sensitive emails, add: "Do not admit fault; frame as external dependency."

---

## Example 3 — Focused code review

### Use case

Get a quick security and quality pass on a code snippet before opening a PR.

### System prompt

```
You are a senior engineer doing code review.
List issues as: [CRITICAL], [WARNING], or [SUGGESTION].
For each issue, give a one-line fix. Max 5 items.
```

### User prompt

````
Review this Python function:
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
```
````

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Severity labels** | `[CRITICAL]` vs `[SUGGESTION]` helps you triage without reading everything equally. |
| **Cap on items** | "Max 5" keeps output scannable; Claude prioritizes the worst issues first. |
| **One-line fix** | Forces actionable output, not just problem description. |
| **Code fences** | Markdown fences preserve formatting so Claude parses syntax correctly. |

### When to adapt

- Add stack-specific rules: "Follow PEP 8" or "Use TypeScript strict mode conventions."
- Pass file path and surrounding context for larger reviews.
- Lower `max_tokens` to 512 — reviews should stay short.

---

## Prompt design cheat sheet

Use this when writing your own prompts:

1. **Role** — Who is Claude in this task? ("You are a …")
2. **Task** — One clear verb phrase. ("Extract …", "Draft …", "Review …")
3. **Format** — Exact sections, bullets, JSON schema, or word count.
4. **Constraints** — Tone, things to avoid, max length, priority rules.
5. **Input** — Put variable data in the user message, not the system prompt.

### Anti-patterns to avoid

- Vague asks: "Make this better" → instead specify *what* better means.
- Mixing rules and data in one blob → split system vs. user.
- No output format → you'll get a different shape every time.
- Overly long system prompts with unused instructions → keep only what affects output.

---

## Run individual examples

```bash
# Python
python claude_demo.py --example summarize
python claude_demo.py --example email
python claude_demo.py --example code-review

# Node
node claude_demo.js --example summarize
node claude_demo.js --example email
node claude_demo.js --example code-review
```

Edit the `system` and `user` strings in the script to match your real inputs, then iterate until the output is consistently usable with minimal edits.
