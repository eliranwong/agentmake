from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["openai-whisper"]
try:
    import whisper
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import whisper

import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL") if os.getenv("WHISPER_MODEL") else "base"

# Function method
def transcribe_audio_whisper(audio_filepath: str, language: str, **kwargs):
    import whisper
    
    from agentmake import AGENTMAKE_USER_DIR, getCurrentDateTime, writeTextFile
    from pathlib import Path
    import os, shutil
    def check_file_format(file_path):
        # List of allowed file extensions
        allowed_extensions = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
        # Getting the file extension
        _, file_extension = os.path.splitext(file_path)
        # Checking if the file extension is in the list of allowed extensions
        return True if file_extension.lower() in allowed_extensions else False

    if audio_filepath and os.path.isfile(audio_filepath):

        if not shutil.which("ffmpeg"):
            print("Install 'ffmpeg' first!")
            print("Read https://github.com/openai/whisper/tree/main#setup")
            return ""
        # https://github.com/openai/whisper/tree/main#python-usage
        # platform: llamacpp or ollama
        if language.lower() in ("english", "non-english"):
            model = whisper.load_model(WHISPER_MODEL if language.lower() == "english" else "large")
            result = model.transcribe(audio_filepath)
        else:
            # non-English
            model = whisper.load_model("large")

            # load audio and pad/trim it to fit 30 seconds
            audio = whisper.load_audio(audio_filepath)
            audio = whisper.pad_or_trim(audio)

            # make log-Mel spectrogram and move to the same device as the model
            mel = whisper.log_mel_spectrogram(audio).to(model.device)

            # detect the spoken language
            _, probs = model.detect_language(mel)
            print(f"Detected language: {max(probs, key=probs.get)}")

            # decode the audio
            options = whisper.DecodingOptions()
            result = whisper.decode(model, mel, options)

        transcription = result['text']
        print("```transcription")
        print(transcription)
        print("```")
        # save a copy
        transcriptions_dir = os.path.join(AGENTMAKE_USER_DIR, "transcriptions")
        Path(transcriptions_dir).mkdir(parents=True, exist_ok=True)
        writeTextFile(os.path.join(transcriptions_dir, getCurrentDateTime()), transcription)
        return ""

    return "[INVALID]"

TOOL_SCHEMA = {
    "name": "transcribe_audio_whisper",
    "description": '''Transcribe audio into text with Whisper''',
    "parameters": {
        "type": "object",
        "properties": {
            "audio_filepath": {
                "type": "string",
                "description": "Return the audio file path that I specified in my requests. Return an empty string '' if it is not specified.",
            },
            "language": {
                "type": "string",
                "description": "Audio language",
                "enum": ["English", "non-English"],
            },
        },
        "required": ["audio_filepath", "language"],
    },
}

TOOL_FUNCTION = transcribe_audio_whisper