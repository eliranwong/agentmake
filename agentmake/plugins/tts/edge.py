from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["edge-tts"]
try:
    import edge_tts
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import edge_tts

def run_edge_tts(content: str, **kwargs):
    import os, edge_tts, asyncio
    from agentmake import PACKAGE_PATH

    edgettsRate = float(os.getenv("TTS_EDGE_RATE")) if os.getenv("TTS_EDGE_RATE") else 1.0
    edgettsVoice = os.getenv("TTS_EDGE_VOICE") if os.getenv("TTS_EDGE_VOICE") else "en-GB-SoniaNeural"

    audioFile = os.path.join(PACKAGE_PATH, "temp", "edge.wav")
    async def saveEdgeAudio() -> None:
        rate = (edgettsRate - 1.0) * 100
        rate = int(round(rate, 0))
        communicate = edge_tts.Communicate(content, edgettsVoice, rate=f"{'+' if rate >= 0 else ''}{rate}%")
        await communicate.save(audioFile)
    asyncio.run(saveEdgeAudio())

CONTENT_PLUGIN = run_edge_tts