from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command

from app.graph import graph_app
from app.models import IncomingTicket, PipelineState

app = FastAPI(title="Support Ops Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"ok": True}


@app.post("/tickets")
def submit_ticket(ticket: IncomingTicket):
    config = {"configurable": {"thread_id": ticket.ticket_id}}

    existing = graph_app.get_state(config)
    if existing.values:
        raise HTTPException(
            status_code=409,
            detail=f"Ticket '{ticket.ticket_id}' already submitted.",
        )

    result = graph_app.invoke(PipelineState(ticket=ticket), config=config)

    interurpts = result.get("__interrupt__")
    if interurpts:
        return {
            "status": "pending_approval",
            "ticket_id": ticket.ticket_id,
            "review": interurpts[0].value,
        }
    return {"status": result.get("approval"), "ticket_id": ticket.ticket_id}


@app.post("/tickets/{ticket_id}/decision")
def submit_decision(ticket_id: str, decision: str, edited_text: str | None = None):
    config = {"configurable": {"thread_id": ticket_id}}
    try:
        result = graph_app.invoke(
            Command(resume={"decision": decision, "edited_text": edited_text}),
            config=config,
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "status": "done",
        "ticket_id": ticket_id,
        "approval": result.get("approval"),
        "metrics": {
            "token_usage": result.get("token_usage", {}),
            "latency_ms": result.get("latency_ms", {}),
            "total_tokens": sum(result.get("token_usage", {}).values()),
            "total_latency_ms": round(sum(result.get("latency_ms", {}).values()), 1),
        },
    }
