# mcp-use-elastic-hack-a-night

Hello, yall.

Today we want to try to see who is able to create a nice demo of an mcp agent that is able to search accross thousands of MCP servers. 

We provide you a csv of mcp servers which contain the following structure: 

```python 
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class MCPServer:
    """Dataclass representing an MCP Server from the public_servers_rows.csv dataset"""
    
    id: str
    name: str
    slug: str
    description: str
    namespace: str
    github_repo_url: str
    github_user_id: int
    github_stars: int
    github_readme_url: str
    github_icon_url: str
    spdx_license: Optional[str]
    categories: List[str]
    tools: List[Any]
    environment_variables_schema: Dict[str, Any]
    status: str
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    submitted_by: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    search_vector: str
    usable: bool
    config: Dict[str, Any]
```

the challenge is to create an MCP agent that can search and dynamically connect to a server to perform some interesting task.

# Set up

### Join Discord chat

[DISCORD JOIN LINK](https://discord.gg/WjFWaWD5)

We will use this to share links and/or information! You can use it to ask questions as well! 

### Clone the repo
```bash 
git clone git@github.com:mcp-use/mcp-use-elastic-hack-a-night.git
```

### 2. Set up an Elastic Cloud Serverless project

1. Log in or create an account at (elastic)[https://www.elastic.co/]
2. Select the Elasticsearch use case
3. Select the Elastic Cloud Serverless deployment option
4. Create a new index from file by clicking **Upload File** 
5. Upload the csv `public_server_rows.csv` in the repo
6. In the import settings, select advanced, copy and replace the mapping for the fields `created_at`, `updated_at` and `approved_at` to ensure the date fields are the correct types to be searchable.
```json
 "properties": {
      "created_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss.SSSX||yyyy-MM-dd HH:mm:ss.SSSSX||yyyy-MM-dd HH:mm:ss.SSSSSX||yyyy-MM-dd HH:mm:ss.SSSSSSX",
        "ignore_malformed": true
      },
      "updated_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss.SSSX||yyyy-MM-dd HH:mm:ss.SSSSX||yyyy-MM-dd HH:mm:ss.SSSSSX||yyyy-MM-dd HH:mm:ss.SSSSSSX",
        "ignore_malformed": true
      },
      "approved_at": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss.SSSX||yyyy-MM-dd HH:mm:ss.SSSSX||yyyy-MM-dd HH:mm:ss.SSSSSX||yyyy-MM-dd HH:mm:ss.SSSSSSX",
        "ignore_malformed": true
      }
    }
```
8. Create an API key and copy it in a `.env` file in the repo with name `ELASTIC_API_KEY`
9. Copy the Elastic host name for your index and copy the url in the `.env` file under `ELASTIC_INDEX_URL`

### Install UV
Install UV following the instructions from this [link](https://docs.astral.sh/uv/getting-started/installation/)

If you have another package manager it is fine, but following instructions might differ!

### Create and Activate the virtual environment

Run 
```bash 
uv venv
```
and activate
```
source .venv/bin/activate
```

### Install requirements

```bash
uv pip install -r requirements.txt
```

### Make sure search works
Run the following command to ensure the search functionality works: 
```bash 
python search.py
```
it should return some results like: 
```bash 
(elastic) ➜  elastic git:(main) ✗ python search.py
[{'_index': 'public_servers', '_id': 'F0AtupgBA9pwI1pDAbJB', '_score': 5.6726255, '_source': {'environment_variables_schema': '{"type":"object","required":[],"properties":{}}', 'description': 'Integrates with the Tavily API to provide web search capabilities, enabling internet searches and fact-checking for up-to-date information retrieval.', 'created_at': '2025-08-13 02:47:33.760164+00', 'github_repo_url': 'https://github.com/algonacci/mcp-tavily-search', 'github_stars': 0, 'tools': '[]', 'usable': False, 'search_vector': "'api':7 'capabl':12 'check':19 'date':24 'enabl':13 'fact':18 'fact-check':17 'inform':25 'integr':3 'internet':14 'provid':9 'retriev':26 'search':2,11,15 'tavili':1,6 'up-to-d':21 'web':10", 'updated_at': '2025-08-13 02:47:33.76017+00', 'approved_at': '2025-08-13 02:47:33.760172+00', 'name': 'Tavily Search', 'namespace': 'algonacci', 'id': 'ae6de2d8-f963-35d8-0af8-ba57be494c1b', 'categories': '["general"]', 'github_user_id': 0, 'config': '{"mcpServers":{"tavily_search":{"args":["--directory","%USERPROFILE%/Documents/GitHub/mcp-tavily-search","run","python","main.py"],"command":"uv"}}}', 'slug': 'algonacci-tavily-search-tavily-search', 'github_i\
```

> **⚠️ CAUTION**: Not all servers are properly formatted
The config returned by the search (contained in the CSV) will have one of the two following formats:

```json
{
    "mcpServers": {
        "server1": {"actual server config"}
    }
}
```
or 
```json
{
    // usual mcp configurations entries 
    "url":""
    "command":
}
```


# Time to Hack!

Now the goal should be clear, we want an agent that can automatically connect to MCP servers, now:
* a bonus point, is if it can ask the user credentials if they are needed.
* a second bonus point is if it can connect to multiple servers at once

To do this feel free to use any stack and approach you'd like, but we'd love you to use MCPAgent inside mcp-use, 
we have a starter example in this repo. Some explanation of how it works below.

Oth you can create your own agent, but here we strongly encourage to use MCPClient from mcp-use, also in the repo 
example.

Gooooo!

## Example Server Manager

The server manager is a class that can manage the tools MCPAgent has access to. 
At every step if you are using the server manager, the agent will refresh the tools available to the model based on the server manager tools property. 

Therefore you can use a client inside the server manager to pass tools into the agent, like in the example where we have a tool that: 
1 - Connects to the playwright server.
2 - Exposes the tools to the agent through the server manager.

```python
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
        print("Dynamic ServerManager initialized.")

    def add_tool(self, tool: BaseTool):
        self._server_tools[tool.name] = tool

    @property
    def tools(self) -> list[BaseTool]:
        """Dynamically assembles the list of available tools."""
        return self._management_tools + list(self._server_tools.values())

    def has_tool_changes(self, current_tool_names: set[str]) -> bool:
        """Checks if the toolset has changed by comparing tool names."""
        return {tool.name for tool in self.tools} != current_tool_names
```


## Links 

- [mcp-use GitHub Repository](https://github.com/mcp-use/mcp-use)
- [mcp-use Documentation](https://docs.mcp-use.com)
- [mcp-use PyPI Package](https://pypi.org/project/mcp-use/)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
