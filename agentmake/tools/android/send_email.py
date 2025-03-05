def send_email(email_address: str, subject: str, body: str, **kwargs):
    import urllib.parse
    import subprocess
    subject = urllib.parse.quote(subject.replace('"', '\\"'))
    body = urllib.parse.quote(body.replace('"', '\\"'))

    # e.g. am start -a android.intent.action.SENDTO -d "mailto:john.doe@example.com?subject=Hello&body=How%20are%20you?"
    cli = f'''am start -a android.intent.action.SENDTO -d "mailto:{email_address}?subject={subject}&body={body}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "send_email",
    "description": "Send email",
    "parameters": {
        "type": "object",
        "properties": {
            "email_address": {
                "type": "string",
                "description": "The recipient email address. Return an empty string '' if user does not specify an email address.",
            },
            "subject": {
                "type": "string",
                "description": "Give a title to the email.",
            },
            "body": {
                "type": "string",
                "description": "The body or content of the email.",
            },
        },
        "required": ["email_address", "subject", "body"],
    },
}

TOOL_FUNCTION = send_email