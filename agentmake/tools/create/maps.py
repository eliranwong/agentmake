from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["folium", "geopy"]
try:
    import folium
    from geopy.geocoders import Nominatim
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import folium
    from geopy.geocoders import Nominatim


def create_map(code: str, **kwargs):
    import re, os, shutil
    from agentmake import getOpenCommand
    from agentmake.utils.handle_python_code import fineTunePythonCode

    refined_python_code = fineTunePythonCode(code)
    exec(refined_python_code)

    htmlPattern = r"""\.save\(["']([^\(\)]+\.html)["']\)"""
    match = re.search(htmlPattern, code)
    if match:
        htmlFile = match.group(1)
        openCmd = getOpenCommand()
        if shutil.which(openCmd):
            os.system(f"{openCmd} {htmlFile}")
        print(f"Saved: {htmlFile}")
    return ""

TOOL_SCHEMA = {
    "name": "create_map",
    "description": f'''Create maps''',
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Generate python code that integrates packages 'folium' and 'geopy', when needed, to resolve my request. Created maps are saved in *.html file. Tell me the file path at the end.",
            },
        },
        "required": ["code"],
    },
}

TOOL_FUNCTION = create_map