TOOL_SYSTEM = "You are an online search expert. You expertise lies in identifing keywords for online searches, in order to resolve user request."

TOOL_SCHEMA = {
    "name": "ollama_web_search",
    "description": "Search the web for real-time information or latest updates when AI lacks information",
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

def ollama_web_search(keywords: str, **kwargs):

    from agentmake import OllamacloudAI
    import os
    DEFAULT_MAXIMUM_ONLINE_SEARCHES = int(os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES")) if os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES") else 5

    output = OllamacloudAI.getClient().web_search(query=keywords, max_results=DEFAULT_MAXIMUM_ONLINE_SEARCHES)

    results = []
    for index, item in enumerate(output.results):
        results.append(f"""# Search Result {index+1}

## Title

{item.title}

## URL

{item.url}

## Content

{item.content}""")

    return "\n\n---\n\n".join(results)

TOOL_FUNCTION = ollama_web_search