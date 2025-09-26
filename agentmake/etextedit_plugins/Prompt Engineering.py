def prompt_engineering(event=None):
    buffer = event.app.current_buffer if event is not None else text_field.buffer
    selectedText = buffer.copy_selection().text
    content = selectedText if selectedText else buffer.text
    content = agentmake(content, system="improve_prompt_2", **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
    content = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", content, flags=re.DOTALL).strip()
    # insert the improved prompt
    buffer.insert_text(format_assistant_content(content))
    # Repaint the application; get_app().invalidate() does not work here
    get_app().reset()