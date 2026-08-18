from langgraph.types import interrupt
from app.models import ApprovalDecision, PipelineState


def approval_node(state: PipelineState) -> PipelineState:
    decision: dict = interrupt(
        {
            "ticket_id": state.ticket.ticket_id,
            "draft": state.draft.text if state.draft else "",
            "faithfulness_score": (
                state.guardrail.faithfulness_score if state.guardrail else None
            ),
        }
    )
    state.approval = ApprovalDecision(decision["decision"])
    state.final_text = decision.get("edited_text") or (
        state.draft.text if state.draft else None
    )
    return state
