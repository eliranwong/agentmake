def translate_traditional_chinese_deepseek(content, **kwargs):
    from agentmake import agentmake
    
    print_on_terminal = kwargs.get("print_on_terminal")
    if print_on_terminal:
        print("```translation")
    messages = agentmake(
        content,
        system="Translate the given content into simplified Chinese. Provide me with the translation only, without additional explanations.",
        backend="openai",
        model="gpt-4o",
    )
    if print_on_terminal:
        print("```")
    translation = messages[-1].get("content", "")
    return translation

CONTENT_PLUGIN = translate_traditional_chinese_deepseek