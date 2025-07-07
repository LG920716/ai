from promptflow.core import tool
from promptflow.contracts.multimedia import Image as PFImage
import requests
import io
from PIL import Image as PILImage

@tool
def image_check(image_url: str) -> dict:
    result = {
        "image": None,
        "has_image": False,
    }

    if not image_url or not image_url.startswith(('http://', 'https://')):
        return result

    try:
        response = requests.get(image_url, stream=True, timeout=5)
        response.raise_for_status()

        image_bytes_io = io.BytesIO(response.content)

        try:
            image_bytes_io.seek(0)
            pil_image = PILImage.open(image_bytes_io)
            pil_image.verify()
            image_bytes_io.seek(0)

        except PILImage.UnidentifiedImageError:
            return result

        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        if not content_type.startswith('image/'):
            return result

        result["image"] = PFImage(data=image_bytes_io.getvalue(), mime_type=content_type)
        result["has_image"] = True

    except requests.exceptions.RequestException:
        pass
    except Exception:
        pass

    return result