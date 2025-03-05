# a dummy tool to force fallback to regular chat completion

def auto_heal(messages, **kwargs):
    from agentmake import agentmake
    from copy import deepcopy
    import os

    MAXIMUM_AUTO_HEALING = int(os.getenv("MAXIMUM_AUTO_HEALING")) if os.getenv("MAXIMUM_AUTO_HEALING") else 3
    
    messages_copy = deepcopy(messages)
    messages_copy = agentmake(messages_copy, tool="magic", **kwargs)
    trial = 0
    while "```buggy_python_code\n" in messages_copy[-1].get("content", "") and trial < MAXIMUM_AUTO_HEALING:
        messages_copy = agentmake(messages_copy, tool="correct_python", **kwargs)
        trial += 1
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Execute various computing tasks or gain access to device information, with additional capabilities to automatically diagnose and correct broken Python code."""

TOOL_FUNCTION = auto_heal