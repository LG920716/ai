from promptflow.core import tool
from promptflow.contracts.multimedia import Image as PFImage
from PIL import Image as PILImage

@tool
def no_image(no_image, image, title_categroy):
    return True