TOOL_SCHEMA = {
    "name": "youtube_audio_qna_azure",
    "description": "Search for information in a YouTube video content",
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "Youtube url given by user",
            },
        },
        "required": ["url"],
    },
}

def youtube_audio_qna_azure(url: str, **kwargs):

    from agentmake import agentmake
    import os

    transcription = agentmake(
        url,
        tool=os.path.join("youtube", "transcribe_azure"),
        **kwargs,
    )[-1].get("content", "")
    return f"## Transcription of YouTube video: {url}\n\n{transcription}"

TOOL_FUNCTION = youtube_audio_qna_azure