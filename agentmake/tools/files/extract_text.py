TOOL_SYSTEM = """You are an good at identifying a file path or an url from user request. Return an empty string '' for parameter `filepath_or_url` if no image is given."""

TOOL_SCHEMA = {
    "name": "extract_text",
    "description": "Extract the text content from a file or a webpage, and convert it into markdown format; a filepath or an URL is required.",
    "parameters": {
        "type": "object",
        "properties": {
            "filepath_or_url": {
                "type": "string",
                "description": "Either a file path or an url. Return an empty string '' if not given.",
            },
        },
        "required": ["filepath_or_url"],
    },
}

def extract_text(filepath_or_url: str="", **kwargs):
    from agentmake import extractText
    if not filepath_or_url:
        return None
    print(extractText(filepath_or_url))
    return ""

TOOL_FUNCTION = extract_text