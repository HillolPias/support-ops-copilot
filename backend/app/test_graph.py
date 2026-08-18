from app.graph import graph_app
from app.models import PipelineState, IncomingTicket

ticket = IncomingTicket(
    ticket_id="t-004",
    customer_email="test@example.com",
    subject="Refund question",
    body="I was charged for the annual plan 3 days ago, can I get a refund?",
)

state = PipelineState(ticket=ticket)

result = graph_app.invoke(state)
print("Triage:", result["triage"])
print("Retrieved chunk:", len(result["retrieved"]))
print("Draft:", result["draft"].text)
print("Guardrail:", result["guardrail"])
