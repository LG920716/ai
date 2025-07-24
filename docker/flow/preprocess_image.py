import requests
from PIL import Image
from io import BytesIO
from promptflow.core import tool

@tool
def load_image_from_url(url: str):
    result = {
        "image": None,
        "has_image": False,
    }

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 如果不是 200，會丟出例外
        image = Image.open(BytesIO(response.content))
        image.load()  # 確保整張圖片都載入進來
        result["image"] = image
        result["has_image"] = True
    except Exception as e:
        print(f"載入圖片失敗：{e}")

    return result