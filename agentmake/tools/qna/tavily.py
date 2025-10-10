from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["tavily-python"]
try:
    from tavily import TavilyClient
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    from tavily import TavilyClient

def ask_tavily(messages: list, **kwargs):
    from tavily import TavilyClient

    import os

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY").split(",") if os.getenv("TAVILY_API_KEY") else [""]

    if not TAVILY_API_KEY[0]:
        return None
    query = messages[-1].get("content", "")
    if not query:
        return None
    
    if len(TAVILY_API_KEY) > 1:
        first_item = TAVILY_API_KEY.pop(0)
        TAVILY_API_KEY.append(first_item)

    print(TavilyClient(api_key=TAVILY_API_KEY[0]).qna_search(query=query))
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Ask Tavily to answer a question."""

TOOL_FUNCTION = ask_tavily