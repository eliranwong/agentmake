from agentmake.utils.manage_package import installPipPackage
REQUIREMENTS = ["qrcode"]
try:
    import qrcode
except:
    for i in REQUIREMENTS:
        installPipPackage(i)
    import qrcode

def create_qrcode(url: str="", text: str="", **kwargs):
    import os, qrcode, shutil
    from agentmake import getOpenCommand, getCurrentDateTime

    def openImageFile(imageFile):
        openCmd = getOpenCommand()
        if shutil.which("termux-share"):
            os.system(f"termux-share {imageFile}")
        elif shutil.which(openCmd):
            cli = f"{openCmd} {imageFile}"
            os.system(cli)
            #subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        message = f"Image saved: {imageFile}"
        print(message)

    url = url if url else text
    if not url:
        return None
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    filepath = os.path.join(os.getcwd(), f"qr_code_{getCurrentDateTime()}.png")
    img = qr.make_image(fill='black', back_color='white')
    img.save(filepath)
    
    if os.path.isfile(filepath):
        openImageFile(filepath)
        print(f"File saved: {filepath}")
    return ""

TOOL_SCHEMA = {
    "name": "create_qrcode",
    "description": f'''Create QR code''',
    "parameters": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The url that is to be converted into qr code. Return '' if not given.",
            },
            "text": {
                "type": "string",
                "description": "The text content that is to be converted into qr code. Return '' if not given.",
            },
        },
        "required": ["url", "text"],
    },
}

TOOL_FUNCTION = create_qrcode