def send_sms(phone_number: str, message: str, **kwargs):
    import subprocess
    message = message.replace('"', '\\"') # required
    cli = f'''termux-sms-send -n {phone_number} "{message}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "send_sms",
    "description": f'''Send sms message.''',
    "parameters": {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "The phone number of the selected person to which the message is sent.",
            },
            "message": {
                "type": "string",
                "description": "Generate SMS message",
            },
        },
        "required": ["phone_number", "message"],
    },
}

TOOL_FUNCTION = send_sms