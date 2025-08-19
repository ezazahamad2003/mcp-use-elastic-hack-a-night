# Installing the Elastic Python Client & Performing a Search

## 1. Install the Elasticsearch Python Client
```bash
pip install elasticsearch
```
---

## 2. Import and Initialize the Client
Create a `.env` file with your Elasticsearch connection details:
```bash
ELASTIC_URL=https://your-cluster.es.us-central1.gcp.cloud.es.io
ELASTIC_API_KEY=your_api_key_here
```

Then, in Python:
```python
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the client
client = Elasticsearch(
    os.getenv("ELASTIC_URL"),
    api_key=os.getenv("ELASTIC_API_KEY")
)
```

---

## 3. Perform a Simple Search
```python
response = client.search(
    index="your-index-name",
    query={
        "match": {
            "description": "your search text"
        }
    }
)

# Print results
for hit in response["hits"]["hits"]:
    print(hit["_source"])
```

---

## 4. Example: Range Query
```python
response = client.search(
    index="your-index-name",
    query={
        "range": {
            "created_at": {
                "gte": "2025-01-01",
                "lte": "2025-12-31"
            }
        }
    }
)
```

---

## 5. Useful Links
- [Elasticsearch Python Client Docs](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
- [Query DSL Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)

## 6. Search Query Examples to Find and Rank MCP Servers

### 1. Text relevance with popularity and recency


```json
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "<TASK TEXT HERE>",
          "fields": ["description^3", "name^5", "slug", "namespace"]
        }
      },
      "functions": [
        { "filter": { "term": { "usable": true }}, "weight": 2.0 },
        { "field_value_factor": { "field": "github_stars", "modifier": "log1p", "missing": 0 }},
        { "gauss": { "updated_at": { "origin": "now", "scale": "30d", "decay": 0.5 }}}
      ],
      "score_mode": "sum",
      "boost_mode": "multiply"
    }
  },
  "size": 5
}
```

---

### 2. Browsing / web search servers (filter + sort)


```json
{
  "query": {
    "bool": {
      "must": [
        { "multi_match": {
          "query": "browser web search crawl scrape playwright tavily serp",
          "fields": ["description", "name"]
        }}
      ],
      "filter": [
        { "term": { "usable": true } }
      ]
    }
  },
  "sort": [{ "github_stars": "desc" }],
  "size": 5
}
```

---

### 3. Weather / climate (recent, approved, usable)


```json
{
  "query": {
    "bool": {
      "must": [
        { "multi_match": {
          "query": "weather climate forecast",
          "fields": ["description", "name"]
        }}
      ],
      "filter": [
        { "term": { "usable": true }},
        { "term": { "status": "approved" }},
        { "range": { "updated_at": { "gte": "now-180d" }}}
      ]
    }
  },
  "size": 5
}
```

---

### 4. GitHub-popular candidates for a task (stars ≥ 50)

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "description": "github stars ranking" } }
      ],
      "filter": [
        { "range": { "github_stars": { "gte": 50 }}}
      ]
    }
  },
  "sort": [{ "github_stars": "desc" }],
  "size": 5
}
```

---

## More Links
- [Retrievers](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers)
- [Multi-match query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query)
- [Function score query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query)
- [Boolean query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query)
- [Range query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-range-query)
- [Sorting](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/sort-search-results)
- [Date Math](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/common-options#date-math)
- [Date Range Aggregations](https://www.elastic.co/docs/reference/aggregations/search-aggregations-bucket-daterange-aggregation?utm_source=chatgpt.com)
