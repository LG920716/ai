from promptflow.core import tool
from promptflow.contracts.multimedia import Image as PFImage
import requests
import io
from PIL import Image as PILImage, UnidentifiedImageError

@tool
def image_check(image_url: str) -> dict:
    result = {
        "image": None,
        "has_image": False,
    }

    if not image_url or not image_url.startswith(('http://', 'https://')):
        return result

    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": image_url
        }

        response = requests.get(image_url, headers=headers, stream=True, timeout=5)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return result

        if len(response.content) < 1024:  # 太小，可能是 HTML 錯誤頁面
            return result

        image_bytes_io = io.BytesIO(response.content)

        try:
            pil_image = PILImage.open(image_bytes_io).convert("RGB")
            image_bytes_io.seek(0)
        except (UnidentifiedImageError, OSError):
            return result

        result["image"] = PFImage(data=image_bytes_io.getvalue(), mime_type=content_type)
        result["has_image"] = True

    except requests.RequestException:
        pass
    except Exception:
        pass

    return result
