"""
Refine and optimize user requests to achieve more effective and efficient task resolution.
"""

def improve_prompt(
    content: str,
    **kwargs,
):
    from agentmake import agentmake
    import json

    if not content:
        return ""

    schema = {
        "name": "improve_prompt",
        "description": "Refine and optimize user requests to achieve more effective and efficient task resolution.",
        "parameters": {
            "type": "object",
            "properties": {
                "improved_prompt": {
                    "type": "string",
                    "description": "Refine and optimize user requests to achieve more effective and efficient task resolution.",
                },
            },
            "required": ["improved_prompt"],
        },
    }

    print_on_terminal = kwargs.get("print_on_terminal")
    del kwargs["print_on_terminal"]
    messages = agentmake(
        content,
        system="improve_prompt",
        schema=schema,
        print_on_terminal=False,
        **kwargs,
    )

    try:
        improved_prompt = json.loads(messages[-1].get("content", "")).get("improved_prompt")
    except:
        return content
    if print_on_terminal:
        print(f"```improved_version\n{improved_prompt}\n```")
    return improved_prompt

CONTENT_PLUGIN = improve_prompt