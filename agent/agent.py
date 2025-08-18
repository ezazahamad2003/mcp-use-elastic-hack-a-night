"""
This example demonstrates a dynamic, multi-step agent workflow
using a custom ServerManager.
"""
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from mcp_use.agents import MCPAgent
from .server_manager import ElasticServerManager
from mcp_use.client import MCPClient

# Load environment variables from .env file
load_dotenv()


async def main():
    """Run the dynamic, multi-step agent workflow."""
    print("🚀 Starting dynamic tool loading example...")

    client = MCPClient(config={})

    agent = MCPAgent(
        llm=ChatOpenAI(model="gpt-4o"),
        use_server_manager=True,
        server_manager=ElasticServerManager(mcp_client=client),
    )

    # --- Step 1: Connect to the Playwright server to get browsing tools ---
    print("\n--- Agent Step 1: Connecting to Playwright Server ---")
    result = await agent.run(
        "I need to browse the web. Please connect to the Playwright server. Then google for 'best places to visit in Barcelona'",
    )
    print(result)
    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
