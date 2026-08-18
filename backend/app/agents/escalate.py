from app.models import PipelineState, ApprovalDecision


def auto_escalate_node(state: PipelineState) -> PipelineState:
    state.approval = ApprovalDecision.escalated
    state.final_text = None
    return state
