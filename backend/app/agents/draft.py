import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, DRAFT_MODEL
from app.models import PipelineState, DraftResponse

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You draft customer support replies for a B2B SaaS product.
Rules:
- Only state facts that appear in the provided context chunks. If the context doesn't cover the question, say you're escalating to a specialist instead of guessing.
- Never invent policy details, refund amounts, or dates.
- If the context says something must be escalated to a human, escalate it instead of attempting to resolve it yourself.
- Never claim you personally will perform an action (like "I will process 
  your refund"). State what the policy allows, and say the team will follow 
  up to complete it.
- Keep the tone warm and concise.

Respond ONLY with JSON matching this schema, no prose:
{"text": "...", "cited_sources": ["doc.md", ...]}"""


def draft_node(state: PipelineState) -> PipelineState:
    context = (
        "\n\n".join(f"[{c.source}] {c.text}" for c in state.retrieved)
        or "No relevant context found."
    )

    user_msg = (
        f"Ticket subject: {state.ticket.subject}\n"
        f"Ticket body: {state.ticket.body}\n"
        f"Category: {state.triage.category if state.triage else 'unknown'}\n\n"
        f"Context:\n{context}"
    )

    response = client.chat.completions.create(
        model=DRAFT_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    parsed = json.loads(response.choices[0].message.content)
    state.draft = DraftResponse(**parsed)
    return state
