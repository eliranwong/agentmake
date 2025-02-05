import pyperclip, shutil
from agentmake.utils.system import getCliOutput

def paste_text(content):
    try:
        clipboardText = getCliOutput("termux-clipboard-get") if shutil.which("termux-clipboard-get") else pyperclip.paste()
        return content.rstrip() + f"\n\n{clipboardText}"
    except:
        return content

CONTENT_PLUGIN = paste_text