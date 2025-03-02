from agentmake import PACKAGE_PATH, USER_OS, getOpenCommand
import shutil, os, subprocess
import edge_tts, asyncio
from typing import Optional

def list_edgetts_voices():
    async def getVoices():
        voices = await edge_tts.list_voices()
        return voices
    voices = asyncio.run(getVoices())
    voices = [voice["ShortName"] for voice in voices if "ShortName" in voice]
    return voices

def generate_edge_tts_audio(content: str, edgettsVoice: Optional[str] = None, edgettsRate: Optional[float] = None, audioFile: Optional[str] = None) -> str:
    if not edgettsRate:
        edgettsRate = float(os.getenv("TTS_EDGE_RATE")) if os.getenv("TTS_EDGE_RATE") else 1.0
    if not edgettsVoice:
        edgettsVoice = os.getenv("TTS_EDGE_VOICE") if os.getenv("TTS_EDGE_VOICE") else "en-GB-SoniaNeural"
    if not audioFile:
        audioFile = os.path.join(PACKAGE_PATH, "temp", "edge.wav")
    async def saveEdgeAudio() -> None:
        rate = (edgettsRate - 1.0) * 100
        rate = int(round(rate, 0))
        communicate = edge_tts.Communicate(content, edgettsVoice, rate=f"{'+' if rate >= 0 else ''}{rate}%")
        await communicate.save(audioFile)
    asyncio.run(saveEdgeAudio())
    #playAudioFile(audioFile)
    return audioFile

def playAudioFile(audioFile):
    # Play audio file
    # This function is a wrapper around the play command
    if shutil.which("termux-media-player"):
        os.system(f'''termux-media-player play "{audioFile}"''')
    elif os.getenv("TTS_USE_VLC") and os.getenv("TTS_USE_VLC").lower() == "true":
        playAudioFile_vlc(audioFile)
    elif os.getenv("TTS_USE_MPV") and os.getenv("TTS_USE_MPV").lower() == "true" and shutil.which("mpv"):
        audioFile = os.path.abspath(audioFile).replace('"', '\\"')
        os.system(f'''mpv --no-loop-file --really-quiet "{audioFile}"''')
    else:
        try:
            try:
                import sounddevice, soundfile
            except:
                from agentmake.utils.manage_package import installPipPackage
                installPipPackage("sounddevice")
                installPipPackage("soundfile")
                import sounddevice, soundfile
            sounddevice.play(*soundfile.read(audioFile)) 
            sounddevice.wait()
        except:
            command = f"{getOpenCommand()} {audioFile}"
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

def getHideOutputSuffix():
    return f" > {'nul' if USER_OS == 'Windows' else '/dev/null'} 2>&1"

def playAudioFile_vlc(audioFile):
    audioFile = os.path.abspath(audioFile).replace('"', '\\"')

    macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
    windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
    
    command = ""
    vlcSpeed = float(os.getenv("TTS_VLC_RATE")) if os.getenv("TTS_VLC_RATE") else 1.0

    # vlc on macOS
    if os.path.isfile(macVlc):
        command = f'''{macVlc} --intf rc --play-and-exit --rate {vlcSpeed} "{audioFile}"{getHideOutputSuffix()}'''
    # vlc on windows
    elif os.path.isfile(windowsVlc):
        command = f'''"{windowsVlc}" --intf dummy --play-and-exit --rate {vlcSpeed} "{audioFile}"'''
    # vlc on other platforms
    elif shutil.which("cvlc"):
        command = f'''cvlc --no-loop --play-and-exit --rate {vlcSpeed} "{audioFile}"{getHideOutputSuffix()}'''
    # use .communicate() to wait for the playback to be completed as .wait() or checking pid existence does not work
    if command:
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
