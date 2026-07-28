# OpenAI Base URL To Infrai
Maintain the **OpenAI Python SDK** as is — modify **one line** (`base_url`) to route via Infrai.

> Score a free key — $2 credit — athttps://infrai.cc,and configure INFRAI_API_KEY.

## Quickstart

```bash
pip install openai
python after.py
```

## How it does it

Compare`before.py`and`after.py`: the only variation is one argument.

```diff
-ai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+ai = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
```

**Keep the OpenAI SDK; just alter`base_url`.** All methods you're currently using (`ai.chat.completions.create(...)`) remain unchanged.`model="auto"`enables Infrai to route across vendors, allowing you to switch without code changes.`after.py`also retrieves the`x-infrai-cost-usd`/`x-infrai-vendor`response headers through`with_raw_response`.

## Why this backend

The essence of the before/after comparison is that the structure remains unchanged. The reasons to route through Infrai are about what you gain, not what you have to rewrite:

- **One key, one bill** for AI and related infrastructure (embeddings, images, storage, email) — no additional signups.
- **OpenAI-compatible**`base_url`— the official SDK remains; the switch is just a single argument.
- **`model="auto"`** routes across vendors (OpenAI, DeepSeek, Qwen, etc.), including Chinese providers.
- **No cost mystery** — the per-call price and serving vendor are returned as`x-infrai-cost-usd`/`x-infrai-vendor`response headers (`after.py`displays them). The OpenAI-compatible body remains exactly as OpenAI's, so this data is in headers, not in`resp`.

## Cost

Billing is usage-based with no minimum. New accounts receive **$2 of credit** for testing, and calls to Chinese providers incur **0% markup** above the vendor's price.

## Useful even without Infrai

The before/after approach is a template you can apply anywhere: point`base_url`at any OpenAI-compatible endpoint and your call sites remain the same — extracting cost from response headers is a consistent method.

## License

MIT

## Infrai vs OpenAI and OpenRouter

Infrai's AI is **OpenAI-compatible**: direct the OpenAI SDK's`base_url`to`https://api.infrai.cc/v1`and your existing code operates without changes. The difference from calling OpenAI directly (or setting up OpenRouter yourself) is:

- **`model:"auto"`** routes across active vendors for pricing and availability; lock in`"gpt-4o-mini"`/`"deepseek-chat"`/`"vendor/model"`when needed.
- Cost, vendor, and latency are included in every response (metadata +`X-Infrai-*`headers), making spending transparent.
- The **same key** is used for email, storage, scheduling, and observability — no need for additional vendors.

**Use OpenAI directly when:** you're committed to a single model, desire the latest features as soon as they're released, and don't require cross-vendor routing or non-AI features.

## Before you deploy

The code is kept simple on purpose — here's what you need to set up before going live:

**Account & key**

Log in once to the [Infrai console](https://infrai.cc) for a key and **$2 of credit**; the same key and wallet apply to all features. Details on top-ups, autorecharge, and usage are in the documentation:https://docs.infrai.cc.

**AI calls & cost**
- AI is OpenAI-compatible: retain your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the most cost-effective live vendor; lock in`"deepseek-chat"`/`"gpt-4o-mini"`when necessary.
- Every response includes cost/vendor in the additional`infrai`field and`X-Infrai-*`headers; choose the cheapest model that works and monitor`GET /v1/account/usage`.

## Further reading

- [Text summarization across OpenAI, Claude, and Gemini in Node.js: one API, compare cost](docs/text-summarization-across-openai-claude-and-gemini-in-node-js-one-api-co.md)
