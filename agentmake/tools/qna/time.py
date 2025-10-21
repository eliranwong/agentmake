from agentmake.utils.system import get_linux_distro
from agentmake import USER_OS

TOOL_PLATFORM = "Linux (" + get_linux_distro().get("name", "") + ")" if USER_OS == "Linux" else USER_OS
TOOL_PLATFORM = TOOL_PLATFORM.replace("()", "")

TOOL_SYSTEM = f"""You are a senior python engineer. Your expertise lies in generating python code that works on {TOOL_PLATFORM}, to answer my query about time.
Remember, you should format the answer or requested information into a string that is easily readable by humans.
The generated code should conclude with a `print` statement that presents the requested information or describes the work performed.
I want the generated code to be executed directly, so do NOT use `if __name__ == "__main__":` in your code."""

TOOL_SCHEMA = {
    "name": "answer_time_query",
    "description": "Answer a query about time; time-related query is required",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate Python code that integrates libraries `pendulum` or `pytz` to answer my query about time.",
            },
        },
        "required": ["code"],
    },
}

def answer_time_query(code: str, **kwargs):
    from agentmake import DEVELOPER_MODE
    from agentmake.utils.handle_python_code import fineTunePythonCode
    import traceback

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

TOOL_FUNCTION = answer_time_query
