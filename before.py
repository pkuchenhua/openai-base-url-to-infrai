"""Before: the stock OpenAI client, talking straight to OpenAI."""
import os
from openai import OpenAI

ai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

resp = ai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hi in one line."}],
)
print(resp.choices[0].message.content)
