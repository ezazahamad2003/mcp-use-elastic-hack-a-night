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

### 1 Clone the repo
```bash 
git clone git@github.com:mcp-use/mcp-use-elastic-hack-a-night.git
```

### Set up Elastic

1 - Log in or create an account at (elastic)[https://www.elastic.co/]
2 - Create a new index from file by clicking **Upload File** 
3 - Upload the csv `public_server_rows.csv` in the repo
4 - Create an API key and copy it in a `.env` file in the repo with name `ELASTIC_API_KEY`
5 - Copy the Elastic host name for your index and copy the url in the `.env` file under `ELASTIC_INDEX_URL`

### 2 Install UV
Install UV following the instructions from this [link](https://docs.astral.sh/uv/getting-started/installation/)

### 3 Create and Activate the virtual environment

Run 
```bash 
uv venv
```
and activate
```
source .venv/bin/activate
```

### 4 Install requirements

```bash
uv pip install -r requirements.txt
```

### 5 Make sure search works
Run the following command to ensure the search functionality works: 
```bash 
python search.py
```
it should return some results like: 
```bash 
(elastic) ➜  elastic git:(main) ✗ python search.py
[{'_index': 'public_servers', '_id': 'F0AtupgBA9pwI1pDAbJB', '_score': 5.6726255, '_source': {'environment_variables_schema': '{"type":"object","required":[],"properties":{}}', 'description': 'Integrates with the Tavily API to provide web search capabilities, enabling internet searches and fact-checking for up-to-date information retrieval.', 'created_at': '2025-08-13 02:47:33.760164+00', 'github_repo_url': 'https://github.com/algonacci/mcp-tavily-search', 'github_stars': 0, 'tools': '[]', 'usable': False, 'search_vector': "'api':7 'capabl':12 'check':19 'date':24 'enabl':13 'fact':18 'fact-check':17 'inform':25 'integr':3 'internet':14 'provid':9 'retriev':26 'search':2,11,15 'tavili':1,6 'up-to-d':21 'web':10", 'updated_at': '2025-08-13 02:47:33.76017+00', 'approved_at': '2025-08-13 02:47:33.760172+00', 'name': 'Tavily Search', 'namespace': 'algonacci', 'id': 'ae6de2d8-f963-35d8-0af8-ba57be494c1b', 'categories': '["general"]', 'github_user_id': 0, 'config': '{"mcpServers":{"tavily_search":{"args":["--directory","%USERPROFILE%/Documents/GitHub/mcp-tavily-search","run","python","main.py"],"command":"uv"}}}', 'slug': 'algonacci-tavily-search-tavily-search', 'github_i\
```

# Time to Hack!

Now the goal should be clear, we want an agent that can automatically connect to MCP servers, now:
* a bonus point, is if it can ask the user credentials if they are needed.
* a second bonus point is if it can connect to multiple servers at once

To do this feel free to use any stack you'd like, but we'd love you to use MCPAgent inside mcp-use, 
we have a starter example in this repo. 

Oth you can create your own agent, but here we strongly encourage to use MCPClient from mcp-use, also in the repo 
example.

Gooooo!

