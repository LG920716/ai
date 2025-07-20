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
        # 嘗試下載圖片
        response = requests.get(image_url, stream=True, timeout=5)
        response.raise_for_status()

        # 轉為 BytesIO
        image_bytes_io = io.BytesIO(response.content)

        # 驗證是否為有效圖片
        try:
            pil_image = PILImage.open(image_bytes_io)
            pil_image.verify()  # 這會破壞 stream pointer，要重新 seek
            image_bytes_io.seek(0)
        except UnidentifiedImageError:
            return result
        except Exception:
            return result

        # 確認 Content-Type 是圖片格式
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            return result

        # 包裝成 PFImage 格式給 PromptFlow
        result["image"] = PFImage(data=image_bytes_io.getvalue(), mime_type=content_type)
        result["has_image"] = True

    except requests.RequestException:
        pass
    except Exception:
        pass

    return result