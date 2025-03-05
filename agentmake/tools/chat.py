# a dummy tool to force fallback to regular chat completion

def chat(messages, **kwargs):
    return None

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Provide user with static knowledge-based information, without real-time updates."""

TOOL_FUNCTION = chat