import json
import requests
from promptflow.core import tool
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@tool
def call_api(session_id: str) -> str:
    # 建立 session 並設定重試策略
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    
    url = "http://140.136.202.125/api/Context"
    params = {"sessionId": session_id}
    
    try:
        # 使用 session 來發送請求，這樣重試策略才能生效
        response = session.get(url, params=params, verify=False)
        response.raise_for_status()  # 檢查回應狀態碼，觸發 HTTPError 異常
        
        # 處理 API 回應，並確認回應是 JSON 格式
        response_json = response.json()
        
        # 如果回應是一個列表，進行迭代
        if isinstance(response_json, list):
            results = []
            for item in response_json:
                # 確認每個項目是否包含 "questionQuestion" 鍵
                json_data = {"questionQuestion": item.get("questionQuestion")}
                results.append(json.dumps(json_data, ensure_ascii=False))
            return "\n".join(results)
        else:
            return "Unexpected response format: Expected a list."
    
    except requests.exceptions.RequestException as e:
        return f"HTTP 請求失敗: {e}"
    except json.JSONDecodeError:
        return "無法解析回應為 JSON 格式"
