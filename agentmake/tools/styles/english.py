from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
from agentmake.utils.handle_text import readTextFile
import os

system_path_1 = os.path.join(AGENTMAKE_USER_DIR, "systems", "styles", "english.md")
system_path_2 = os.path.join(PACKAGE_PATH, "systems", "styles", "english.md")

TOOL_SYSTEM = readTextFile(system_path_1 if os.path.isfile(system_path_1) else system_path_2)

TOOL_SCHEMA = {
    "name": "improve_english",
    "description": "Refine and enhance written content to align with standard English conventions.",
    "parameters": {
        "type": "object",
        "properties": {
            "improved_version": {
                "type": "string",
                "description": "Refine and enhance written content to align with standard English conventions.",
            },
        },
        "required": ["improved_version"],
    },
}

def improve_english(improved_version: str, **kwargs):
    print(f"```improved_version\n{improved_version}\n```")
    return ""

TOOL_FUNCTION = improve_english