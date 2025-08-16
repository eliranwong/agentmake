TOOL_SYSTEM = """You are an AI assistant. Generate a response based on user input."""

def share(generated_response: str, **kwargs):
    import pydoc
    generated_response = generated_response.replace('"', '\\"') # required
    pydoc.pipepager(generated_response, cmd="termux-share -a send")
    return ""

TOOL_SCHEMA = {
    "name": "share",
    "description": f'''Share a generated message with other apps''',
    "parameters": {
        "type": "object",
        "properties": {
            "generated_response": {
                "type": "string",
                "description": "The generated response.",
            },
        },
        "required": ["generated_response"],
    },
}

TOOL_FUNCTION = share