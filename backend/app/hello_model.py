from openai import OpenAI
from app.config import OPENAI_API_KEY, TRIAGE_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(
    model=TRIAGE_MODEL,
    messages=[{"role": "user", "content": "Reply with exactly the word: pong"}],
)

print(response.choices[0].message.content)
