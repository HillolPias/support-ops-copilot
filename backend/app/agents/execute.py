from app.models import PipelineState, ApprovalDecision
from app.mcp.tools import send_reply_email


def execute_node(state: PipelineState) -> PipelineState:
    if state.approval in (ApprovalDecision.approved, ApprovalDecision.edited):
        send_reply_email(
            to=state.ticket.customer_email,
            subject=f"Re: {state.ticket.subject}",
            body=state.final_text or "",
        )

    return state
