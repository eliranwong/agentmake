"""
Read content alound using Piper TTS utilities
"""

from agentmake.utils.manage_package import installPipPackage
import shutil
if not shutil.which("piper"):
    installPipPackage("piper-tts")

def run_piper_tts(content: str, **kwargs):
    import os, shutil, pydoc
    from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH
    from agentmake.utils.media import playAudioFile, getHideOutputSuffix

    vlcSpeed = float(os.getenv("TTS_VLC_RATE")) if os.getenv("TTS_VLC_RATE") else 1.0
    TTS_PIPER_OPTIONS = os.getenv("TTS_PIPER_OPTIONS") if os.getenv("TTS_PIPER_OPTIONS") else ""
    TTS_PIPER_VOICE = os.getenv("TTS_PIPER_VOICE") if os.getenv("TTS_PIPER_VOICE") else "en_GB-aru-medium"

    audioFile = os.path.join(PACKAGE_PATH, "temp", "piper.wav")
    model_dir = os.path.join(AGENTMAKE_USER_DIR, "models", "piper")
    model_path = f"""{os.path.join(model_dir, TTS_PIPER_VOICE)}.onnx"""
    model_config_path = f"""{model_path}.json"""
    piper_additional_options = f" {TTS_PIPER_OPTIONS.strip()}" if TTS_PIPER_OPTIONS.strip() else ""
    if os.path.isfile(model_path):
        if shutil.which("cvlc"):
            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | cvlc --no-loop --play-and-exit --rate {vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
        elif shutil.which("aplay"):
            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
        else:
            cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
    else:
        print("[Downloading voice ...] ")
        if shutil.which("cvlc"):
            cmd = f'''"{shutil.which("piper")}" --model {TTS_PIPER_VOICE} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | cvlc --no-loop --play-and-exit --rate {vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050{piper_additional_options} -{getHideOutputSuffix()}'''
        elif shutil.which("aplay"):
            cmd = f'''"{shutil.which("piper")}" --model {TTS_PIPER_VOICE} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | aplay -r 22050 -f S16_LE -t raw{piper_additional_options} -{getHideOutputSuffix()}'''
        else:
            cmd = f'''"{shutil.which("piper")}" --model {TTS_PIPER_VOICE} --download-dir "{model_dir}" --data-dir "{model_dir}" --output_file "{audioFile}"{piper_additional_options}{getHideOutputSuffix()}'''
    pydoc.pipepager(content, cmd=cmd)
    if not shutil.which("cvlc") and not shutil.which("aplay"):
        playAudioFile(audioFile)
    return content

CONTENT_PLUGIN = run_piper_tts