# a shortcut tool to perform online searches

def web(messages, **kwargs):
    from agentmake import agentmake
    import os
    DEFAULT_ONLINE_SEARCH_TOOL=os.getenv("DEFAULT_ONLINE_SEARCH_TOOL") if os.getenv("DEFAULT_ONLINE_SEARCH_TOOL") else "search/google"
    messages = agentmake(messages, tool=DEFAULT_ONLINE_SEARCH_TOOL, **kwargs)
    return messages

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Perform online searches to obtain the latest and most up-to-date, real-time information"""

TOOL_FUNCTION = web