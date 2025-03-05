from agentmake import config
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json
import os


class AzureAI:
    
    DEFAULT_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") if os.getenv("AZURE_OPENAI_API_VERSION") else "2024-10-21" # check the latest api version at https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#data-plane-inference
    DEFAULT_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") if os.getenv("AZURE_OPENAI_API_KEY") else ""
    DEFAULT_API_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT") if os.getenv("AZURE_OPENAI_API_ENDPOINT") else ""
    DEFAULT_MODEL = os.getenv("AZURE_OPENAI_MODEL") if os.getenv("AZURE_OPENAI_MODEL") else "gpt-4o"
    DEFAULT_TEMPERATURE = float(os.getenv("AZURE_OPENAI_TEMPERATURE")) if os.getenv("AZURE_OPENAI_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("AZURE_OPENAI_MAX_TOKENS")) if os.getenv("AZURE_OPENAI_MAX_TOKENS") else 16384

    DEFAULT_DALLE_API_KEY = os.getenv("AZURE_DALLE_API_KEY") if os.getenv("AZURE_DALLE_API_KEY") else ""
    DEFAULT_DALLE_API_ENDPOINT = os.getenv("AZURE_DALLE_API_ENDPOINT") if os.getenv("AZURE_DALLE_API_ENDPOINT") else ""
    DEFAULT_DALLE_MODEL = os.getenv("AZURE_DALLE_MODEL") if os.getenv("AZURE_DALLE_MODEL") else "dall-e-3"

    DEFAULT_WHISPER_API_KEY = os.getenv("AZURE_WHISPER_API_KEY") if os.getenv("AZURE_WHISPER_API_KEY") else ""
    DEFAULT_WHISPER_API_ENDPOINT = os.getenv("AZURE_WHISPER_API_ENDPOINT") if os.getenv("AZURE_WHISPER_API_ENDPOINT") else ""
    DEFAULT_WHISPER_MODEL = os.getenv("AZURE_WHISPER_MODEL") if os.getenv("AZURE_WHISPER_MODEL") else "whisper"

    @staticmethod
    def getClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        if (api_key or AzureAI.DEFAULT_API_KEY) and (api_endpoint or AzureAI.DEFAULT_API_ENDPOINT):
            config.azure_client = AzureOpenAI(
                api_key=api_key if api_key else AzureAI.DEFAULT_API_KEY,
                azure_endpoint=api_endpoint if api_endpoint else AzureAI.DEFAULT_API_ENDPOINT,
                api_version=AzureAI.DEFAULT_API_VERSION,
            )
            return config.azure_client
        return None

    @staticmethod
    def getDalleClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        if (api_key or AzureAI.DEFAULT_DALLE_API_KEY) and (api_endpoint or AzureAI.DEFAULT_DALLE_API_ENDPOINT):
            config.azure_client = AzureOpenAI(
                api_key=api_key if api_key else AzureAI.DEFAULT_DALLE_API_KEY,
                azure_endpoint=api_endpoint if api_endpoint else AzureAI.DEFAULT_DALLE_API_ENDPOINT,
                api_version=AzureAI.DEFAULT_API_VERSION,
            )
            return config.azure_client
        return None

    @staticmethod
    def getWhisperClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        if (api_key or AzureAI.DEFAULT_WHISPER_API_KEY) and (api_endpoint or AzureAI.DEFAULT_WHISPER_API_ENDPOINT):
            config.azure_client = AzureOpenAI(
                api_key=api_key if api_key else AzureAI.DEFAULT_WHISPER_API_KEY,
                azure_endpoint=api_endpoint if api_endpoint else AzureAI.DEFAULT_WHISPER_API_ENDPOINT,
                api_version=AzureAI.DEFAULT_API_VERSION,
            )
            return config.azure_client
        return None

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
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> ChatCompletion:
        if not api_key and not AzureAI.DEFAULT_API_KEY:
            raise ValueError("Azure API key is required.")
        if not api_endpoint and not AzureAI.DEFAULT_API_ENDPOINT:
            raise ValueError("Azure API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return AzureAI.getClient(api_key=api_key, api_endpoint=api_endpoint).chat.completions.create(
            model=model if model else AzureAI.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else AzureAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else AzureAI.DEFAULT_MAX_TOKENS,
            tools=[{"type": "function", "function": schema}] if schema else None,
            tool_choice={"type": "function", "function": {"name": schema["name"]}} if schema else None,
            stream=stream,
            stop=stop,
            timeout=api_timeout,
            **kwargs
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
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = AzureAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
