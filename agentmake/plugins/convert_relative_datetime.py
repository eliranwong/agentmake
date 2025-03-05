def convert_relative_datetime(
    content,
    **kwargs,
):
    import datetime, re

    CURRENT_DATETIME = re.sub(r"\..*?$", "", str(datetime.datetime.now()))
    CURRENT_DAY = datetime.date.today().strftime("%A")

    TOOL_SYSTEM = f"""# Role
You are an expert converting relative dates and times into absolute ones.

# Job description
* You convert any relative dates and times in the my input, into exact dates and times, based on the reference that the current datetime is {CURRENT_DATETIME} ({CURRENT_DAY}).
* You provide me with the revised writing only, without additional information or explanation about the changes you have made.
* If there is no change, return to my original writing to me, without any additional information or comments.

# Expertise
Your expertise lies in identifying relative dates and times from the my input and converting them to the absolute ones.

# Instruction
Provide me with the revised writing only.
Remember, do NOT give me extra comments or explanations.  I want the 'revised_writing' only."""

    TOOL_SCHEMA = {
        "name": "convert_relative_datetime",
        "description": f"""Convert relative dates and times into absolute one, based on the reference that the current datetime is {CURRENT_DATETIME} ({CURRENT_DAY}).""",
        "parameters": {
            "type": "object",
            "properties": {
                "revised_writing": {
                    "type": "string",
                    "description": "The revised version of user writing",
                },
            },
            "required": ["revised_writing"],
        },
    }

    from agentmake import agentmake
    import json
    print_on_terminal = kwargs.get("print_on_terminal")
    del kwargs["print_on_terminal"] # avoid printing dictionary output
    messages = agentmake(
        content,
        system=TOOL_SYSTEM,
        schema=TOOL_SCHEMA,
        print_on_terminal=False,
        **kwargs,
    )
    revised_writing = json.loads(messages[-1]["content"])["revised_writing"]
    if print_on_terminal:
        print(f"```revised_writing\n{revised_writing}\n```")
    return revised_writing

CONTENT_PLUGIN = convert_relative_datetime