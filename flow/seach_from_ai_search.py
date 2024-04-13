from promptflow import tool
from openai import OpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure.core.credentials import AzureKeyCredential
import json

#Azure AI Search setting
AZURE_SEARCH_SERVICE = "fju-basic"
AZURE_SEARCH_INDEX = "qampus-index"
AZURE_SEARCH_KEY = "WIqsQwWj6JuykjPSxnEWUgZPBZl8Q9KkRQGjmqwxcbAzSeCOICL9"

search_client = SearchClient(
    endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY))
    

@tool
def my_python_tool(input: str, input_embedding: str) -> str:
    r = search_client.search(input, 
                        query_type=QueryType.SEMANTIC, 
                        query_language="zh-tw",
                        semantic_configuration_name="default", 
                        top=3,
                        query_caption="extractive",
                        query_answer="extractive",
                        vector=input_embedding, 
                        top_k=50, 
                        vector_fields="embedding")
    results = []
    for json_doc in r:
        #print(json_doc)
        json_data = {
            "content": json_doc["content"],
            "metadata_storage_name": json_doc["metadata_storage_name"],
            "sourcefile": json_doc["sourcefile"]
        }
        results.append(json.dumps(json_data, ensure_ascii=False))
    content = "\n".join(results)
    return content
