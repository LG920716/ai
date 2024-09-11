import requests
from promptflow.core import tool
import json

@tool
def call_api(session_id):
    url = "http://140.136.202.125/api/Context"

    params = {
        'sessionId': session_id
    }
    
    response = requests.get(url, params=params, verify=False)  # verify=False 是為了跳過 SSL 驗證

    response_json = response.json()
    results = []
    for item in response_json:
        json_data = {
            "questionQuestion": item.get("questionQuestion")
        }
        results.append(json.dumps(json_data, ensure_ascii=False))
    return "\n".join(results)