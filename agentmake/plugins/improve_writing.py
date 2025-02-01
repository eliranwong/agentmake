from agentmake import generate, DEFAULT_AI_BACKEND
from typing import Optional, Union, List
import os, json

WRITING_STYLE = os.getenv('WRITING_STYLE') if os.getenv('WRITING_STYLE') else 'standard English'

TOOL_SYSTEM = f"""# Role
You are an excellent writer.

# Job description
Your job is to improve my writing sytle only, without extra comments or explantions.

# Expertise
Your expertise lies in proofreading and improving my writing.

# Instruction
You improve the writing in the user's input, according to {WRITING_STYLE}.
Remember, do NOT give me extra comments explanations.  I want only the 'improved_writing'"""

TOOL_SCHEMA = {
    "name": "improve_writing",
    "description": f"Improve user writing, according to {WRITING_STYLE}",
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

def improve_writing(
    content,
    **kwargs,
):
    messages = generate(
        content,
        system=TOOL_SYSTEM,
        schema=TOOL_SCHEMA,
        **kwargs,
    )
    improved_writing = json.loads(messages[-1]["content"])["improved_writing"]
    return improved_writing

CONTENT_PLUGIN = improve_writing