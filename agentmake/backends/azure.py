from openai import AzureOpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json, os


class AzureLLM:
    
    DEFAULT_API_VERSION = "2024-10-21" # check the latest api version at https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#data-plane-inference
    DEFAULT_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") if os.getenv("AZURE_OPENAI_API_KEY") else os.getenv("AZURE_API_KEY")
    DEFAULT_API_ENDPOINT = ""
    DEFAULT_MODEL = "gpt-4o"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 16384

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
        if not api_key and not AzureLLM.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        if not api_endpoint and not AzureLLM.DEFAULT_API_ENDPOINT:
            raise ValueError("API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return AzureOpenAI(api_key=api_key if api_key else AzureLLM.DEFAULT_API_KEY, azure_endpoint=api_endpoint if api_endpoint else AzureLLM.DEFAULT_API_ENDPOINT, api_version=AzureLLM.DEFAULT_API_VERSION).chat.completions.create(
            model=model if model else AzureLLM.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else AzureLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else AzureLLM.DEFAULT_MAX_TOKENS,
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
        completion = AzureLLM.getChatCompletion(
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
