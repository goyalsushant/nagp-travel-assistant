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
            "app.mcp_servers.weather_server",
        ],
    )

    print("=" * 60)
    print("Connecting to Weather MCP Server")
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

            print("\nCalling get_weather...")

            result = await session.call_tool(
                "get_weather",
                {
                    "city": "Singapore",
                    "forecast_days": 3,
                },
            )

            print("\n" + "=" * 60)
            print("WEATHER RESULT")
            print("=" * 60)

            for content in result.content:

                if hasattr(content, "text"):
                    print(content.text)
                else:
                    print(content)


if __name__ == "__main__":
    asyncio.run(main())