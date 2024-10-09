import json
import requests
from promptflow.core import tool

@tool
def call_api(session_id: str) -> str:
    url = "http://140.136.202.125/api/Context"
    params = {"sessionId": session_id}
    response = requests.get(url, params=params, verify=False)
    response_json = response.json()
    results = []
    for item in response_json:
        json_data = {"questionQuestion": item.get("questionQuestion")}
        results.append(json.dumps(json_data, ensure_ascii=False))
    return "\n".join(results)