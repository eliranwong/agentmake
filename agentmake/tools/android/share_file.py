def share_file(file_path: str, **kwargs):
    import subprocess
    file_path = file_path.replace('"', '\\"') # required
    cli = f'''termux-share -a send "{file_path}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "share_file",
    "description": f'''Share a file''',
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The file path of the file, being shared. Return an empty string '' if it is not given.",
            },
        },
        "required": ["file_path"],
    },
}

TOOL_FUNCTION = share_file