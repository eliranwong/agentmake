def phi4_azure(messages, **kwargs):
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential

    azure_messages = []
    for i in messages:
        role = i.get("role", "")
        content = i.get("content", "")
        if role == "system":
            azure_messages.append(SystemMessage(content))
        elif role == "user":
            azure_messages.append(UserMessage(content))
        elif role == "assistant":
            azure_messages.append(AssistantMessage(content))

    model_name = os.getenv("AZURE_PHI_MODEL")

    client = ChatCompletionsClient(
        endpoint=os.getenv("AZURE_PHI_API_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_PHI_API_KEY")),
        temperature=float(os.getenv("AZURE_PHI_TEMPERATURE")),
        max_tokens=int(os.getenv("AZURE_PHI_MAX_TOKENS")),
    )

    response = client.complete(
        stream=True,
        messages=azure_messages,
        model=model_name,
    )

    for update in response:
        if update.choices and update.choices[0].delta:
            print(update.choices[0].delta.content or "", end="")

    client.close()

    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Provide user with information via reasoning model Phi-4 via Azure service."""

TOOL_FUNCTION = phi4_azure