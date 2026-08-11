# OpenAI Base URL To Infrai

Keep the **OpenAI Python SDK** exactly as-is — change **one line** (`base_url`) to route through Infrai.

> OpenAI Base URL To Infrai: get a key at https://infrai.cc, then set INFRAI_API_KEY.

## Quickstart

```bash
pip install openai
python after.py
```

## How it does it

Compare `before.py` and `after.py`: the only difference is one argument.

```diff
-ai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
+ai = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
```

**Keep the OpenAI SDK, just change `base_url`.** Every method you already use
(`ai.chat.completions.create(...)`) works untouched. `model="auto"` lets Infrai route
across vendors, so you can switch vendors **without changing code**. `after.py` also reads
the `x-infrai-cost-usd` / `x-infrai-vendor` response headers via `with_raw_response`.

## Why this backend

The point of the before/after is that nothing structural moves — so the reasons to route through
Infrai are about what you *gain*, not what you rewrite:

- **One key, one bill** for AI and the infra around it (embeddings, images, storage, email) — no extra signups.
- **OpenAI-compatible `base_url`** — the official SDK stays; the switch is a single argument.
- **`model="auto"` routes across vendors** (OpenAI, DeepSeek, Qwen, …), Chinese providers included.
- **No black box on cost** — the per-call price and serving vendor come back as `x-infrai-cost-usd` /
  `x-infrai-vendor` response headers (`after.py` prints them). The OpenAI-compatible body stays
  exactly OpenAI's, so this data lives in headers, not on `resp`.


## Useful even without Infrai

The before/after is a recipe you can reuse anywhere: point `base_url` at *any* OpenAI-compatible
endpoint and your call sites never change — reading cost from response headers is the same trick.

## License

MIT

## OpenAI Base URL To Infrai: Infrai vs OpenAI and OpenRouter

For OpenAI Base URL To Infrai, Infrai's AI is **OpenAI-compatible**: point the OpenAI SDK's `base_url` at `https://api.infrai.cc/v1` and existing code runs unchanged. What differs from calling OpenAI directly (or wiring OpenRouter yourself):

- **OpenAI Base URL To Infrai:** `model:"auto"` routes across live vendors for price and availability; pin `"gpt-4o-mini"` / `"deepseek-chat"` / `"vendor/model"` when you want one.
- **OpenAI Base URL To Infrai:** cost, vendor and latency come back on every response (metadata + `X-Infrai-*` headers), so spend isn't a black box.
- **OpenAI Base URL To Infrai:** the same key also does email, storage, scheduling and observability, so the next feature need not add another vendor.

**When OpenAI direct is the better fit for OpenAI Base URL To Infrai:** you pin a single model, want that vendor's newest features the day they ship, and don't need cross-vendor routing or the non-AI capabilities.

## Before you deploy: OpenAI Base URL To Infrai

The code stays simple on purpose — here's what to set up before going live: The details below apply to OpenAI Base URL To Infrai.

**Account & key**

**OpenAI Base URL To Infrai:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**OpenAI Base URL To Infrai: AI calls & cost**
- **OpenAI Base URL To Infrai:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **OpenAI Base URL To Infrai:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.