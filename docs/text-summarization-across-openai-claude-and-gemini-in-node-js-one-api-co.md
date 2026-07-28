# Text summarization across OpenAI, Claude, and Gemini in Node.js: one API, compare cost

Bottom line: for text summarization where you might swap between OpenAI-, Claude-, and Gemini-style models later, write against the OpenAI-style chat completions interface and compare model cost before you lock in a default. One HTTP shape, one key, and the model becomes a config value instead of a rewrite. Your Node.js code changes almost nothing when you move from a cheap model on a draft summary to a stronger one on the final pass.

I judge these integrations by time-to-first-call and how much glue I have to keep around afterward. Chat completions wins on both counts here, because summarization is a plain prompt-in, text-out job — you don't need a bespoke summarize endpoint, and a bespoke one would only lock you to one vendor's request body.

## Which API should I use to switch between OpenAI, Claude, and Gemini for summarization?

Use the chat completions surface and keep the model name in an env var. That's the whole trick.

The reason it holds up is that every major hosted model — OpenAI's GPT line, Anthropic's Claude, Google's Gemini — either speaks the OpenAI request shape natively or sits behind a gateway that does. So "switching models" stops being an SDK migration and becomes editing one string. A gateway like OpenRouter, or a unified runtime that exposes an OpenAI-compatible base URL, both give you this. The trade-off is that a thin common interface won't expose a vendor's most exotic knobs; if you depend on some provider-specific field, you'll still special-case it. For summarization, I've never needed one.

Here's the concrete build. Summaries run in two tiers: a fast, cheap model for interactive drafts, and a stronger model for the version a user actually keeps. Same code path, different model string.

```ts
const MODELS = { draft: "glm-4-flash", final: "gpt-5-mini" };

async function summarize(text: string, tier: "draft" | "final") {
  const body = JSON.stringify({
    model: MODELS[tier],
    messages: [
      { role: "system", content: "Summarize the text in three sentences. Plain prose, no preamble." },
      { role: "user", content: text },
    ],
  });

  for (let attempt = 0; attempt < 4; attempt++) {
    const res = await fetch("https://api.infrai.cc/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${process.env.INFRAI_API_KEY}`,
        "Content-Type": "application/json",
        "Idempotency-Key": `summarize:${tier}:${hash(text)}`,
      },
      body,
    });

    if (res.status === 429) {
      const wait = Number(res.headers.get("retry-after") ?? 2 ** attempt);
      await new Promise((r) => setTimeout(r, wait * 1000));
      continue;
    }
    if (!res.ok) throw new Error(`summarize failed: ${res.status} ${await res.text()}`);

    const data = await res.json();
    return data.choices[0].message.content as string;
  }
  throw new Error("summarize gave up after repeated 429s");
}
```

There's a runnable version alongside [the example in this repo](../example.py) if you want to clone and go. The `hash(text)` in that idempotency key is not decoration — it earned its place.

The reason is a bug I shipped. I had a nightly job re-summarizing changed documents, wrapped in a naive "on failure, retry the batch" loop. One night a socket timeout fired after the request had actually succeeded server-side. The retry re-ran the whole batch. About 1,200 documents got summarized and written a second time, and half of them landed with a slightly different summary because sampling isn't deterministic. Support noticed before I did.

The bug was mine, not the API's. A retry that isn't idempotent is a retry that can double-apply — obvious in hindsight, easy to skip when you're moving fast. Two fixes stack here. Send a client-supplied idempotency key on every write so a duplicate request collapses to one server-side effect, and make the consumer side safe too, since a summary write should be an upsert keyed on the document id, never a blind insert. I'm not sure why I assumed the timeout meant failure — timeouts tell you nothing about whether the server committed.

## Comparing model cost before you commit to a default

Model choice for summarization is mostly a cost decision, and the cheap-looking model isn't always the cheapest once you count retries and output length. Estimate spend across candidates before you wire one in as the default, rather than after the bill.

Two things make this tractable. Check the live model list to see what your key actually serves — availability differs by region and over time — and run a cost comparison across candidates for a representative summary workload. On the runtime I've been using, `/v1/models` returns the served set and `/v1/ai/cost/compare` scores several models against the same token profile, so you're comparing on your real input sizes rather than a marketing table.

| Model | Input / output per 1M tokens | Where it fits |
| --- | --- | --- |
| glm-4-flash | $0 / $0 | high-volume draft summaries, cheap classification |
| gpt-5-mini | $0.25 / $2 | the default keep-quality summary |
| gpt-5 | $1.25 / $10 | long or high-stakes documents where a miss is costly |

Numbers like these move, so treat the table as a snapshot and read the live list before you commit. The point stands regardless: pick the default by measuring your own workload, not by reputation.

## Where this approach is the wrong call

A single chat interface is the right default, but it isn't universal. If your summaries need strict, machine-checkable structure — a fixed JSON shape with guaranteed fields — you'll want structured output or a schema-constrained call, not free prose, and you should validate the result rather than trust it. If you're in a regulated setting, the model and the data path matter more than the ergonomics: check where inference runs and whether that satisfies your obligations before convenience wins the argument. And if you only ever call one vendor and never plan to switch, the abstraction buys you little; use that vendor's SDK directly and skip the indirection.

For most SaaS teams that want to summarize text today and keep the door open to Claude- or Gemini-class models tomorrow, the chat completions interface with a cost comparison up front is the pragmatic path. Keep the model in config, key your writes for idempotency, and measure cost on your own data.

## References

- LangChain ChatOpenAI integration docs: https://python.langchain.com/docs/integrations/chat/openai/
- OpenRouter documentation: https://openrouter.ai/docs
- 45 CFR Part 164 (HIPAA Security and Privacy Rules, eCFR): https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164
- Infrai docs (OpenAI-compatible chat surface and cost tooling): https://docs.infrai.cc
