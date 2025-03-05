# a dummy tool to force fallback to regular chat completion

TOOL_SCHEMA = {
    "name": "correct_python_code",
    "description": "Fix Python code if both the buggy python code and the error are provided.",
    "parameters": {
        "type": "object",
        "properties": {
            "corrected_code": {
                "type": "string",
                "description": "Generate an improved version of python code that resolved the traceback error. Return the original code only if traceback shows an import error.",
            },
            "missing_module": {
                "type": "string",
                "description": """The module name identified in ModuleNotFoundError, if any. Return '' if there is no import error in the traceback.""",
            },
            "brief_issue_description": {
                "type": "string",
                "description": """Briefly explain the error""",
            },
        },
        "required": ["corrected_code", "missing_module", "brief_issue_description"],
    },
}

def correct_python(corrected_code: str, missing_module: str, brief_issue_description: str, **kwargs):
    from agentmake.utils.manage_package import installPipPackage
    from agentmake import DEVELOPER_MODE
    from agentmake.utils.handle_python_code import fineTunePythonCode
    import traceback

    if missing_module:
        print(f"# Issue: {brief_issue_description}\n")
        print(f"Trying to install the missing module: {missing_module} ...")
        installPipPackage(missing_module)

    refined_python_code = fineTunePythonCode(corrected_code)
    print("# Running improved python code ...")
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

TOOL_FUNCTION = correct_python