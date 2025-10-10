from agentmake import config
from typing import Optional
import json
import os, traceback
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage, ChatCompletionsToolDefinition, FunctionDefinition
from azure.core.credentials import AzureKeyCredential

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class GithubAnyAI:

    DEFAULT_API_KEY = os.getenv("GITHUB_ANY_API_KEY").split(",") if os.getenv("GITHUB_ANY_API_KEY") else [""]
    DEFAULT_MODEL = os.getenv("GITHUB_ANY_MODEL") if os.getenv("GITHUB_ANY_MODEL") else "DeepSeek-V3"
    DEFAULT_TEMPERATURE = float(os.getenv("GITHUB_ANY_TEMPERATURE")) if os.getenv("GITHUB_ANY_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("GITHUB_ANY_MAX_TOKENS")) if os.getenv("GITHUB_ANY_MAX_TOKENS") else 4000 # https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(GithubAnyAI.DEFAULT_API_KEY) > 1:
            first_item = GithubAnyAI.DEFAULT_API_KEY.pop(0)
            GithubAnyAI.DEFAULT_API_KEY.append(first_item)
        return GithubAnyAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or GithubAnyAI.DEFAULT_API_KEY[0]:
            token = os.environ["GITHUB_TOKEN"] = api_key if api_key else GithubAnyAI.getApiKey()
            config.github_any_client = ChatCompletionsClient(
                endpoint="https://models.inference.ai.azure.com",
                credential=AzureKeyCredential(token),
            )
            return config.github_any_client
        return None

    @staticmethod
    def toAzureMessages(messages: list):
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
        return azure_messages

    @staticmethod
    def getChatCompletion(
        messages: list,
        model: Optional[str]=None,
        schema: Optional[dict]=None,
        temperature: Optional[float]=None,
        max_tokens: Optional[int]=None,
        #context_window: Optional[int]=None, # applicable to ollama only
        #batch_size: Optional[int]=None, # applicable to ollama only
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        stream: Optional[bool]=False,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        #api_timeout: Optional[float]=None,
        **kwargs,
    ):
        if not api_key and not GithubAnyAI.DEFAULT_API_KEY:
            raise ValueError("Azure API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        completion = None
        used_api_keys = []
        while completion is None:

            this_api_key = api_key if api_key else GithubAnyAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                completion = GithubAnyAI.getClient(api_key=this_api_key).complete(
                    stream=stream,
                    messages=GithubAnyAI.toAzureMessages(messages),
                    model=model if model else GithubAnyAI.DEFAULT_MODEL,
                    temperature=temperature if temperature is not None else GithubAnyAI.DEFAULT_TEMPERATURE,
                    max_tokens=max_tokens if max_tokens else GithubAnyAI.DEFAULT_MAX_TOKENS,
                    stop=stop,
                    #response_format='json_object',
                    tools=[ChatCompletionsToolDefinition(function=FunctionDefinition(**schema))] if schema else None,
                    tool_choice="required" if schema else None,
                    **kwargs,
                )
            except Exception as e:
                print(f"An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
                print(f"Failed API key: {this_api_key}")
        return completion

    @staticmethod
    def getDictionaryOutput(
        messages: list,
        schema: dict,
        model: Optional[str]=None,
        temperature: Optional[float]=None, 
        max_tokens: Optional[int]=None,
        #context_window: Optional[int]=None, # applicable to ollama only
        #batch_size: Optional[int]=None, # applicable to ollama only
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        #api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = GithubAnyAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            #api_endpoint=api_endpoint,
            #api_timeout=api_timeout,
            **kwargs
        )
        if not completion.choices[0].message.tool_calls:
            print(f"```error\nNo tool calls found. Check if the model '{model}' supports tools.\n```")
            return {}
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments.replace("'", '"'))
