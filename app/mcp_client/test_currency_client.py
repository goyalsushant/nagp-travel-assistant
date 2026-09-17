import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import (
    StdioServerParameters,
    stdio_client,
)


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp_servers.currency_server",
        ],
    )

    print("=" * 60)
    print("Connecting to Currency MCP Server")
    print("=" * 60)

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\nMCP connection established.")

            tools = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools.tools:
                print(f"- {tool.name}")
                print(f"  {tool.description}")

            print("\nCalling convert_currency...")

            result = await session.call_tool(
                "convert_currency",
                {
                    "amount": 50000,
                    "from_currency": "INR",
                    "to_currency": "SGD",
                },
            )

            print("\n" + "=" * 60)
            print("CURRENCY RESULT")
            print("=" * 60)

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)


if __name__ == "__main__":
    asyncio.run(main())