from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
from agentmake.utils.handle_text import readTextFile
import os

system_path_1 = os.path.join(AGENTMAKE_USER_DIR, "systems", "improve_prompt.md")
system_path_2 = os.path.join(PACKAGE_PATH, "systems", "improve_prompt.md")

TOOL_SYSTEM = readTextFile(system_path_1 if os.path.isfile(system_path_1) else system_path_2)

TOOL_SCHEMA = {
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

def improve_prompt(improved_prompt: str, **kwargs):
    print(f"```improved_version\n{improved_prompt}\n```")
    return ""

TOOL_FUNCTION = improve_prompt