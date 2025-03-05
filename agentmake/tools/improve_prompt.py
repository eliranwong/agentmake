TOOL_SYSTEM = ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Improve prompt clarity and writing style of the user request."""

def improve_prompt(messages, **kwargs):
    from agentmake import agentmake

    messages = agentmake(
        messages,
        system="improve_prompt",
        **kwargs,
    )
    if not kwargs.get("print_on_terminal"):
        # make sure the output is printed on terminal
        print(messages[-1].get("content", ""))
    return ""

TOOL_FUNCTION = improve_prompt