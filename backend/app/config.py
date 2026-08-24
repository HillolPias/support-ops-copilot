import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent  # .../backend

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Cost/latency split: cheap model for classification-style tasks,
# stronger model only where response quality actually matters to the customer.
TRIAGE_MODEL = os.getenv("TRIAGE_MODEL", "gpt-4o-mini")
DRAFT_MODEL = os.getenv("DRAFT_MODEL", "gpt-4o")
GUARDRAIL_MODEL = os.getenv("GUARDRAIL_MODEL", "gpt-4o-mini")

FAITHFULNESS_THRESHOLD = float(os.getenv("FAITHFULNESS_THRESHOLD", 0.7))

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(BACKEND_DIR / "chroma_data"))
DOCS_DIR = os.getenv("DOCS_DIR", str(BACKEND_DIR / "data" / "docs"))
