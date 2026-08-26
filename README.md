# Support Ops Copilot

A multi-agent customer support ticket resolver built to demonstrate production-oriented AI engineering: agent orchestration, RAG grounding, independent guardrails, human-in-the-loop control, cost/latency observability, and real MCP tool integration — not just a working demo.

## Why this exists

Most AI-agent portfolio projects stop at "an agent that calls a tool and it works." This one is built around a different question: what does it take for a support-ticket agent to be something a company could actually trust in production? That means the system has to fail _safely_ and _measurably_ — verify its own output, refuse to act autonomously without a human checkpoint, and be testable in CI, not just demoable once.

## Architecture

Ticket in
-> triage (classifies category + urgency, gpt-4o-mini)
-> retrieval (RAG grounding via ChromaDB, local embeddings)
-> draft (writes a reply grounded only in retrieved context, gpt-4o)
-> guardrail (LLM-as-judge faithfulness score + rule-based safety scan)
|-- failed --> auto_escalate --> END (never sent, routed to a human queue)
|-- passed --> approval (LangGraph interrupt() genuinely pauses here)
-> execute (MCP tool call, only after human approval)
-> END

Every node reads and writes a single shared `PipelineState` object — there are no direct function-argument handoffs between agents, which is what makes adding a new node later mean "read some fields, write one field, wire two edges" rather than rewriting signatures throughout.

### Design decisions worth knowing about

- **Cost/latency-aware model routing.** Triage and guardrail checking use `gpt-4o-mini`; only the draft agent, where response quality actually matters to the customer, uses `gpt-4o`. Real per-node token usage and latency are tracked in `PipelineState` and surfaced in the API response.
- **The guardrail is a second, independent model call — not the draft agent grading its own work.** It receives only the retrieved context and the draft text, with no memory of why the draft was written, and scores how well the reply is actually grounded. Combined with a cheap rule-based scan (password mentions, prompt-injection phrase echoes) that runs before any model call.
- **Human approval is enforced structurally, not just in the UI.** `approval_node` calls LangGraph's `interrupt()`, which genuinely halts graph execution and checkpoints the paused state. Nothing downstream — including the MCP action executor — can run until a real resume call with a human decision arrives. A guardrail failure routes straight to auto-escalation and skips approval entirely, so a failing draft is never even shown as "ready to send."
- **MCP tool integration is real, not a mocked schema.** `mcp_server/server.py` is a standalone process exposing `send_reply_email` as an actual MCP tool over stdio transport. `app/mcp/tools.py` is a genuine client — subprocess spawn, protocol handshake (`session.initialize()`), tool call — not a direct Python function call. `execute_node` required zero changes when this was swapped in from an earlier stub, since the function signature never changed.
- **Evals gate CI**, not just exist as a folder. `evals/run_evals.py` scores category accuracy, correct-escalation rate, and required-keyword coverage against a small golden-ticket dataset, and exits non-zero below threshold. Wired into GitHub Actions on any PR touching agent code, the graph, or the knowledge base.

## Project structure

backend/
app/
agents/ triage, retrieval, draft, guardrail, approval, execute
rag/ ingest.py (chunk + embed + store), retriever.py (query)
mcp/ tools.py — MCP client
models.py Pydantic schemas shared across the whole pipeline
config.py env-driven config, model routing, path resolution
graph.py the LangGraph StateGraph wiring
main.py FastAPI endpoints
mcp_server/
server.py standalone MCP server (send_reply_email tool)
data/docs/ the knowledge base RAG retrieves from
evals/
dataset.jsonl golden tickets
run_evals.py scoring + CI gate
frontend/ Next.js approval dashboard
.github/workflows/ CI: eval gate on relevant PRs

## Running it locally

```bash
git clone https://github.com/HillolPias/support-ops-copilot.git
cd support-ops-copilot/backend
uv sync
cp .env.example .env   # add your OPENAI_API_KEY
uv run python -m app.rag.ingest    # build the ChromaDB index
uv run uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`, submit a ticket, review the draft and faithfulness score, approve/edit/reject.

## Running the evals

```bash
uv run --project backend python evals/run_evals.py
```

## What broke, and what that taught me

Worth being honest about rather than presenting a project that looks like it worked on the first try — it didn't, and the debugging is part of the actual engineering:

- **A relative path bug in `CHROMA_PERSIST_DIR`** resolved against the process's _current working directory_ rather than the project's actual location, causing intermittent `Collection does not exist` errors depending on which folder a command happened to be run from. Fixed by resolving the path relative to `config.py`'s own file location instead.
- **The escalation-detection heuristic in the eval harness and the draft agent's own prompt drifted out of sync** — a prompt fix ("say the team will follow up" instead of "I will process this") accidentally started tripping the eval's escalation-phrase detector on _successful_ resolutions. Caught by the eval suite, not by manual testing — exactly the kind of regression this project's eval gate exists to catch.
- **The MCP server integration broke in three distinct ways** during setup: spawning the subprocess with a bare `"python"` command resolved to the wrong interpreter on Windows (fixed with `sys.executable`); a standalone `fastmcp` package and the bundled `mcp.server.fastmcp` module conflicted; and the `mcp` SDK's `2.x` line turned out to be a very recent major version with a breaking API change (`FastMCP` renamed) not yet reflected in most documentation — resolved by pinning to `mcp<2.0.0`, the stable, well-documented line.

## Roadmap

- [ ] Surface cost/latency metrics in the frontend dashboard (currently API-only)
- [ ] Swap the local MCP server for a real Gmail/Slack MCP server
- [ ] Expand the eval dataset and add an LLM-graded rubric alongside the current heuristic scoring
- [ ] Persistent (Postgres) checkpointer instead of in-memory, so a paused approval survives a server restart
