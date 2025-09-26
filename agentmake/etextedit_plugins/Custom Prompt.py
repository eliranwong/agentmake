def custom_prompt(event=None):
    async def coroutine():
        prompt_dialog = MultilineTextInputDialog(
            title="Custom Prompt",
            label="Enter your prompt:",
        )

        custom_prompt = await show_dialog_as_float(prompt_dialog)

        if custom_prompt is not None:
            buffer = event.app.current_buffer if event is not None else text_field.buffer
            selectedText = buffer.copy_selection().text
            content = selectedText if selectedText else buffer.text
            content = agentmake(get_augment_instruction(custom_prompt, content), system="auto" if ApplicationState.auto_agent else None, **AGENTMAKE_CONFIG)[-1].get("content", "").strip()
            # insert the improved prompt as a code block
            buffer.insert_text(format_assistant_content(content))
            # Repaint the application; get_app().invalidate() does not work here
            get_app().reset()
    
    ensure_future(coroutine())