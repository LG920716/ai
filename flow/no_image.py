from promptflow.core import tool

@tool
def no_image_handler() -> str:
    return "-"