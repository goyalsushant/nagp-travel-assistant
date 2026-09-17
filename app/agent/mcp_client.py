import asyncio
import sys
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)


class MCPClientManager:
    """
    Manages connections to the Travel Assistant MCP servers.

    Currently supported:
        - Weather MCP
        - Currency MCP
    """

    def __init__(self):
        self.sessions: dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()

    async def connect_server(
        self,
        server_name: str,
        module_name: str,
    ):
        """
        Start an MCP server and establish a client session.
        """

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-m",
                module_name,
            ],
        )

        read, write = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()

        self.sessions[server_name] = session

        print(
            f"MCP server connected: {server_name}"
        )

    async def connect_all(self):
        """
        Connect to all MCP servers used by the application.
        """

        await self.connect_server(
            "weather",
            "app.mcp_servers.weather_server",
        )

        await self.connect_server(
            "currency",
            "app.mcp_servers.currency_server",
        )

    async def list_tools(self) -> dict[str, list[Any]]:
        """
        Return tools exposed by all connected MCP servers.
        """

        all_tools = {}

        for server_name, session in self.sessions.items():

            response = await session.list_tools()

            all_tools[server_name] = response.tools

        return all_tools

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: dict[str, Any],
    ):
        """
        Call an MCP tool on a connected server.
        """

        if server_name not in self.sessions:
            raise RuntimeError(
                f"MCP server '{server_name}' is not connected."
            )

        session = self.sessions[server_name]

        return await session.call_tool(
            tool_name,
            arguments,
        )

    async def close(self):
        """
        Close all MCP connections.
        """

        await self.exit_stack.aclose()

    async def __aenter__(self):
        await self.connect_all()
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        await self.close()


async def main():

    print("=" * 60)
    print("TRAVEL ASSISTANT MCP CLIENT")
    print("=" * 60)

    async with MCPClientManager() as manager:

        print("\nConnected MCP servers:")
        print("- Weather")
        print("- Currency")

        print("\nAvailable tools:")

        tools = await manager.list_tools()

        for server_name, server_tools in tools.items():

            print(f"\n[{server_name.upper()}]")

            for tool in server_tools:

                print(f"- {tool.name}")
                print(
                    f"  {tool.description}"
                )

        print("\n" + "=" * 60)
        print("Testing Weather MCP")
        print("=" * 60)

        weather_result = await manager.call_tool(
            "weather",
            "get_weather",
            {
                "city": "Singapore",
                "forecast_days": 3,
            },
        )

        for content in weather_result.content:

            if hasattr(content, "text"):
                print(content.text)
            else:
                print(content)

        print("\n" + "=" * 60)
        print("Testing Currency MCP")
        print("=" * 60)

        currency_result = await manager.call_tool(
            "currency",
            "convert_currency",
            {
                "amount": 50000,
                "from_currency": "INR",
                "to_currency": "SGD",
            },
        )

        for content in currency_result.content:

            if hasattr(content, "text"):
                print(content.text)
            else:
                print(content)


if __name__ == "__main__":
    asyncio.run(main())