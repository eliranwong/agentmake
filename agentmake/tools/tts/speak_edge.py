TOOL_SYSTEM = ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Read text aloud with Edge TTS utility."""

def speak_termux_tts(messages, **kwargs):
    from agentmake.utils.media import generate_edge_tts_audio, playAudioFile
    content = messages[-1].get("content", "")
    audioFile = generate_edge_tts_audio(content)
    print(f"Audio file generated: {audioFile}")
    playAudioFile(audioFile)
    return ""

TOOL_FUNCTION = speak_termux_tts