from app.agents.triage import triage_node
from app.models import IncomingTicket, PipelineState

ticket = IncomingTicket(
    ticket_id="t-001",
    customer_email="test@example.com",
    subject="Refund question",
    body="I was charged for the annual plan 3 days ago, can I get a refund?",
)
state = PipelineState(ticket=ticket)
result = triage_node(state)
print(result.triage)
