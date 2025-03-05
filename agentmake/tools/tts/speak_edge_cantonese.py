TOOL_SYSTEM = ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Read text aloud in Cantonese with Edge TTS utility."""

def speak_cantonese_termux_tts(messages, **kwargs):
    from agentmake.utils.media import generate_edge_tts_audio, playAudioFile
    content = messages[-1].get("content", "")
    audioFile = generate_edge_tts_audio(content, edgettsVoice="zh-HK-HiuGaaiNeural")
    print(f"Audio file generated: {audioFile}")
    playAudioFile(audioFile)
    return ""

TOOL_FUNCTION = speak_cantonese_termux_tts