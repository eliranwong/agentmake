def copy_text(content, **kwargs):
    import pyperclip, shutil, pydoc
    pydoc.pipepager(content, cmd="termux-clipboard-set") if shutil.which("termux-clipboard-set") else pyperclip.copy(content)
    return content

CONTENT_PLUGIN = copy_text