from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
from agentmake.utils.handle_text import readTextFile
import os

system_path_1 = os.path.join(AGENTMAKE_USER_DIR, "biblemate", "summarize_task_instruction.md")
system_path_2 = os.path.join(PACKAGE_PATH, "biblemate", "summarize_task_instruction.md")

TOOL_SYSTEM = readTextFile(system_path_1 if os.path.isfile(system_path_1) else system_path_2)

TOOL_SCHEMA = {
    "name": "summarize_task_instruction",
    "description": "Identify the task goal regarding Bible study and transform it into a direct instruction in one sentence.",
    "parameters": {
        "type": "object",
        "properties": {
            "one_sentence_instruction": {
                "type": "string",
                "description": "Identify the task goal regarding Bible study and transform it into a direct instruction in one sentence.",
            },
        },
        "required": ["one_sentence_instruction"],
    },
}

def summarize_task_instruction(one_sentence_instruction: str, **kwargs):
    print(f"```instruction\n{one_sentence_instruction}\n```")
    return ""

TOOL_FUNCTION = summarize_task_instruction