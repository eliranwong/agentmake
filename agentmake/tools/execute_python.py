# a dummy tool to force fallback to regular chat completion

TOOL_SCHEMA = {
    "name": "execute_python_code",
    "description": "Execute a single block of python code.",
    "parameters": {
        "type": "object",
        "properties": {
            "python_code": {
                "type": "string",
                "description": "The python code to be executed.",
            },
        },
        "required": ["python_code"],
    },
}

def execute_python(python_code: str, **kwargs):
    from agentmake import DEVELOPER_MODE
    from agentmake.utils.handle_python_code import fineTunePythonCode
    import traceback

    refined_python_code = fineTunePythonCode(python_code)
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

TOOL_FUNCTION = execute_python