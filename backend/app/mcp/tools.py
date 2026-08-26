import sys
import asyncio
from os import write
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent / "mcp_server" / "server.py"
)

_ACTION_LOG: list[dict] = []


async def _call_send_reply_email(to: str, subject: str, body: str) -> str:
    server_params = StdioServerParameters(
        command=sys.executable, args=[str(SERVER_SCRIPT)]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "send_reply_email",
                arguments={"to": to, "subject": subject, "body": body},
            )
            return result.content[0].text


def send_reply_email(to: str, subject: str, body: str) -> dict:
    result_text = asyncio.run(_call_send_reply_email(to, subject, body))
    action = {
        "tool": "send_reply_email",
        "to": to,
        "subject": subject,
        "result": result_text,
    }
    _ACTION_LOG.append(action)
    print(f"[MCP:send_reply_email] -> {result_text}")
    return {"status": result_text}


def get_action_log() -> list[dict]:
    return list(_ACTION_LOG)
