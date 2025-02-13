def ask_copilot(message: str, **kwargs):
    import subprocess
    message = message.replace('"', '\\"') # required
    # e.g. am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+441234567&text=Hello"
    # Microsoft Copilot Business Account: +18772241042
    cli = f'''am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=+18772241042&text={message}"'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "ask_copilot",
    "description": f'''Send request to Microsoft CoPilot via Whatsapp''',
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message being sent to Microsoft CoPilot",
            },
        },
        "required": ["message"],
    },
}

TOOL_FUNCTION = ask_copilot