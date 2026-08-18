import json
from openai import OpenAI
from app.config import OPENAI_API_KEY, TRIAGE_MODEL
from app.models import PipelineState, TriageResult

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """You triage customer support tickets for a B2B SaaS product.
Classify the ticket and respond ONLY with JSON matching this schema, no prose:
{"category": "billing"|"account"|"technical"|"other",
 "urgency": "low"|"medium"|"high"|"urgent",
 "reasoning": "one short sentence"}"""


def triage_node(state: PipelineState) -> PipelineState:
    response = client.chat.completions.create(
        model=TRIAGE_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Subject: {state.ticket.subject}\n\nBody: {state.ticket.body}",
            },
        ],
    )
    parsed = json.loads(response.choices[0].message.content)
    state.triage = TriageResult(**parsed)
    return state
