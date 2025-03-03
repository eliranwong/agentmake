from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["tavily-python"]
try:
    from tavily import TavilyClient
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    from tavily import TavilyClient

def search_tavily(messages: list, **kwargs):
    from tavily import TavilyClient

    import os

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY").split(",") if os.getenv("TAVILY_API_KEY") and "," in os.getenv("TAVILY_API_KEY") else [os.getenv("TAVILY_API_KEY")]

    if not TAVILY_API_KEY[0]:
        return None
    query = messages[-1].get("content", "")
    if not query:
        return None
    
    if len(TAVILY_API_KEY) > 1:
        first_item = TAVILY_API_KEY.pop(0)
        TAVILY_API_KEY.append(first_item)

    print(TavilyClient(api_key=TAVILY_API_KEY[0]).get_search_context(query=query))
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Search for online information via Tavily."""

TOOL_FUNCTION = search_tavily