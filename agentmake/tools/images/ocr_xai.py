TOOL_SYSTEM = f"""You are an good at identifying an image path or an image url from user request. Return an empty string '' for parameter `image_path_or_url` if no image is given."""

TOOL_SCHEMA = {
    "name": "ocr_azure",
    "description": "Extract text from an image file or url.",
    "parameters": {
        "type": "object",
        "properties": {
            "image_path_or_url": {
                "type": "string",
                "description": "Either an image path or an image url. Return an empty string '' if not given.",
            },
        },
        "required": ["image_path_or_url"],
    },
}

def ocr_ollama(image_path_or_url: str="", **kwargs):

    from agentmake import extractText
    import os

    if not image_path_or_url:
        return None
    XAI_VISUAL_MODEL = os.getenv("XAI_VISUAL_MODEL") if os.getenv("XAI_VISUAL_MODEL") else "grok-2-vision-latest"
    print(extractText(image_path_or_url, image_backend="xai", llm_model=XAI_VISUAL_MODEL))
    return ""

TOOL_FUNCTION = ocr_ollama