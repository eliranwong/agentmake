from agentmake import config
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json
import os


class OpenaiCompatibleAI:

    DEFAULT_API_KEY = os.getenv("CUSTOM_API_KEY") if os.getenv("CUSTOM_API_KEY") else "agentmake"
    DEFAULT_API_ENDPOINT = os.getenv("CUSTOM_API_ENDPOINT") if os.getenv("CUSTOM_API_ENDPOINT") else "" # e.g. "http://localhost:11434/v1" for Ollama
    DEFAULT_MODEL = os.getenv("CUSTOM_MODEL")
    DEFAULT_TEMPERATURE = float(os.getenv("CUSTOM_TEMPERATURE")) if os.getenv("CUSTOM_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("CUSTOM_MAX_TOKENS")) if os.getenv("CUSTOM_MAX_TOKENS") else 4000 # https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits

    @staticmethod
    def getClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        config.custom_client = OpenAI(api_key=api_key if api_key else OpenaiCompatibleAI.DEFAULT_API_KEY, base_url=api_endpoint if api_endpoint else OpenaiCompatibleAI.DEFAULT_API_ENDPOINT)
        return config.custom_client

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
        #if not api_key and not OpenaiCompatibleAI.DEFAULT_API_KEY:
        #    raise ValueError("API key is required.")
        #if not api_endpoint and not OpenaiCompatibleAI.DEFAULT_API_ENDPOINT:
        #    raise ValueError("API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return OpenaiCompatibleAI.getClient(api_key=api_key, api_endpoint=api_endpoint).chat.completions.create(
            model=model if model else OpenaiCompatibleAI.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else OpenaiCompatibleAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else OpenaiCompatibleAI.DEFAULT_MAX_TOKENS,
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
        completion = OpenaiCompatibleAI.getChatCompletion(
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
