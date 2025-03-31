"""
Read content alound using Android TTS utilities
"""

def run_termux_tts(content: str, **kwargs):
    import os
    TTS_TERMUX_LANGUAGE = os.getenv("TTS_TERMUX_LANGUAGE") if os.getenv("TTS_TERMUX_LANGUAGE") else "en-US"
    TTS_TERMUX_RATE = float(os.getenv("TTS_TERMUX_LANGUAGE")) if os.getenv("TTS_TERMUX_LANGUAGE") else 1.0
    content = content.replace('"', '\\"')
    os.system(f'''termux-tts-speak -l {TTS_TERMUX_LANGUAGE} -r {TTS_TERMUX_RATE} "{content}"''')
    return content

CONTENT_PLUGIN = run_termux_tts