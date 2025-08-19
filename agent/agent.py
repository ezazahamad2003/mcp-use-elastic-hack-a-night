"""
This example demonstrates a dynamic, multi-step agent workflow
using a custom ServerManager.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from .server_manager import ElasticServerManager
from mcp_use import MCPClient, MCPAgent

# Load environment variables from .env file
load_dotenv()

client = MCPClient(config={})

search_agent = MCPAgent(
    llm=ChatOpenAI(model="gpt-4o"),
    use_server_manager=True,
    client=client,
    server_manager=ElasticServerManager(mcp_client=client),
)
