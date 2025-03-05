from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
from agentmake.utils.handle_text import readTextFile
import os

system_path_1 = os.path.join(AGENTMAKE_USER_DIR, "systems", "styles", "british_english.md")
system_path_2 = os.path.join(PACKAGE_PATH, "systems", "styles", "british_english.md")

TOOL_SYSTEM = readTextFile(system_path_1 if os.path.isfile(system_path_1) else system_path_2)

TOOL_SCHEMA = {
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

def improve_british_english(improved_version: str, **kwargs):
    print(f"```improved_version\n{improved_version}\n```")
    return ""

TOOL_FUNCTION = improve_british_english