"""
Read content alound in default text-to-speech voice
"""

from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["edge-tts"]
try:
    import edge_tts
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import edge_tts

def run_edge_tts(content: str, **kwargs):
    from agentmake.utils.media import generate_edge_tts_audio, playAudioFile
    audioFile = generate_edge_tts_audio(content)
    playAudioFile(audioFile)
    return content

CONTENT_PLUGIN = run_edge_tts