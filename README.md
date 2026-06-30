# Claude AI Setup Kit

A clean, repeatable starter kit for integrating [Anthropic Claude](https://www.anthropic.com) into your daily workflow. Includes working demo scripts (Python and Node.js), setup documentation, and three prompt patterns tailored for **consultants and professional-services teams**.

## Quick start

1. **Create an account** and API key → [SETUP_GUIDE.md](./docs/SETUP_GUIDE.md)
2. **Pick a stack** and run the demo:

```bash
# Python
cd python && cp .env.example .env   # add your key
pip install -r requirements.txt
python claude_demo.py

# Node.js
cd node && cp .env.example .env     # add your key
npm install
npm run demo
```

3. **See example prompts** → [EXAMPLE_PROMPTS.md](./docs/EXAMPLE_PROMPTS.md)

## What's included

| Deliverable | Location |
|-------------|----------|
| Working demo (Python) | `python/claude_demo.py` |
| Working demo (Node.js) | `node/claude_demo.js` |
| Account & API key setup guide | [docs/SETUP_GUIDE.md](./docs/SETUP_GUIDE.md) |
| How to extend the integration | [docs/EXTENSION_GUIDE.md](./docs/EXTENSION_GUIDE.md) |
| Three example prompts + rationale | [docs/EXAMPLE_PROMPTS.md](./docs/EXAMPLE_PROMPTS.md) |
| Handoff / verification checklist | [docs/HANDOFF_CHECKLIST.md](./docs/HANDOFF_CHECKLIST.md) |

## Demo commands

```bash
# Smoke test only
python claude_demo.py
npm run demo

# All three example prompts
python claude_demo.py --all
npm run demo:all

# Single example
python claude_demo.py --example discovery
node claude_demo.js --example status-email
```

## Requirements

- Anthropic API key ([get one here](https://console.anthropic.com/settings/keys))
- Python 3.9+ **or** Node.js 18+
- Outbound HTTPS to `api.anthropic.com`

## Security

Never commit your `.env` file. API keys belong in environment variables or a secrets manager — not in source code.

## License

MIT — use and adapt freely for your projects.
