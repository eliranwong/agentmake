# a dummy tool to force fallback to regular chat completion

def chat(messages, **kwargs):
    return None

TOOL_SCHEMA = {}

TOOL_FUNCTION = chat