import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "http://localhost:3000/mcp"


async def main():
    print("Connecting to MCP server...")

    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            print("Initializing MCP session...")

            await session.initialize()

            print("\nConnected successfully.")

            result = await session.list_tools()

            print("\nAvailable tools:")

            for tool in result.tools:
                print(f"- {tool.name}: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())