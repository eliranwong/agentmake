from agentmake.utils.handle_python_code import fineTunePythonCode
from agentmake.utils.system import get_linux_distro
import platform

TOOL_PLATFORM = "Linux (" + get_linux_distro().get("name", "") + ")" if platform.system() == "Linux" else platform.system()
TOOL_PLATFORM = TOOL_PLATFORM.replace("()", "")

TOOL_SYSTEM = f"""You are a senior python engineer. Your expertise is to resolve my request, by generating python code that works on {TOOL_PLATFORM}."""

TOOL_SCHEMA = {
    "name": "task",
    "description": "Execute computing task or gain access to device information",
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
        "required": ["code", "title", "risk"],
    },
}

def task(code: str, title: str, risk: str):
    print(f"Running task: {title}")
    #print(f"Risk: {risk}") # implement risk management later
    print()

    refined_python_code = fineTunePythonCode(code)
    exec(refined_python_code, globals())

    print()
    print("Done!")
    return ""

TOOL_FUNCTION = task