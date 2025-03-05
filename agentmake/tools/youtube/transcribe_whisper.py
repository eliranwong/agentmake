from agentmake.utils.manage_package import installPipPackage
from agentmake import PACKAGE_PATH, getCurrentDateTime
import shutil, re, os

# install binary ffmpeg and python package yt-dlp to work with this plugin
if not shutil.which("yt-dlp"):
    installPipPackage("yt-dlp")
if not shutil.which("ffmpeg"):
    raise ValueError("Tool 'ffmpeg' is not found on your system! Read https://github.com/eliranwong/letmedoit/wiki/Install-ffmpeg for installation.")

# update once a date
currentDate = re.sub("_.*?$", "", getCurrentDateTime())
ytdlp_updated = os.path.join(PACKAGE_PATH, "temp", f"yt_dlp_updated_on_{currentDate}")
if not os.path.isfile(ytdlp_updated):
    installPipPackage("--upgrade yt-dlp")
    open(ytdlp_updated, "a", encoding="utf-8").close()

from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["openai-whisper"]
try:
    import whisper
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import whisper

TOOL_SYSTEM = f"""You are an good at identifying a YouTube url from user request. Return an empty string '' for parameter `url` if no YouTube url is given."""

TOOL_SCHEMA = {
    "name": "transcribe_youtube_audio_whisper",
    "description": "Transcribe YouTube video into text with Whisper model",
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

def transcribe_youtube_audio_whisper(url: str="", **kwargs):

    from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH, agentmake, showErrors, extractText, getCurrentDateTime, writeTextFile
    from agentmake.utils.online import is_valid_url
    from pathlib import Path
    import re, os, shutil

    def is_youtube_url(url_string):
        pattern = r'(?:https?:\/\/)?(?:www\.)?youtu(?:\.be|be\.com)\/(?:watch\?v=|embed\/|v\/)?([a-zA-Z0-9_-]+)'
        match = re.match(pattern, url_string)
        return match is not None

    if is_youtube_url(url):
        # download the video and convert into mp3        
        temp_youtube_mp3_file = os.path.join(PACKAGE_PATH, "temp", "youtube.mp3")
        if os.path.isfile(temp_youtube_mp3_file):
            os.remove(temp_youtube_mp3_file)
        downloadCommand = f'''yt-dlp -x --audio-format mp3 --output {temp_youtube_mp3_file}'''
        os.system(f"{downloadCommand} {url}")
        if shutil.which("pkill"):
            os.system("pkill yt-dlp")
        # transcribe the audio file
        transcription = agentmake(
            temp_youtube_mp3_file,
            tool=os.path.join("audio", "transcribe_whisper"),
            **kwargs,
        )[-1].get("content", "")
        print("```transcription")
        print(transcription)
        print("```")
        # save a copy
        transcriptions_dir = os.path.join(AGENTMAKE_USER_DIR, "transcriptions")
        Path(transcriptions_dir).mkdir(parents=True, exist_ok=True)
        writeTextFile(os.path.join(transcriptions_dir, getCurrentDateTime()), transcription)
        return ""
    elif is_valid_url(url):
        try:
            print(extractText(url))
            return ""
        except Exception as e:
            showErrors(e)
            return None
    else:
        print("Invalid link given!")
        return None

TOOL_FUNCTION = transcribe_youtube_audio_whisper