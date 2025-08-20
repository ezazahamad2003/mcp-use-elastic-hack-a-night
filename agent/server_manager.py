import asyncio
import os
from typing import Dict, Any, List
from langchain_core.tools import BaseTool
from mcp_use.client import MCPClient
from mcp_use.managers.base import BaseServerManager
from mcp_use.adapters.langchain_adapter import LangChainAdapter
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


class SearchServersTool(BaseTool):
    """Searches the Elasticsearch index for MCP servers based on a query."""
    name: str = "search_servers"
    description: str = "Search for MCP servers in the database based on task description or capabilities (e.g., 'weather', 'web browsing', 'github')"
    server_manager: "ElasticServerManager"

    def _run(self, query: str) -> str:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, but _run should be sync
            # Let's create a simple sync version
            return self._sync_search(query)
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self._arun(query))
    
    def _sync_search(self, query: str) -> str:
        """Synchronous version of the search."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize Elasticsearch client
            client = Elasticsearch(
                os.getenv("ELASTIC_INDEX_URL"),
                api_key=os.getenv("ELASTIC_API_KEY")
            )
            
            # Create search query with relevance scoring (simplified to avoid date issues)
            search_query = {
                "query": {
                    "function_score": {
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": ["description^3", "name^5", "slug", "namespace"]
                            }
                        },
                        "functions": [
                            {"filter": {"term": {"usable": True}}, "weight": 2.0},
                            {"field_value_factor": {"field": "github_stars", "modifier": "log1p", "missing": 0}}
                        ],
                        "score_mode": "sum",
                        "boost_mode": "multiply"
                    }
                },
                "size": 5
            }
            
            # Perform search
            response = client.search(index="public_servers", body=search_query)
            
            if not response["hits"]["hits"]:
                return f"No servers found matching '{query}'. Try different keywords."
            
            # Format results
            results = []
            for i, hit in enumerate(response["hits"]["hits"], 1):
                server = hit["_source"]
                results.append(
                    f"{i}. **{server.get('name', 'Unknown')}**\n"
                    f"   - Description: {server.get('description', 'No description')}\n"
                    f"   - Stars: {server.get('github_stars', 0)}\n"
                    f"   - Install: {server.get('install_command', 'No install command')}\n"
                    f"   - ID: {hit['_id']}"
                )
            
            return f"Found {len(results)} servers for '{query}':\n\n" + "\n\n".join(results) + f"\n\nUse 'connect_server' with the server ID to connect."
            
        except Exception as e:
            return f"Error searching servers: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Search for servers matching the query."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize Elasticsearch client
            client = Elasticsearch(
                os.getenv("ELASTIC_INDEX_URL"),
                api_key=os.getenv("ELASTIC_API_KEY")
            )
            
            # Create search query with relevance scoring (simplified to avoid date issues)
            search_query = {
                "query": {
                    "function_score": {
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": ["description^3", "name^5", "slug", "namespace"]
                            }
                        },
                        "functions": [
                            {"filter": {"term": {"usable": True}}, "weight": 2.0},
                            {"field_value_factor": {"field": "github_stars", "modifier": "log1p", "missing": 0}}
                        ],
                        "score_mode": "sum",
                        "boost_mode": "multiply"
                    }
                },
                "size": 5
            }
            
            # Perform search
            response = client.search(index="public_servers", body=search_query)
            
            if not response["hits"]["hits"]:
                return f"No servers found matching '{query}'. Try different keywords."
            
            # Format results
            results = []
            for i, hit in enumerate(response["hits"]["hits"], 1):
                server = hit["_source"]
                results.append(
                    f"{i}. **{server.get('name', 'Unknown')}**\n"
                    f"   - Description: {server.get('description', 'No description')}\n"
                    f"   - Stars: {server.get('github_stars', 0)}\n"
                    f"   - Install: {server.get('install_command', 'No install command')}\n"
                    f"   - ID: {hit['_id']}"
                )
            
            return f"Found {len(results)} servers for '{query}':\n\n" + "\n\n".join(results) + f"\n\nUse 'connect_server' with the server ID to connect."
            
        except Exception as e:
            return f"Error searching servers: {str(e)}"


class ConnectServerTool(BaseTool):
    """Connects to a specific MCP server by ID found in the search results."""
    name: str = "connect_server"
    description: str = "Connect to a specific MCP server using its ID from search results"
    server_manager: "ElasticServerManager"

    def _run(self, server_id: str) -> str:
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context, create sync version
            return self._sync_connect(server_id)
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(self._arun(server_id))
    
    def _sync_connect(self, server_id: str) -> str:
        """Synchronous version of server connection (placeholder)."""
        return f"Sync connection to server {server_id} not yet implemented. Use async version or implement sync connection logic here."

    async def _arun(self, server_id: str) -> str:
        """Connect to a server by its ID."""
        try:
            # Load environment variables
            load_dotenv()
            
            # Initialize Elasticsearch client
            client = Elasticsearch(
                os.getenv("ELASTIC_INDEX_URL"),
                api_key=os.getenv("ELASTIC_API_KEY")
            )
            
            # Get server details by ID
            response = client.get(index="public_servers", id=server_id)
            server = response["_source"]
            
            # Extract connection info
            server_name = server.get("slug", server.get("name", server_id))
            install_command = server.get("install_command")
            
            if not install_command:
                return f"No install command found for server {server_name}"
            
            # Parse install command to get MCP server config
            # Most commands are like "npx @modelcontextprotocol/server-name" or "pip install package-name"
            if install_command.startswith("npx "):
                command = "npx"
                args = install_command[4:].split()
            elif install_command.startswith("pip install "):
                # For pip packages, we need a different approach
                return f"Server {server_name} requires pip install. Manual setup needed: {install_command}"
            else:
                # Try to parse generic command
                parts = install_command.split()
                command = parts[0] if parts else "node"
                args = parts[1:] if len(parts) > 1 else []
            
            # Connect to MCP client
            mcp_client = self.server_manager.mcp_client
            adapter = self.server_manager.adapter
            
            # Add server if not exists
            if server_name not in mcp_client.get_server_names():
                mcp_client.add_server(server_name, {"command": command, "args": args})
            
            # Create session
            try:
                mcp_client.get_session(server_name)
            except ValueError:
                await mcp_client.create_session(server_name)
            
            # Cache the server's tools
            if server_name not in self.server_manager._server_tools:
                connector = mcp_client.get_session(server_name).connector
                new_tools = await adapter._create_tools_from_connectors([connector])
                self.server_manager._server_tools.update({tool.name: tool for tool in new_tools})
            
            # Set as active server
            self.server_manager.active_server = server_name
            num_tools = len([t for t in self.server_manager._server_tools.values() if not t.name.startswith(('search_servers', 'connect_server', 'connect_to_playwright'))])
            
            return f"Successfully connected to {server.get('name', server_name)}! {num_tools} tools are now available."
            
        except Exception as e:
            return f"Error connecting to server {server_id}: {str(e)}"


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
        self._management_tools: list[BaseTool] = [
            SearchServersTool(server_manager=self),
            ConnectServerTool(server_manager=self),
            ConnectPlaywrightTool(server_manager=self)
        ]
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
