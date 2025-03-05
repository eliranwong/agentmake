def send_whatsapp(message: str, **kwargs):
    import subprocess
    message = message.replace('"', '\\"') # required
    # e.g. am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+441234567&text=Hello"
    # https://api.whatsapp.com/send?phone=+18772241042
    cli = f'''am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?text={message}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "send_whatsapp",
    "description": f'''Send WhatsApp messages''',
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message that is to be sent to the recipient",
            },
        },
        "required": ["message"],
    },
}

TOOL_FUNCTION = send_whatsapp
