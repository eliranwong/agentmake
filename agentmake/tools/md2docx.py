from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["pypandoc"]
try:
    import pypandoc
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import pypandoc


TOOL_SCHEMA = {
    "name": "md2docx",
    "description": "Convert Markdown format into Docx.",
    "parameters": {
        "type": "object",
        "properties": {
            "markdown_file": {
                "type": "string",
                "description": "Either a file path. Return an empty string '' if not given.",
            },
        },
        "required": ["markdown_file"],
    },
}

def md2docx(markdown_file: str="", **kwargs):
    import pypandoc, os
    from agentmake import getOpenCommand
    docx_file = markdown_file.replace(".md", ".docx")
    pypandoc.convert_file(markdown_file, 'docx', outputfile=docx_file)
    print(f"Converted {markdown_file} to {docx_file}")
    os.system(f"{getOpenCommand()} {docx_file}")
    return ""

TOOL_FUNCTION = md2docx

