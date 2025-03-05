from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["yfinance"]
try:
    import yfinance
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import yfinance

TOOL_SYSTEM = f"""# Your role
You are a finance expert who is skilled in writing python code in resolving user query.

# Your job
Search or analyze financial data.

# Your expertise
Your expertise lies in generating python code that integrates package 'yfinance' to resolve my request.
Integrate package matplotlib, in your code, to visualize data, if applicable.
Remember, you should format the requested finance information into a string that is easily readable by humans.
Use the 'print' function in the last line of your generated code to display the finance information."""

def search_finance(code: str, **kwargs):

    from agentmake.utils.handle_python_code import fineTunePythonCode

    refined_python_code = fineTunePythonCode(code)
    print("```output")
    exec(refined_python_code)
    print("```")
    return ""

TOOL_SCHEMA = {
    "name": "search_finance",
    "description": '''Search or analyze financial data. Use this function ONLY WHEN package yfinance is useful to resolve my request''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates package yfinance to resolve my request. Integrate package matplotlib to visualize data, if applicable.",
            },
        },
        "required": ["code"],
    },
}

TOOL_FUNCTION = search_finance