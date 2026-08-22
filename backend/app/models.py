from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TicketUrgency(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketCategory(str, Enum):
    billing = "billing"
    account = "account"
    technical = "technical"
    other = "other"


class IncomingTicket(BaseModel):
    ticket_id: str
    customer_email: str
    subject: str
    body: str


class TriageResult(BaseModel):
    category: TicketCategory
    urgency: TicketUrgency
    reasoning: str


class RetrievedChunk(BaseModel):
    source: str
    text: str
    score: float


class DraftResponse(BaseModel):
    text: str
    cited_sources: list[str] = Field(default_factory=list)


class GuardrailVerdict(BaseModel):
    passed: bool
    faithfulness_score: float
    safety_flags: list[str] = Field(default_factory=list)
    notes: str = ""


class ApprovalDecision(str, Enum):
    approved = "approved"
    edited = "edited"
    escalated = "escalated"
    rejected = "rejected"


class PipelineState(BaseModel):
    ticket: IncomingTicket
    triage: Optional[TriageResult] = None
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    draft: Optional[DraftResponse] = None
    guardrail: Optional[GuardrailVerdict] = None
    approval: Optional[ApprovalDecision] = None
    final_text: Optional[str] = None
    token_usage: dict[str, int] = Field(default_factory=dict)
    latency_ms: dict[str, float] = Field(default_factory=dict)
