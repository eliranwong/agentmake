def take_photo(jpeg_file_path, **kwargs):
    import subprocess
    if not jpeg_file_path:
        jpeg_file_path = "photo.jpg"
    cli = f'''termux-camera-photo "{jpeg_file_path}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Saved :{jpeg_file_path}")
    return ""

TOOL_SCHEMA = {
    "name": "take_photo",
    "description": f'''Take a photo with the main camera''',
    "parameters": {
        "type": "object",
        "properties": {
            "jpeg_file_path": {
                "type": "string",
                "description": "The file path at which the image is saved. Return 'photo.jpg' if it is not specified in the user input.",
            },
        },
        "required": ["jpeg_file_path"],
    },
}

TOOL_FUNCTION = take_photo