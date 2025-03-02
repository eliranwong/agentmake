from agentmake import USER_OS, getOpenCommand
import shutil, os, subprocess

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

def playAudioFile_vlc(audioFile):
    def getHideOutputSuffix():
        return f" > {'nul' if USER_OS == 'Windows' else '/dev/null'} 2>&1"

    audioFile = os.path.abspath(audioFile).replace('"', '\\"')

    macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
    windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
    
    command = ""
    vlcSpeed = float(os.getenv("TTS_VLC_SPEED")) if os.getenv("TTS_VLC_SPEED") else 1.0

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
