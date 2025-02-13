def send_tweet(message: str, **kwargs):

    from agentmake.utils.online import openURL
    import urllib.parse

    if message:
        openURL(f"""https://twitter.com/intent/tweet?text={urllib.parse.quote(message)}""")
    return ""

TOOL_SCHEMA = {
    "name": "send_tweet",
    "description": f'''Generate a tweet to twitter''',
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The generated message that is to be sent to twitter. You generate this message according to user input.",
            },
        },
        "required": ["message"],
    },
}

TOOL_FUNCTION =send_tweet