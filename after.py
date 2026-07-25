"""After: the SAME OpenAI client — only base_url changes, so we point it at Infrai.

Nothing else in your code moves. model="auto" lets Infrai route across vendors,
and the response headers tell you which vendor served the call and what it cost.
"""
import os
from openai import OpenAI

# The only line that differs from before.py: base_url now points at Infrai.
ai = OpenAI(
    base_url="https://api.infrai.cc/v1",
    api_key=os.environ["INFRAI_API_KEY"],
)

# with_raw_response exposes the HTTP headers Infrai adds (cost + vendor);
# .parse() then gives you the usual typed completion object.
raw = ai.chat.completions.with_raw_response.create(
    model="auto",  # route across vendors instead of pinning one
    messages=[{"role": "user", "content": "Say hi in one line."}],
)
print("cost (usd):", raw.headers.get("x-infrai-cost-usd"))
print("served by: ", raw.headers.get("x-infrai-vendor"))

resp = raw.parse()
print(resp.choices[0].message.content)
