from agentmake.utils.system import get_linux_distro
from agentmake import USER_OS

# Template: edit {COMMAND}, {PURPOSE} and {URL}

TOOL_PLATFORM = "Linux (" + get_linux_distro().get("name", "") + ")" if USER_OS == "Linux" else USER_OS
TOOL_PLATFORM = TOOL_PLATFORM.replace("()", "")

TOOL_SYSTEM = f"""You are a senior Python engineer and an `{COMMAND}` expert. Your expertise is in generating Python code that executes `{COMMAND}` commands on {TOOL_PLATFORM} to {PURPOSE}.
The generated code should conclude with a `print` statement that describes the work performed."""

TOOL_SCHEMA = {
    "name": "cli_{COMMAND}",
    "description": "{PURPOSE} that can be handled using the `{COMMAND}` command.",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate Python code that executes an `{COMMAND}` command to {PURPOSE}, based on the specifications in my request",
            },
            "title": {
                "type": "string",
                "description": "Title for the task",
            },
        },
        "required": ["code", "title"],
    },
}

def cli_{COMMAND}(code: str, title: str, **kwargs):
    from agentmake import DEVELOPER_MODE
    from agentmake.utils.handle_python_code import fineTunePythonCode
    import traceback, shutil

    if not shutil.which("{COMMAND}"):
        print("Required command `{COMMAND}` not found! Visit {URL} for installation.")
        return ""

    print(f"# Task: {title}")
    print()

    refined_python_code = fineTunePythonCode(code)
    print("Running python code ...")
    if DEVELOPER_MODE:
        print(f"```python\n{refined_python_code}\n```\n\n")

    print("```output")
    try:
        exec(refined_python_code)
        print("```")
    except Exception as e:
        print(f"An error occured: {e}\n```\n\n")
        print(f"```buggy_python_code\n{refined_python_code}\n```\n\n")
        print(f"```traceback\n{traceback.format_exc()}\n```")

    return ""

TOOL_FUNCTION = cli_{COMMAND}