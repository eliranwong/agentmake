from agentmake.utils.system import get_linux_distro
from agentmake import USER_OS

TOOL_PLATFORM = "Linux (" + get_linux_distro().get("name", "") + ")" if USER_OS == "Linux" else USER_OS
TOOL_PLATFORM = TOOL_PLATFORM.replace("()", "")

TOOL_SYSTEM = f"""You are a senior python engineer. Your expertise lies in generating python code that works on {TOOL_PLATFORM}, to resolve my request.
Remember, you should format the answer or requested information, if any, into a string that is easily readable by humans.
Use the 'print' function in the last line of your generated code to display the requested information."""

TOOL_SCHEMA = {
    "name": "magic",
    "description": "Execute any computing tasks or gain access to device information",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate Python code that integrates any relevant packages to resolve my request",
            },
            "title": {
                "type": "string",
                "description": "Title for the task",
            },
            "risk": {
                "type": "string",
                "description": "Assess the risk level of damaging my device upon executing the task. e.g. file deletions or similar significant impacts are regarded as 'high' level.",
                "enum": ["high", "medium", "low"],
            },
        },
        "required": ["code", "title"],
    },
}

def magic(code: str, title: str, risk: str="high", **kwargs):
    from agentmake import DEVELOPER_MODE
    from agentmake.utils.handle_python_code import fineTunePythonCode
    import traceback

    print(f"# Task: {title}")
    #print(f"Risk: {risk}") # implement risk management later
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

TOOL_FUNCTION = magic