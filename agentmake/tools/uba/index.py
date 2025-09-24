TOOL_SYSTEM = ""
TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Get bible verse smart indexes."""

def index(messages, **kwargs):
    from agentmake.utils.online import get_local_ip
    import requests, os, re
    import urllib.parse
    from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser

    command = messages[-1].get("content", "")
    command = BibleVerseParser(False).extractAllReferencesReadable(command)
    if not command:
        print("Please provide a valid Bible reference to complete your request.")
        return ""
    command = urllib.parse.quote_plus(command)
    command = f"INDEX:::{command}"

    UBA_API_LOCAL_PORT = int(os.getenv("UBA_API_LOCAL_PORT")) if os.getenv("UBA_API_LOCAL_PORT") else 8080
    UBA_API_ENDPOINT = os.getenv("UBA_API_ENDPOINT") if os.getenv("UBA_API_ENDPOINT") else f"http://{get_local_ip()}:{UBA_API_LOCAL_PORT}/plain" # use dynamic local ip if endpoint is not specified
    UBA_API_TIMEOUT = int(os.getenv("UBA_API_TIMEOUT")) if os.getenv("UBA_API_TIMEOUT") else 10
    UBA_API_PRIVATE_KEY = os.getenv("UBA_API_PRIVATE_KEY") if os.getenv("UBA_API_PRIVATE_KEY") else ""

    endpoint = UBA_API_ENDPOINT
    private = f"private={UBA_API_PRIVATE_KEY}&" if UBA_API_PRIVATE_KEY else ""
    url = f"""{endpoint}?{private}cmd={command}"""
    try:
        response = requests.get(url, timeout=UBA_API_TIMEOUT)
        response.encoding = "utf-8"
        content = response.text.strip()
        content = content.replace("\nsearch for a location", "").replace("""\nBible Locations\n\n[not applicable]""", "")
        content = content.replace("search for a character\nsearch for a name & its meaning", "")
        content = re.sub(r"\[search a .*?\n", "", content)
        content = re.sub(r"\[search an encyclope.*?$", "", content)
        print("## "+content.replace("[", "- ["))
    except Exception as err:
        print(f"An error occurred: {err}")
    
    return ""

TOOL_FUNCTION = index