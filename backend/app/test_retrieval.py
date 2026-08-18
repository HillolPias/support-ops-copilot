from app.agents.retrieval import retrieval_node
from app.models import IncomingTicket, PipelineState

ticket = IncomingTicket(
    ticket_id="t-003",
    customer_email="test@example.com",
    subject="Refund question",
    body="I was charged for the annual plan 3 days ago, can I get a refund?",
)
state = PipelineState(ticket=ticket)
result = retrieval_node(state)
for chunk in result.retrieved:
    print(f"[{chunk.score}] {chunk.source}: {chunk.text[:80]}...")
