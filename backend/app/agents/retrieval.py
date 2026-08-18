from app.models import PipelineState
from app.rag.retriever import retrieve


def retrieval_node(state: PipelineState) -> PipelineState:
    query = f"{state.ticket.subject}\n{state.ticket.body}"
    state.retrieved = retrieve(query, k=4)
    return state
