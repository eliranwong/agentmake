from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["googlesearch-python"]
try:
    import googlesearch
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import googlesearch

import os, json

TOOL_SYSTEM = "You expertise is to identify keywords for online searches, in order to resolve user request."

TOOL_SCHEMA = {
    "name": "search_google",
    "description": "Search Google for real-time information or latest updates when LLM lacks information",
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

def search_google(keywords):
    info = {}
    for index, item in enumerate(googlesearch.search(keywords, advanced=True, num_results=os.getenv("MAXIMUM_INTERNET_SEARCHES") if os.getenv("MAXIMUM_INTERNET_SEARCHES") else 5)):
        info[f"information {index}"] = {
            "title": item.title,
            "url": item.url,
            "description": item.description,
        }
    return json.dumps(info)

TOOL_FUNCTION = search_google