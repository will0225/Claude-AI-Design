# Three Example Prompts (and Why They Work)

These prompts are tailored for **consultants and professional-services teams** — discovery calls, client updates, and research synthesis. They are built into `claude_demo.py` / `claude_demo.js`.

Run them with:

```bash
python claude_demo.py --all
# or
npm run demo:all
```

Each example follows a repeatable pattern you can copy for your own use cases.

---

## Example 1 — Discovery call → proposal outline

### Use case

After a sales or discovery call, turn rough notes into a client-ready scope outline you can send within hours — without rewriting from scratch.

### System prompt

```
You are a consultant turning discovery call notes into a proposal outline.
Output exactly four sections: Client Snapshot (3 bullets), Stated Needs,
Proposed Scope (bulleted deliverables tagged S/M/L for effort),
Next Steps (owner + date). Use client-ready language; avoid internal jargon.
```

### User prompt (sample input)

```
Discovery call notes:
Discovery call 2026-06-30 with Jordan (COO), Brightline Marketing, ~12 staff.
Pain: client reporting takes 6+ hrs/week; proposal drafts inconsistent across team.
Tried ChatGPT Team — outputs vary too much, hard to reuse prompts.
Wants Claude wired into daily workflow; open to Python script or Zapier if simpler.
Budget: $5–8k for setup + training. Timeline: live in 3 weeks before Q3 campaigns.
Must loop in IT on API/data policy. Competitor quote pending from another vendor.
Jordan asked for a scope doc by Friday; decision by next Tuesday.
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Fixed four-section schema** | Mirrors how clients expect proposals: who they are, what they need, what you'll deliver, what's next. |
| **Effort tags (S/M/L)** | Forces realistic scoping instead of an open-ended task list. |
| **Client-ready language rule** | Strips internal shorthand ("loop in IT") into polished copy you can edit lightly and send. |
| **Separation of concerns** | System = format and tone; user = raw call notes you paste after every discovery call. |

### When to adapt

- Add a **Pricing Options** section (good/better/best tiers).
- Include **Out of Scope** bullets to prevent scope creep.
- Increase `max_tokens` to 2048 for longer enterprise discovery calls.

---

## Example 2 — Weekly client status update

### Use case

Send a consistent Friday status email across all active engagements — progress, blockers, next week, and one clear ask.

### System prompt

```
You write weekly project status emails for consulting clients.
Structure exactly: Subject line, Progress This Week (3 bullets),
Blockers (one bullet or 'None'), Plan for Next Week (3 bullets),
Ask of Client (one sentence or 'None').
Tone: confident and transparent. Body under 150 words. No exclamation marks.
```

### User prompt

```
Client: Northwind Digital. Project: Claude workflow setup.
This week: completed API setup and demo script; drafted three tailored prompts;
shared setup guide for their team.
Blocker: waiting on their legal team to approve API usage policy.
Next week: handoff screen share; customize prompts for client reporting workflow;
document Zapier option for non-technical staff.
Ask: confirm handoff call slot (Tue or Wed afternoon).
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Repeatable weekly structure** | Same sections every week — clients know where to look; you fill in bullet facts only. |
| **Explicit blocker field** | Surfaces risks early instead of burying them in prose. |
| **Single "Ask of Client"** | One CTA per email improves response rates vs. multiple requests. |
| **Hard word limit** | Keeps updates scannable for busy executives. |

### When to adapt

- Add **Budget/Timeline Status** (green/yellow/red) for fixed-fee projects.
- Paste your email sign-off into the system prompt for consistent branding.
- For internal standups, swap "Ask of Client" for "Decisions Needed."

---

## Example 3 — Research notes → executive brief

### Use case

Synthesize messy competitive research, tool comparisons, or market notes into a brief you can attach to a proposal or share with a client stakeholder.

### System prompt

```
You synthesize raw research notes into an executive brief for a client RFP.
Output: Headline (one sentence), Key Findings (5 bullets),
Implications for This Client (3 bullets), Recommended Actions (numbered, max 3).
Preserve [UNVERIFIED] tags on any unconfirmed claims.
```

### User prompt

```
Research notes:
Research re: AI tooling for Brightline's workflow automation RFP response.
- Claude API: strong long-document handling; official Python + Node SDKs.
- OpenAI GPT-4o: larger plugin ecosystem; team already has some ChatGPT seats.
- Anthropic API data: not used for training by default — important for client data.
- Zapier / Make: both have Anthropic connectors; good for marketing ops, ~$20+/mo.
- Pricing: Haiku cheapest/high volume; Sonnet best balance; Opus for heavy reasoning.
- Claude.ai Projects: may suffice for non-technical staff without API spend.
- [UNVERIFIED] Gemini Enterprise may integrate better with Google Workspace.
- Client priority: repeatable prompts, clear handoff docs, minimal engineering lift.
```

### Why it works

| Technique | What it does |
|-----------|--------------|
| **Headline first** | Forces a one-sentence thesis before detail — execs get the point immediately. |
| **Findings vs. implications split** | Separates facts from "so what for this client," which is what they're paying for. |
| **Capped recommendations (max 3)** | Prevents analysis paralysis; you sound decisive, not encyclopedic. |
| **[UNVERIFIED] preservation** | Keeps honest uncertainty visible — critical when research feeds client decisions. |

### When to adapt

- Add a **Sources** section if you need auditability.
- Change "Implications for This Client" to match the prospect name from Example 1.
- Use for vendor comparisons, policy research, or industry trend scans.

---

## Prompt design cheat sheet

Use this when writing your own prompts:

1. **Role** — Who is Claude in this task? ("You are a consultant …")
2. **Task** — One clear verb phrase. ("Turn … into …", "Write …", "Synthesize …")
3. **Format** — Exact sections, bullets, tags, or word count.
4. **Constraints** — Tone, audience, things to avoid.
5. **Input** — Put variable data (notes, facts, names) in the user message.

### Anti-patterns to avoid

- Vague asks: "Make this better" → specify the output shape instead.
- Mixing rules and data in one blob → split system vs. user.
- No output format → you'll get a different shape every time.
- Overly long system prompts with unused instructions → keep only what affects output.

---

## Run individual examples

```bash
# Python
python claude_demo.py --example discovery
python claude_demo.py --example status-email
python claude_demo.py --example research-brief

# Node
node claude_demo.js --example discovery
node claude_demo.js --example status-email
node claude_demo.js --example research-brief
```

Edit the `system` and `user` strings in the script to match your real inputs, then iterate until the output is consistently usable with minimal edits.

---

## Industry variants (quick swaps)

If your client is not in consulting, keep the same **system/user split** and swap the content:

| Industry | Example 1 (structured extract) | Example 2 (draft comms) | Example 3 (synthesis) |
|----------|-------------------------------|---------------------------|------------------------|
| **Marketing agency** | Campaign kickoff notes → creative brief | Client campaign performance recap | Competitor ad audit notes → strategy memo |
| **Legal / compliance** | Intake call notes → matter summary | Client update on review status | Regulatory change notes → impact brief |
| **Real estate** | Buyer consultation → property brief | Weekly listing pipeline update | Neighborhood market stats → seller advisory |
| **Product / engineering** | User interview notes → feature spec outline | Sprint stakeholder update | Tech evaluation notes → build vs. buy memo |

Copy the closest row, paste your client's real notes into the user message, and tune the system prompt sections to match their deliverable names.
