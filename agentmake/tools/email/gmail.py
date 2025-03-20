TOOL_SYSTEM = "You are an expert in writing emails, specializing in generating email title and content based on user requests. You are also skilled at finding the recipient's email address from the information provided."

TOOL_SCHEMA = {
    "name": "send_gmail",
    "description": "Send Gmail",
    "parameters": {
        "type": "object",
        "properties": {
            "email_address": {
                "type": "string",
                "description": "The recipient of the email.",
            },
            "email_title": {
                "type": "string",
                "description": "Give a title to the email.",
            },
            "email_content": {
                "type": "string",
                "description": "The body or content of the email.",
            },
        },
        "required": ["email_title", "email_content"],
    },
}

def send_gmail(email_title: str, email_content: str, email_address: str="", **kwargs):

    from agentmake.utils.online import openURL
    import urllib.parse

    subject = urllib.parse.quote(email_title)
    body = urllib.parse.quote(email_content)

    def getGoogleLink():
        link = "https://mail.google.com/mail/?view=cm&fs=1"
        if email_address:
            link += f"&to={email_address}"
        if subject:
            link += f"&su={subject}"
        if body:
            link += f"&body={body}"
        return link

    openURL(getGoogleLink())
    return ""

TOOL_FUNCTION = send_gmail