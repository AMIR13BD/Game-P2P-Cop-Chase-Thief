"""Async FastMCP client wrapper: bearer-header auth, one call per request (robust)."""

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


class PeerClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.headers = {"Authorization": f"Bearer {token}"}

    def _transport(self) -> StreamableHttpTransport:
        return StreamableHttpTransport(self.url, headers=self.headers)

    async def call(self, tool: str, payload: dict | None = None) -> dict:
        async with Client(self._transport()) as client:
            result = await client.call_tool(
                tool, {"payload": payload} if payload is not None else {}
            )
            return result.data

    async def version(self) -> dict:
        async with Client(self._transport()) as client:
            return (await client.call_tool("version", {})).data
