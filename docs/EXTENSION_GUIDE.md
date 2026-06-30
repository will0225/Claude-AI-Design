# Extension Guide — Modify and Grow Your Claude Integration

Once the demo script runs, use this guide to adapt the setup for your own workflows.

---

## How the demo is structured

```
python/claude_demo.py   (or node/claude_demo.js)
├── getClient()         → reads ANTHROPIC_API_KEY, creates SDK client
├── ask()               → single function wrapping messages.create()
├── smoke_test()        → minimal verification call
└── prompt_*()          → three example use cases
```

Every API call follows the same pattern:

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="Instructions that define behavior",
    messages=[{"role": "user", "content": "Your input here"}],
)
text = response.content[0].text
```

The **system** prompt sets persistent rules; **messages** carry the conversation.

---

## Add a new prompt (5-minute change)

1. Open `claude_demo.py` (or `claude_demo.js`).
2. Copy an existing `prompt_*` function.
3. Change the `system` and `user` strings.
4. Register it in the `EXAMPLES` dict.
5. Run: `python claude_demo.py --example your-key`

### Template

```python
def prompt_my_workflow(client) -> None:
    print("=" * 60)
    print("MY WORKFLOW — short description")
    print("=" * 60)
    reply = ask(
        client,
        system=(
            "Role + output format + constraints. "
            "Be specific about length, tone, and structure."
        ),
        user="Paste or build your input here.",
        max_tokens=2048,  # increase for longer outputs
    )
    print(f"\nClaude:\n{reply}\n")
```

---

## Change the model

Set an environment variable (no code change):

```bash
# In .env
CLAUDE_MODEL=claude-opus-4-6
```

Or pass it inline:

```bash
CLAUDE_MODEL=claude-haiku-4-5 python claude_demo.py
```

| Model | Trade-off |
|-------|-----------|
| `claude-haiku-4-5` | Fastest, cheapest — good for classification and simple tasks |
| `claude-sonnet-4-6` | Best balance — default for most workflows |
| `claude-opus-4-6` | Highest quality — complex reasoning, long documents |

See current models: [docs.anthropic.com/models](https://docs.anthropic.com/en/docs/about-claude/models)

---

## Multi-turn conversations

Pass prior turns in `messages`:

```python
messages = [
    {"role": "user", "content": "Summarize this doc in 3 bullets."},
    {"role": "assistant", "content": "• Point one\n• Point two\n• Point three"},
    {"role": "user", "content": "Now expand bullet two into a paragraph."},
]
response = client.messages.create(
    model=DEFAULT_MODEL,
    max_tokens=1024,
    messages=messages,
)
```

Store `messages` in a list and append each exchange for chat-style apps.

---

## Streaming responses (better UX for long outputs)

**Python:**

```python
with client.messages.stream(
    model=DEFAULT_MODEL,
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a 500-word summary."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**Node.js:**

```javascript
const stream = await client.messages.stream({
  model: DEFAULT_MODEL,
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a 500-word summary." }],
});
for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```

---

## Structured JSON output

When you need machine-parseable results, describe the schema in the system prompt:

```python
system = """Return ONLY valid JSON matching this schema:
{
  "summary": "string",
  "action_items": [{"owner": "string", "task": "string", "due": "YYYY-MM-DD"}],
  "risk_level": "low|medium|high"
}"""
```

For production apps, use the SDK's **structured outputs** or Pydantic parsing (Python) to validate responses automatically. See [Structured outputs docs](https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs).

---

## Integrate into your own project

### Minimal Python module

```python
# my_app/claude_client.py
import os
from anthropic import Anthropic

_client = None

def get_claude():
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client

def complete(system: str, user: str, max_tokens: int = 1024) -> str:
    r = get_claude().messages.create(
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return r.content[0].text
```

Import `complete()` anywhere in your app.

### Environment in production

| Environment | Recommended approach |
|-------------|---------------------|
| Local dev | `.env` file (never committed) |
| CI/CD | GitHub Actions secret `ANTHROPIC_API_KEY` |
| Cloud (AWS/GCP/Azure) | Secrets Manager / Parameter Store |
| Docker | `docker run -e ANTHROPIC_API_KEY=...` or Docker secrets |

---

## Prompt maintenance workflow

1. **Version prompts in Git** — keep system prompts in `.md` or `.txt` files, load them at runtime.
2. **Name prompts clearly** — e.g. `prompts/email_delay_notice.system.txt`.
3. **Test after model upgrades** — re-run `--all` when you change models.
4. **Log inputs/outputs carefully** — redact PII before logging; Anthropic's [data policies](https://www.anthropic.com/policies) apply.

Example: load a prompt file

```python
SYSTEM = Path("prompts/summarize.system.txt").read_text()
reply = ask(client, system=SYSTEM, user=user_input)
```

---

## Cost and rate limits

- Each call costs tokens (input + output). Check usage in the Console.
- Set `max_tokens` to the smallest value that still gives good results.
- Cache repeated system prompts where possible (see [Prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)).
- Use Haiku for high-volume, simple tasks; Sonnet/Opus for quality-critical work.

---

## Official resources

- [Anthropic API reference](https://docs.anthropic.com/en/api/messages)
- [Python SDK on GitHub](https://github.com/anthropics/anthropic-sdk-python)
- [TypeScript SDK on GitHub](https://github.com/anthropics/anthropic-sdk-typescript)
- [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)
