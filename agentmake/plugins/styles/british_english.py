"""
Review and refine written content to ensure it adheres to standard British English conventions.
"""

def improve_british_english(
    content: str,
    **kwargs,
):
    from agentmake import agentmake
    import json, os

    if not content:
        return ""

    schema = {
        "name": "improve_british_english",
        "description": "Review and refine written content to ensure it adheres to standard British English conventions.",
        "parameters": {
            "type": "object",
            "properties": {
                "improved_version": {
                    "type": "string",
                    "description": "Review and refine written content to ensure it adheres to standard British English conventions.",
                },
            },
            "required": ["improved_version"],
        },
    }

    print_on_terminal = kwargs.get("print_on_terminal")
    del kwargs["print_on_terminal"]
    messages = agentmake(
        content,
        system=os.path.join("styles", "british_english"),
        schema=schema,
        print_on_terminal=False,
        **kwargs,
    )

    try:
        improved_version = json.loads(messages[-1].get("content", "")).get("improved_version")
    except:
        return content
    if print_on_terminal:
        print(f"```improved_version\n{improved_version}\n```")
    return improved_version

CONTENT_PLUGIN = improve_british_english