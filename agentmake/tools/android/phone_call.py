def phone_call(phone_number: str, **kwargs):
    import subprocess
    cli = f'''termux-telephony-call {phone_number}'''
    subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return ""

TOOL_SCHEMA = {
    "name": "phone_call",
    "description": f'''Make a phone call''',
    "parameters": {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "The phone number of the selected person",
            },
        },
        "required": ["phone_number"],
    },
}

TOOL_FUNCTION = phone_call