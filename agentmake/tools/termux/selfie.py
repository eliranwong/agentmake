def selfie(jpeg_file_path: str, **kwargs):
    import subprocess
    if not jpeg_file_path:
        jpeg_file_path = "selfie.jpg"
    cli = f'''termux-camera-photo -c 1 "{jpeg_file_path}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Saved :{jpeg_file_path}")
    return ""

TOOL_SCHEMA = {
    "name": "selfie",
    "description": f'''Take a selfie with the main camera''',
    "parameters": {
        "type": "object",
        "properties": {
            "jpeg_file_path": {
                "type": "string",
                "description": "The file path at which the image is saved. Return 'selfie.jpg' when user does not specify a file name.",
            },
        },
        "required": ["jpeg_file_path"],
    },
}

TOOL_FUNCTION = selfie