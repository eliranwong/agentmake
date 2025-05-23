"""
Automate tool selection
"""

from agentmake import agentmake

agentmake("Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work", agent="auto_tool_selection")

agentmake("Download mp3 from a youtube video https://www.youtube.com/watch?v=X6Mtpk4jeVA", agent="auto_tool_selection")

# Equivalent CLI command:
# > ai -a auto_tool_selection "Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work"