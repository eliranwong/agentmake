TOOL_SYSTEM = ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Speack with text-to-speech ability."""

def speak_termux_tts(messages, **kwargs):
    content = messages[-1].get("content", "")
    import os
    TTS_TERMUX_LANGUAGE = os.getenv("TTS_TERMUX_LANGUAGE") if os.getenv("TTS_TERMUX_LANGUAGE") else "en-US"
    TTS_TERMUX_RATE = float(os.getenv("TTS_TERMUX_LANGUAGE")) if os.getenv("TTS_TERMUX_LANGUAGE") else 1.0
    content = content.replace('"', '\\"')
    os.system(f'''termux-tts-speak -l {TTS_TERMUX_LANGUAGE} -r {TTS_TERMUX_RATE} "{content}"''')
    return ""

TOOL_FUNCTION = speak_termux_tts