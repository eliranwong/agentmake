def improve_prompt(
    content: str,
    **kwargs,
):
    from agentmake import agentmake
    if not content:
        return ""
    if kwargs.get("print_on_terminal"):
        print("```improved_prompt")
    messages = agentmake(
        content,
        system="improve_prompt",
        **kwargs,
    )
    if kwargs.get("print_on_terminal"):
        print("```")
    improved_prompt = messages[-1].get("content", "").strip()
    if not improved_prompt:
        return content
    return improved_prompt

CONTENT_PLUGIN = improve_prompt