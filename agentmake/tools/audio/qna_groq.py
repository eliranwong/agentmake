TOOL_SCHEMA = {
    "name": "audio_qna_groq",
    "description": '''Search for information in audio content''',
    "parameters": {
        "type": "object",
        "properties": {
            "audio_filepath": {
                "type": "string",
                "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
            },
        },
        "required": ["audio_filepath"],
    },
}

def audio_qna_groq(audio_filepath: str, **kwargs):
    from agentmake import agentmake
    import os
    transcription = agentmake(
        audio_filepath,
        tool=os.path.join("audio", "transcribe_groq"),
        **kwargs,
    )[-1].get("content", "")
    return f"## Transcription of audio file: {audio_filepath}\n\n{transcription}"

TOOL_FUNCTION = audio_qna_groq