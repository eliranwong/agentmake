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

    from agentmake import extractText, OllamaAI
    import os
    from agentmake import OLLAMA_FOUND, OLLAMA_NOT_FOUND_MESSAGE
    if not OLLAMA_FOUND:
        print(OLLAMA_NOT_FOUND_MESSAGE)
        return ""

    if not image_path_or_url:
        return None
    OLLAMA_VISUAL_MODEL = os.getenv("OLLAMA_VISUAL_MODEL") if os.getenv("OLLAMA_VISUAL_MODEL") else "granite3.2-vision"
    OllamaAI.downloadModel(OLLAMA_VISUAL_MODEL)
    print(extractText(image_path_or_url, image_backend="ollama", llm_model=OLLAMA_VISUAL_MODEL))
    return ""

TOOL_FUNCTION = ocr_ollama