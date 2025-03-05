TOOL_SYSTEM = "You are an expert in writing emails, specializing in generating email title and content based on user requests. You are also skilled at finding the recipient's email address from the information provided."

TOOL_SCHEMA = {
    "name": "send_outlook",
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
            "eamil_content": {
                "type": "string",
                "description": "The body or content of the email.",
            },
        },
        "required": ["email_title", "eamil_content"],
    },
}

def send_outlook(email_title: str, eamil_content: str, email_address: str="", **kwargs):

    from agentmake.utils.online import openURL
    import urllib.parse

    subject = urllib.parse.quote(email_title)
    body = urllib.parse.quote(eamil_content)

    def getOutlookLink():
        link = "https://outlook.office.com/owa/?path=/mail/action/compose"
        if email_address:
            link += f"&to={email_address}"
        if subject:
            link += f"&subject={subject}"
        if body:
            link += f"&body={body}"
        return link

    openURL(getOutlookLink())
    return ""

TOOL_FUNCTION = send_outlook