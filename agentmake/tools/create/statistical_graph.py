from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["matplotlib"]
try:
    import matplotlib.pyplot as plt
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import matplotlib.pyplot as plt


def create_statistical_graphics(code: str, **kwargs):
    import os, re, shutil
    from agentmake.utils.handle_python_code import fineTunePythonCode
    from agentmake import getOpenCommand

    refined_python_code = fineTunePythonCode(code)
    exec(refined_python_code)

    pngPattern = r"""\.savefig\(["']([^\(\)]+\.png)["']\)"""
    match = re.search(pngPattern, code)
    if match:
        openCmd = getOpenCommand()
        pngFile = match.group(1)
        if shutil.which(openCmd):
            os.system(f"{openCmd} {pngFile}")
        print(f"Saved: {pngFile}")
    return ""

TOOL_SCHEMA = {
    "name": "create_statistical_graphics",
    "description": f'''Create statistical plots, such as pie charts or bar charts, to visualize statistical data''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates package matplotlib to resolve my input. Save the result in png format. Tell me the image path at the end.",
            },
        },
        "required": ["code"],
    },
}

TOOL_FUNCTION = create_statistical_graphics
