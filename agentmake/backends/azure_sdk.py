from agentmake import config
from typing import Optional
import json
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage, ChatCompletionsToolDefinition, FunctionDefinition
from azure.core.credentials import AzureKeyCredential

class AzureSdkAI:

    DEFAULT_API_KEY = os.getenv("AZURE_SDK_API_KEY") if os.getenv("AZURE_SDK_API_KEY") else ""
    DEFAULT_API_ENDPOINT = os.getenv("AZURE_SDK_API_ENDPOINT") if os.getenv("AZURE_SDK_API_ENDPOINT") else ""
    DEFAULT_MODEL = os.getenv("AZURE_SDK_MODEL") if os.getenv("AZURE_SDK_MODEL") else "DeepSeek-V3"
    DEFAULT_TEMPERATURE = float(os.getenv("AZURE_SDK_TEMPERATURE")) if os.getenv("AZURE_SDK_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("AZURE_SDK_MAX_TOKENS")) if os.getenv("AZURE_SDK_MAX_TOKENS") else 8000

    @staticmethod
    def getClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        if (api_key or AzureSdkAI.DEFAULT_API_KEY) and (api_endpoint or AzureSdkAI.DEFAULT_API_ENDPOINT):
            config.azure_sdk_client = ChatCompletionsClient(
                endpoint=api_endpoint if api_endpoint else AzureSdkAI.DEFAULT_API_ENDPOINT,
                credential=AzureKeyCredential(api_key if api_key else AzureSdkAI.DEFAULT_API_KEY),
            )
            return config.azure_sdk_client
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
        api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        #api_timeout: Optional[float]=None,
        **kwargs,
    ):
        if not api_key and not AzureSdkAI.DEFAULT_API_KEY:
            raise ValueError("Azure API key is required.")
        if not api_endpoint and not AzureSdkAI.DEFAULT_API_ENDPOINT:
            raise ValueError("Azure API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return AzureSdkAI.getClient(api_key=api_key, api_endpoint=api_endpoint).complete(
            stream=stream,
            messages=AzureSdkAI.toAzureMessages(messages),
            model=model if model else AzureSdkAI.DEFAULT_MODEL,
            temperature=temperature if temperature is not None else AzureSdkAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else AzureSdkAI.DEFAULT_MAX_TOKENS,
            stop=stop,
            #response_format='json_object',
            tools=[ChatCompletionsToolDefinition(function=FunctionDefinition(**schema))] if schema else None,
            tool_choice="required" if schema else None,
            **kwargs,
        )

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
        api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        #api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = AzureSdkAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            #api_timeout=api_timeout,
            **kwargs
        )
        if not completion.choices[0].message.tool_calls:
            print(f"```error\nNo tool calls found. Check if the model '{model}' supports tools.\n```")
            return {}
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments.replace("'", '"'))
