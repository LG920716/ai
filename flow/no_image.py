from promptflow.core import tool
from promptflow.contracts.multimedia import Image as PFImage
import requests
import io
from PIL import Image as PILImage

@tool
def no_image():
    return True