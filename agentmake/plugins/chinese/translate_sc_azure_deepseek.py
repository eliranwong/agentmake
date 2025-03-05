def translate_into_traditional_chinese_azure_deepseeek(content, **kwargs):
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential

    model_name = os.getenv("AZURE_DEEPSEEK_MODEL")

    client = ChatCompletionsClient(
        endpoint=os.getenv("AZURE_DEEPSEEK_API_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_DEEPSEEK_API_KEY")),
    )

    response = client.complete(
        stream=True,
        messages=[
            SystemMessage("Translate the given content into traditional Chinese. Do NOT think, just translate. Provide me with the translation only, without extra comments or explanations."),
            UserMessage(content),
        ],
        model=model_name,
    )

    text_ouptut = ""
    print("```translation")
    for update in response:
        if update.choices and update.choices[0].delta:
            chunk = update.choices[0].delta.content or ""
            text_ouptut += chunk
            print(chunk, end="")
    print("```")

    client.close()

    return text_ouptut

CONTENT_PLUGIN = translate_into_traditional_chinese_azure_deepseeek