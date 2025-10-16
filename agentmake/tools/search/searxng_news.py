SEARXNG_TABS = [
    "general",
    "translate",
    "web",
    "wikimedia",
    "images",
    "videos",
    "news",
    "map",
    "music",
    "lyrics",
    "radio",
    "it",
    "packages",
    "repos",
    "software_wikis",
    "science",
    "scientific_publications",
    "files",
    "apps",
    "social_media",
]

TOOL_SYSTEM = f"""You are an online news search expert.
You expertise lies in identifing keywords for online searches of news, in order to resolve user query."""

def search_searxng_news(keywords: str, category: str="news", **kwargs):

    from agentmake.utils.online import get_local_ip
    from agentmake.utils.handle_text import htmlToMarkdown, plainTextToUrl
    import re, requests, os

    DEFAULT_MAXIMUM_ONLINE_SEARCHES = int(os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES")) if os.getenv("DEFAULT_MAXIMUM_ONLINE_SEARCHES") else 5
    SEARXNG_HOST = os.getenv("SEARXNG_HOST") if os.getenv("SEARXNG_HOST") else f"http://{get_local_ip()}"
    SEARXNG_PORT = int(os.getenv("SEARXNG_PORT")) if os.getenv("SEARXNG_PORT") else 4000

    def refineSearchResults(content):
        content = htmlToMarkdown(content)
        content = re.sub(r"\nNext page\n[\d\D]*$", "", content) # trim the footer
        searchResults = content.split("\n#")[1:] # trim the header
        refinedSearchResults = []
        for result in searchResults:
            paragraphs = result.split("\n\n")
            textOnlyParagraphs = []
            for paragraph in paragraphs:
                if not re.search(r"\n\[[^\[\]]+\]\([^\)\)]+\)\n", f"\n{paragraph.strip()}\n"):
                    textOnlyParagraphs.append(paragraph.strip())
            if textOnlyParagraphs:
                refinedSearchResults.append("\n\n".join(textOnlyParagraphs))
            elif strippedResult := result.strip():
                refinedSearchResults.append(strippedResult)
            if len(refinedSearchResults) >= DEFAULT_MAXIMUM_ONLINE_SEARCHES:
                break
        return "#" + "\n\n#".join(refinedSearchResults)

    fullUrl = f"{SEARXNG_HOST}:{SEARXNG_PORT}/search?q={plainTextToUrl(keywords)}&categories={category}"
    with requests.get(fullUrl, timeout=60) as response:
        context = response.text
        context = refineSearchResults(context) if context else ""

        print("```url")
        print(fullUrl)
        print("```")
    
    return context

TOOL_SCHEMA = {
    "name": "search_searxng_news",
    "description": "Perform online searches up-to-date and real-time news information",
    "parameters": {
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "Keywords for online news searches",
            },
        },
        "required": ["keywords"],
    },
}

TOOL_FUNCTION = search_searxng_news