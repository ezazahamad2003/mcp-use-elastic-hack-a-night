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

## Elastic

## mcp-use 
