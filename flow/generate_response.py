from promptflow.core import tool

@tool
def generate_response(title: str, title_categroy: str, no_image: str, image: str) -> dict:
    # 判斷 title_result
    title_result = "N" if title == "N" else "Y"

    # 判斷 image_result
    if no_image == "-":
        image_result = "-"
    elif image == "N":
        image_result = "N"
    else:
        image_result = "Y"

    # 判斷 category
    if image_result == "-" and title == "N":
        category = "-"
    elif image != "N":
        category = image  # 代表 image 有分類
    else:
        category = title_categroy  # fallback 使用 title 的分類

    return {
        "title_result": title_result,
        "image_result": image_result,
        "category": category
    }