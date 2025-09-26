def speak(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    selectedText = buffer.copy_selection().text
    content = selectedText if selectedText else buffer.text
    content = re.sub('''[*'"`]''', "", content).replace("\n", " ").strip()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ResourceWarning)
        subprocess.Popen(f'''ai -t tts/speak_edge "{content}"''', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)