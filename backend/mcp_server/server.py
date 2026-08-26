from pathlib import Path
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("support-ops-email-server")

LOG_PATH = Path(__file__).parent / "sent_emails.log"


@mcp.tool()
def send_reply_email(to: str, subject: str, body: str) -> str:
    """Send an approved support reply to a customer's email address."""
    entry = (
        f"--- {datetime.now(timezone.utc).isoformat()} ---\n"
        f"To: {to}\nSubject: {subject}\n\n{body}\n\n"
    )
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    return f"Email queued for delivery to {to}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
