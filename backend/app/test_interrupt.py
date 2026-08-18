from langgraph.types import Command
from app.graph import graph_app
from app.models import IncomingTicket, PipelineState

ticket = IncomingTicket(
    ticket_id="t-007",
    customer_email="test@example.com",
    subject="Refund question",
    body="I was charged for the annual plan 3 days ago, can I get a refund?",
)
config = {"configurable": {"thread_id": ticket.ticket_id}}

# First call: runs until it hits interrupt() and stops there.
result = graph_app.invoke(PipelineState(ticket=ticket), config=config)
print("--- First call result ---")
print(result)


# A human looks at result["__interrupt__"][0].value here, in a real app.
# Now simulate them approving it. Second call, SAME thread_id, resumes.
# the exact same paused run instead of starting over.
result2 = graph_app.invoke(Command(resume={"decision": "approved"}), config=config)
print("--- After resume ---")
print(result2)
