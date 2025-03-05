from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["googlesearch-python"]
try:
    import googlesearch
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import googlesearch

TOOL_SYSTEM = "You are an online search expert. You expertise lies in identifing keywords for online searches, in order to resolve user request."

TOOL_SCHEMA = {
    "name": "search_google",
    "description": "Search Google for real-time information or latest updates when AI lacks information",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "Keywords for online searches",
            },
        },
        "required": ["keywords"],
    },
}

def search_google(keywords: str, **kwargs):

    import googlesearch
    import json, os
    DEFAULT_MAXIMUM_ONLINE_SEARCHES = int(os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES")) if os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES") else 5

    info = {}
    for index, item in enumerate(googlesearch.search(keywords, advanced=True, num_results=DEFAULT_MAXIMUM_ONLINE_SEARCHES)):
        info[f"information {index}"] = {
            "title": item.title,
            "url": item.url,
            "description": item.description,
        }
    return json.dumps(info)

TOOL_FUNCTION = search_google