def transcribe_audio_groq(audio_filepath: str, **kwargs):
    from agentmake import AGENTMAKE_USER_DIR, showErrors, writeTextFile, getCurrentDateTime, GroqAI
    from pathlib import Path
    import os, shutil, subprocess
    def check_file_format(file_path):
        # List of allowed file extensions
        allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
        # Getting the file extension
        _, file_extension = os.path.splitext(file_path)
        # Checking if the file extension is in the list of allowed extensions
        return True if file_extension.lower() in allowed_extensions else False

    if audio_filepath and os.path.isfile(audio_filepath):
        if shutil.which("ffmpeg"):
            temp_audio_filepath = os.path.join(AGENTMAKE_USER_DIR, "temp", os.path.basename(audio_filepath))
            if os.path.isfile(temp_audio_filepath):
                os.remove(temp_audio_filepath)
            cli = f'''ffmpeg -i "{audio_filepath}" -ar 16000 -ac 1 -map 0:a: "{temp_audio_filepath}"'''
            run_cli = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = run_cli.communicate()
            if not stderr:
                audio_filepath = temp_audio_filepath
        if not check_file_format(audio_filepath):
            print("This feature supports the following input file types only: '.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'!")
            return ""
        elif os.path.getsize(audio_filepath) / (1024*1024) > 25:
            print("Audio files are currently limited to 25 MB!")
            return ""
        try:
            # read https://console.groq.com/docs/speech-text
            with open(audio_filepath, "rb") as file:
                transcription = GroqAI.getClient().audio.transcriptions.create(
                    file=(audio_filepath, file.read()),
                    model="whisper-large-v3",
                    #prompt="Specify context or spelling",  # Optional
                    #response_format="json",  # Optional
                    #language="en",  # Optional
                    temperature=0.0  # Optional
                ).text
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
    "name": "transcribe_audio_groq",
    "description": '''Transcribe audio into text with Groq''',
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

TOOL_FUNCTION = transcribe_audio_groq
