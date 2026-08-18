from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from app.models import PipelineState
from app.agents.triage import triage_node
from app.agents.retrieval import retrieval_node
from app.agents.draft import draft_node
from app.agents.guardrail import guardrail_node
from app.agents.approval import approval_node
from app.agents.escalate import auto_escalate_node
from app.agents.execute import execute_node


def route_after_guardrail(state: PipelineState) -> str:
    return "approval" if state.guardrail and state.guardrail.passed else "auto_escalate"


def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("triage", triage_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("draft", draft_node)
    graph.add_node("guardrail", guardrail_node)
    graph.add_node("approval", approval_node)
    graph.add_node("auto_escalate", auto_escalate_node)
    graph.add_node("execute", execute_node)

    graph.set_entry_point("triage")
    graph.add_edge("triage", "retrieval")
    graph.add_edge("retrieval", "draft")
    graph.add_edge("draft", "guardrail")
    graph.add_conditional_edges(
        "guardrail",
        route_after_guardrail,
        {"approval": "approval", "auto_escalate": "auto_escalate"},
    )
    graph.add_edge("approval", "execute")
    graph.add_edge("execute", END)
    graph.add_edge("auto_escalate", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


graph_app = build_graph()
