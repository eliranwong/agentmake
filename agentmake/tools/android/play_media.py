def play_media(media_file_path: str, **kwargs):
    import subprocess
    media_file_path = media_file_path.replace('"', '\\"') # required
    cli = f'''termux-media-player play "{media_file_path}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "play_media",
    "description": f'''Play a media file''',
    "parameters": {
        "type": "object",
        "properties": {
            "media_file_path": {
                "type": "string",
                "description": "The file path of the media file",
            },
        },
        "required": ["media_file_path"],
    },
}

TOOL_FUNCTION = play_media