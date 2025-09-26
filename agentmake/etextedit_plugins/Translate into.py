def translate_into(event=None):
    async def coroutine():
        prompt_dialog = MultilineTextInputDialog(
            title="Translate into ...",
            label="Enter the target language:",
        )

        target_language = await show_dialog_as_float(prompt_dialog)

        if target_language is not None:
            buffer = event.app.current_buffer if event is not None else text_field.buffer
            selectedText = buffer.copy_selection().text
            content = selectedText if selectedText else buffer.text
            content = agentmake(get_augment_instruction(f"Please translate the following content into {target_language}.", content), system="auto" if ApplicationState.auto_agent else None, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
            # insert the improved prompt as a code block
            buffer.insert_text(format_assistant_content(content))
            # Repaint the application; get_app().invalidate() does not work here
            get_app().reset()
    
    ensure_future(coroutine())