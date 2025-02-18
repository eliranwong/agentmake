from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["pillow"]
try:
    from PIL import ImageGrab
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    from PIL import ImageGrab

def screenshot(filepath_or_filename: str, **kwargs):
    from PIL import ImageGrab

    filepath = filepath_or_filename.rstrip()
    if not filepath.endswith(".png"):
        filepath += ".png"
    # Capture the entire screen
    screenshot = ImageGrab.grab()
    # Save the screenshot
    screenshot.save(filepath)
    print(f"Screenshot saved: {filepath}")
    return ""

TOOL_SCHEMA = {
    "name": "screenshot",
    "description": "Take a screenshot and save it in a file",
    "parameters": {
        "type": "object",
        "properties": {
            "filepath_or_filename": {
                "type": "string",
                "description": '''The file path or name for saving the screenshot; return "screenshot.png" if it is not given.''',
            },
        },
        "required": ["filepath_or_filename"],
    },
}

TOOL_FUNCTION = screenshot