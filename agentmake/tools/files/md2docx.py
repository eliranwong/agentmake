from agentmake.utils.manage_package import installPipPackage
import shutil
REQUIREMENTS = ["pypandoc"]
try:
    import pypandoc
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import pypandoc
if not shutil.which("pandoc"):
    raise ValueError("Tool 'pandoc' is not found on your system! Read https://pandoc.org/installing.html for installation.")

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
            "output_file": {
                "type": "string",
                "description": "Output file path. Return an empty string '' if not given.",
            },
        },
        "required": ["markdown_file"],
    },
}

def md2docx(markdown_file: str="", output_file: str="", **kwargs):
    if not markdown_file:
        return None
    if output_file and not output_file.endswith(".docx"):
        output_file = output_file + ".docx"
    import pypandoc, os
    from agentmake import getOpenCommand
    docx_file = output_file if output_file else markdown_file.replace(".md", ".docx")
    pypandoc.convert_file(markdown_file, 'docx', outputfile=docx_file)
    print(f"Converted {markdown_file} to {docx_file}")
    os.system(f"{getOpenCommand()} {docx_file}")
    return ""

TOOL_FUNCTION = md2docx

