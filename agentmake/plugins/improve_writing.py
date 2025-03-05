def improve_writing(
    content,
    **kwargs,
):
    from agentmake import agentmake
    import json, os

    DEFAULT_WRITING_STYLE = os.getenv('DEFAULT_WRITING_STYLE') if os.getenv('DEFAULT_WRITING_STYLE') else 'standard English'

    TOOL_SYSTEM = f"""# Role
You are an excellent writer.

# Job description
Your job is to improve my writing sytle only, without extra comments or explantions.

# Expertise
Your expertise lies in proofreading and improving my writing.

# Instruction
You improve the writing in the user's input, according to {DEFAULT_WRITING_STYLE}.
Remember, do NOT give me extra comments explanations.  I want only the 'improved_writing'"""

    TOOL_SCHEMA = {
        "name": "improve_writing",
        "description": f"Improve user writing, according to {DEFAULT_WRITING_STYLE}",
        "parameters": {
            "type": "object",
            "properties": {
                "improved_writing": {
                    "type": "string",
                    "description": "The improved version of my writing",
                },
            },
            "required": ["improved_writing"],
        },
    }

    print_on_terminal = kwargs.get("print_on_terminal")
    del kwargs["print_on_terminal"] # avoid printing dictionary output
    messages = agentmake(
        content,
        system=TOOL_SYSTEM,
        schema=TOOL_SCHEMA,
        print_on_terminal=False,
        **kwargs,
    )
    improved_writing = json.loads(messages[-1]["content"])["improved_writing"]
    if print_on_terminal:
        print(f"```improved_writing\n{improved_writing}\n```")
    return improved_writing

CONTENT_PLUGIN = improve_writing