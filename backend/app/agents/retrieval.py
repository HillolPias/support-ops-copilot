import time
from app.models import PipelineState
from app.rag.retriever import retrieve


def retrieval_node(state: PipelineState) -> PipelineState:
    start = time.perf_counter()
    query = f"{state.ticket.subject}\n{state.ticket.body}"
    state.retrieved = retrieve(query, k=4)

    state.latency_ms["retrieval"] = round((time.perf_counter() - start) * 1000, 1)
    return state
