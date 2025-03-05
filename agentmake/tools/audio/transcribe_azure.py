def transcribe_audio_azure(audio_filepath: str, **kwargs):
    from agentmake import AzureAI, showErrors, writeTextFile, getCurrentDateTime, AGENTMAKE_USER_DIR
    from pathlib import Path
    import os
    def check_file_format(file_path):
        # List of allowed file extensions
        allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
        # Getting the file extension
        _, file_extension = os.path.splitext(file_path)
        # Checking if the file extension is in the list of allowed extensions
        return True if file_extension.lower() in allowed_extensions else False

    if audio_filepath and os.path.isfile(audio_filepath):
        if not check_file_format(audio_filepath):
            print("This feature supports the following input file types only: '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'!")
            return ""
        elif os.path.getsize(audio_filepath) / (1024*1024) > 25:
            print("Audio files are currently limited to 25 MB!")
            return ""
        try:
            with open(audio_filepath, "rb") as audio_filepath:
                transcription = AzureAI.getWhisperClient().audio.transcriptions.create(
                    model=AzureAI.DEFAULT_WHISPER_MODEL, 
                    file=audio_filepath, 
                    response_format="text"
                )
            print("```transcription")
            print(transcription)
            print("```")
            # save a copy
            transcriptions_dir = os.path.join(AGENTMAKE_USER_DIR, "transcriptions")
            Path(transcriptions_dir).mkdir(parents=True, exist_ok=True)
            writeTextFile(os.path.join(transcriptions_dir, getCurrentDateTime()), transcription)
        except Exception as e:
            showErrors(e)
        return ""

    return "[INVALID]"

TOOL_SCHEMA = {
    "name": "transcribe_audio_azure",
    "description": '''Transcribe audio into text with OpenAI''',
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

TOOL_FUNCTION = transcribe_audio_azure