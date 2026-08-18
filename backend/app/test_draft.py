from app.agents.triage import triage_node
from app.agents.retrieval import retrieval_node
from app.agents.draft import draft_node
from app.models import IncomingTicket, PipelineState

ticket = IncomingTicket(
    ticket_id="t-005",
    customer_email="test@example.com",
    subject="Refund question",
    body="I was charged for the annual plan 3 days ago, can I get a refund?",
)

state = PipelineState(ticket=ticket)
state = triage_node(state)
state = retrieval_node(state)
state = draft_node(state)

print(state.draft.text)
print("Cited:", state.draft.cited_sources)
