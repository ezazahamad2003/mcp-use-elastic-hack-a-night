from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

client = Elasticsearch(
    os.getenv("ELASTIC_INDEX_URL"),
    api_key=os.getenv("ELASTIC_API_KEY")
)

retriever_object = {
    "standard": {
        "query": {
            "multi_match": {
                "query": "Internet browsing",
                "fields": [
                    "description"
                ]
            }
        }
    }
}

search_response = client.search(
    index="public_servers",
    retriever=retriever_object,
)
print(search_response['hits']['hits'])