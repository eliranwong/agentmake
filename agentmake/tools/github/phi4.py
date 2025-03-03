def phi4_github(messages, **kwargs):
    import os
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
    from azure.core.credentials import AzureKeyCredential
    from agentmake import GithubAI

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

    token = os.environ["GITHUB_TOKEN"] = GithubAI.getApiKey()
    endpoint = "https://models.inference.ai.azure.com"
    model_name = "Phi-4"

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
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
TOOL_DESCRIPTION = """Provide user with information via reasoning model Phi-4 via Github tokens."""

TOOL_FUNCTION = phi4_github