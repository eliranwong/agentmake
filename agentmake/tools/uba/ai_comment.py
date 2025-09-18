TOOL_SYSTEM = ""
TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Read bible commentary."""

def commentary(messages, **kwargs):
    from agentmake.plugins.uba.lib.BibleParser import BibleVerseParser
    from agentmake.utils.online import get_local_ip
    import requests, os, re

    UBA_API_LOCAL_PORT = int(os.getenv("UBA_API_LOCAL_PORT")) if os.getenv("UBA_API_LOCAL_PORT") else 8080
    UBA_API_ENDPOINT = os.getenv("UBA_API_ENDPOINT") if os.getenv("UBA_API_ENDPOINT") else f"http://{get_local_ip()}:{UBA_API_LOCAL_PORT}/plain" # use dynamic local ip if endpoint is not specified
    UBA_API_TIMEOUT = int(os.getenv("UBA_API_TIMEOUT")) if os.getenv("UBA_API_TIMEOUT") else 10
    UBA_API_PRIVATE_KEY = os.getenv("UBA_API_PRIVATE_KEY") if os.getenv("UBA_API_PRIVATE_KEY") else ""

    def get_ai_comment(command, b, c, v):
        endpoint = re.sub("/plain$", "/html", UBA_API_ENDPOINT)
        private = f"private={UBA_API_PRIVATE_KEY}&" if UBA_API_PRIVATE_KEY else ""
        url = f"""{endpoint}?{private}cmd={command}"""
        try:
            response = requests.get(url, timeout=UBA_API_TIMEOUT)
            response.encoding = "utf-8"
            readableRef = BibleVerseParser(False).bcvToVerseReference(b,c,v)
            text_output = re.sub("# AI Commentary", f"# AI Commentary - {readableRef}", response.text.strip())
            print(text_output, "\n")
        except Exception as err:
            print(f"An error occurred: {err}")

    user_input = messages[-1].get("content", "")
    refs = BibleVerseParser(False).extractExhaustiveReferences(user_input)
    if refs:
        for b,c,v in refs:
            command = f"AIC:::NET:::{b}.{c}.{v}"
            get_ai_comment(command, b, c, v)
    else:
        print("Please provide a valid Bible reference to complete your request.")
        return ""
    
    return ""

TOOL_FUNCTION = commentary