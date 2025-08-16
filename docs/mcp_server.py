"""
! pip install --upgrade fastmcp agentmake

This file shows a simple of building a MCP server with AgentMake AI tools.
There are only 3 tools inluded in this example, but you can customise to add more.

# Integration wiht Gemini CLI

Edit `.gemini/settings.json` to include the entry `mcpServers`:

{
  ...
  "mcpServers": {
    "youtube-utilities-server": {
      "httpUrl": "http://127.0.0.1:8080/mcp/"
    }
  }
}

"""

from fastmcp import FastMCP
from agentmake import agentmake
import logging, os


logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP(name="YouTube Utilities")

def getResponse(messages:list) -> str:
    return messages[-1].get("content") if messages and "content" in messages[-1] else "Error!"

@mcp.tool
def youtube_transcribe(request:str) -> str:
    """Transcribe YouTube video into text with Google service

Args [required]:
    url: Youtube url given by user
"""
    logger.info(f"[Request] {request}")
    messages = agentmake(request, tool="youtube/transcribe_google")
    return getResponse(messages)

@mcp.tool
def youtube_download_video(request:str) -> str:
    """Download Youtube audio into mp4 video file

Args [required]:
    url: Youtube url given by user

Args [optional]:
    location: Output folder where downloaded file is to be saved
"""
    logger.info(f"[Request] {request}")
    messages = agentmake(request, tool="youtube/download_video")
    return getResponse(messages)

@mcp.tool
def youtube_download_audio(request:str) -> str:
    """Download Youtube audio into mp3 audio file

Args [required]:
    url: Youtube url given by user

Args [optional]:
    location: Output folder where downloaded file is to be saved
"""
    logger.info(f"[Request] {request}")
    messages = agentmake(request, tool="youtube/download_audio")
    return getResponse(messages)

if __name__ == "__main__":
    logger.info(f" AgentMake MCP server started on port {os.getenv('PORT', 8080)}")
    mcp.run(transport="http", port=os.getenv("PORT", 8080))
    # run with CLI
    # astmcp run server.py --transport "http" --port "8080"
