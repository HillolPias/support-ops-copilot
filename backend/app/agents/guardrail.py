import json
import re
from openai import OpenAI
from app.config import OPENAI_API_KEY, GUARDRAIL_MODEL, FAITHFULNESS_THRESHOLD
from app.models import GuardrailVerdict, PipelineState

client = OpenAI(api_key=OPENAI_API_KEY)

JUDGE_SYSTEM_PROMPT = """You are a strict fact-checker. Given a context and a
drafted reply, score how well the reply is grounded in the context.
Respond ONLY with JSON: {"faithfulness_score": 0.0-1.0, "notes": "one sentence"}
A score of 1.0 means every factual claim in the reply is supported by the
context. A score near 0 means the reply invents facts not in the context."""

FORBIDDEN_PATTERNS = [
    (re.compile(r"\bpassword\b", re.I), "mentions password"),
    (re.compile(r"\bcredit card number\b|\bcvv\b", re.I), "mentions raw payment data"),
    (
        re.compile(r"ignore (all|previous) instructions", re.I),
        "possible prompt injection",
    ),
]


def _rule_based_flags(text: str) -> list[str]:
    return [label for pattern, label in FORBIDDEN_PATTERNS if pattern.search(text)]


def guardrail_node(state: PipelineState) -> PipelineState:
    draft_text = state.draft.text if state.draft else ""
    flags = _rule_based_flags(draft_text) + _rule_based_flags(state.ticket.body)

    context = "\n\n".join(c.text for c in state.retrieved) or "No context."

    response = client.chat.completions.create(
        model=GUARDRAIL_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context: \n{context}\n\nDrafted reply:\n{draft_text}",
            },
        ],
    )
    parsed = json.loads(response.choices[0].message.content)
    faithfulness = float(parsed["faithfulness_score"])

    state.guardrail = GuardrailVerdict(
        passed=faithfulness >= FAITHFULNESS_THRESHOLD and not flags,
        faithfulness_score=faithfulness,
        safety_flags=flags,
        notes=parsed.get("notes", ""),
    )
    return state
