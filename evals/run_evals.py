import json
import sys
from pathlib import Path
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.agents.triage import triage_node
from app.agents.retrieval import retrieval_node
from app.agents.draft import draft_node
from app.agents.guardrail import guardrail_node
from app.models import IncomingTicket, PipelineState

DATASET_PATH = Path(__file__).parent / "dataset.jsonl"
ESCALATION_PHRASES = [
    "escalat",
    "specialist",
    "human agent",
    "can't resolve this",
    "case-by-case",
]
# "escalat" is intentionally truncated so it matches both “escalate” and “escalation”.


@dataclass
class EvalResult:
    ticket_id: str
    category_correct: bool
    escalation_correct: bool
    keyword_missing: list[str] = field(default_factory=list)
    faithfulness_score: float = 0.0


# 'looks_escalated' function decides whether a generated draft looks like an escalation.
def looks_escalated(draft_text: str, guardrail_passed: bool) -> bool:
    if not guardrail_passed:
        return True
    lowered = draft_text.lower()
    return any(p in lowered for p in ESCALATION_PHRASES)


def run_one(record: dict) -> EvalResult:
    ticket = IncomingTicket(
        ticket_id=record["ticket_id"],
        customer_email=record["customer_email"],
        subject=record["subject"],
        body=record["body"],
    )
    state = PipelineState(ticket=ticket)
    state = triage_node(state)
    state = retrieval_node(state)
    state = draft_node(state)
    state = guardrail_node(state)

    draft_text = state.draft.text if state.draft else ""
    category_correct = state.triage.category.value == record["expected_category"]
    escalation_correct = (
        looks_escalated(draft_text, state.guardrail.passed)
        == record["expected_escalate"]
    )

    missing = [
        kw
        for kw in record.get("must_mension", [])
        if kw.lower() not in draft_text.lower()
    ]

    return EvalResult(
        ticket_id=record["ticket_id"],
        category_correct=category_correct,
        escalation_correct=escalation_correct,
        keyword_missing=missing,
        faithfulness_score=(
            state.guardrail.faithfulness_score if state.guardrail else 0.0
        ),
    )


def main():
    records = [
        json.loads(line)
        for line in DATASET_PATH.read_text().splitlines()
        if line.strip()
    ]
    print(f"DEBUG: looking for dataset at {DATASET_PATH}")
    print(f"DEBUG: file exists? {DATASET_PATH.exists()}")
    print(f"DEBUG: loaded {len(records)} records")
    results = []

    for record in records:
        result = run_one(record)
        results.append(result)
        ok = (
            result.category_correct
            and result.escalation_correct
            and not result.keyword_missing
        )
        print(
            f"[{'OK' if ok else 'FAIL'}] {result.ticket_id} | category={result.category_correct} "
            f"escalation={result.escalation_correct} missing={result.keyword_missing} "
            f"faithfulness={result.faithfulness_score}"
        )

    n = len(results)
    category_acc = sum(r.category_correct for r in results) / n
    escalation_acc = sum(r.escalation_correct for r in results) / n
    keyword_acc = sum(1 for r in results if not r.keyword_missing) / n

    print(f"\ncategory accuracy:  {category_acc:.0%}")
    print(f"escalation accuracy: {escalation_acc:.0%}")
    print(f"keyword coverage:    {keyword_acc:.0%}")

    THRESHOLD = 0.75
    worst = min(category_acc, escalation_acc, keyword_acc)
    if worst < THRESHOLD:
        print(f"\nEVAL GATE FAILED: {worst:.0%} < {THRESHOLD:.0%}")
        sys.exit(1)
    print("\nEVAL GATE PASSED")


if __name__ == "__main__":
    main()
