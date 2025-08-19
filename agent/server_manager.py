import asyncio
from langchain_core.tools import BaseTool
from mcp_use.client import MCPClient
from mcp_use.managers.base import BaseServerManager
from mcp_use.adapters.langchain_adapter import LangChainAdapter


class ConnectPlaywrightTool(BaseTool):
    """Connects to the Playwright server and makes its tools active."""
    name: str = "connect_to_playwright_server"
    description: str = "Connects to the Playwright server to enable web browsing and scraping tools."
    server_manager: "ElasticServerManager"

    def _run(self) -> str:
        return asyncio.run(self._arun())

    async def _arun(self) -> str:
        """Connects to the server, caches its tools, and sets it as active."""
        client = self.server_manager.mcp_client
        adapter = self.server_manager.adapter
        server_name = "playwright"

        # 1. Connect and create session if needed
        if server_name not in client.get_server_names():
            client.add_server(server_name, {"command": "npx", "args": ["@playwright/mcp@latest"]})
        try:
            client.get_session(server_name)
        except ValueError:
            await client.create_session(server_name)

        # 2. Cache the server's tools
        if server_name not in self.server_manager._server_tools:
            playwright_connector = client.get_session(server_name).connector
            new_tools = await adapter._create_tools_from_connectors([playwright_connector])
            self.server_manager._server_tools.update({tool.name: tool for tool in new_tools})

        # 3. Set the server as active
        self.server_manager.active_server = server_name
        num_tools = len(self.server_manager._server_tools)
        return f"Successfully connected to Playwright. {num_tools} web browsing tools are now available."


class ElasticServerManager(BaseServerManager):
    """A ServerManager that dynamically loads tools from a connected server."""
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.adapter = LangChainAdapter()
        self._server_tools: dict[str, BaseTool] = {}
        self._management_tools: list[BaseTool] = [ConnectPlaywrightTool(server_manager=self)]
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    def add_tool(self, tool: BaseTool):
        self._server_tools[tool.name] = tool

    @property
    def tools(self) -> list[BaseTool]:
        """Dynamically assembles the list of available tools."""
        return self._management_tools + list(self._server_tools.values())

    def has_tool_changes(self, current_tool_names: set[str]) -> bool:
        """Checks if the toolset has changed by comparing tool names."""
        return {tool.name for tool in self.tools} != current_tool_names
