from typing import Any

# Tool schemas in the shape the Anthropic/OpenAI function-calling APIs and
# MCP both expect. For this portfolio version, the implementation below is
# stubbed to just log the action — swap the body of send_reply_email for a
# real MCP client call once you're ready to connect a real email/Slack
# MCP server.


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "send_reply_email",
        "descripttion": "Send the approved reply to the customer's email address.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    }
]

_ACTION_LOG: list[dict[str, Any]] = []


def send_reply_email(to: str, subject: str, body: str) -> dict[str, Any]:
    action = {"tool": "send_reply_email", "to": to, "subject": subject, "body": body}
    _ACTION_LOG.append(action)
    print(f"[MCP:send_reply_email] -> {to}: {subject}")
    return {"status": "sent (stubbed)"}


def get_action_log() -> list[dict[str, Any]]:
    return list(_ACTION_LOG)
