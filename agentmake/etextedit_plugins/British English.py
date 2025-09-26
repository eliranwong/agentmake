def british_english(event=None):
    custom_prompt = "Refine and enhance written content to align with standard British English conventions."

    if custom_prompt is not None:
        buffer = event.app.current_buffer if event is not None else text_field.buffer
        selectedText = buffer.copy_selection().text
        content = selectedText if selectedText else buffer.text
        content = agentmake(get_augment_instruction(custom_prompt, content), system="auto" if ApplicationState.auto_agent else None, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
        # insert the improved prompt as a code block
        buffer.insert_text(format_assistant_content(content))
        # Repaint the application; get_app().invalidate() does not work here
        get_app().reset()