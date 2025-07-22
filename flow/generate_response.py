from promptflow.core import tool

@tool
def generate_response(title: str, title_category: str, no_image: str, image: str) -> dict:
    result = {
        "title_result": title,
        "image_result": "-",
        "category": "-"
    }

    if title == "Y":
        result["category"] = title_category

    elif no_image != "-":
        if image == "N":
            result["image_result"] = "N"
            result["category"] = "非成人商品"
        else:
            result["image_result"] = "Y"
            result["category"] = image

    return result
