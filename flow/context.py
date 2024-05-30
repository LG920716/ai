import requests
from promptflow.core import tool

@tool
def call_api(session_id):
    url = "http://140.136.202.125/api/context"

    params = {
        'sessionId': session_id
    }

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
