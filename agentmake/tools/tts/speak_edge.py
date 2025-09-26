TOOL_SYSTEM = ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Read text aloud with Edge TTS utility."""

def speak_edge_tts(messages, **kwargs):
    from agentmake.utils.media import generate_edge_tts_audio, playAudioFile
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ResourceWarning)
        content = messages[-1].get("content", "")
        audioFile = generate_edge_tts_audio(content)
        print(f"Audio file generated: {audioFile}")
        playAudioFile(audioFile)
    return ""

TOOL_FUNCTION = speak_edge_tts