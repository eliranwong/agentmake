from agentmake import config
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json, os, re


class OpenaiAI:

    DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY")
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL") if os.getenv("OPENAI_MODEL") else "gpt-4o"
    DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE")) if os.getenv("OPENAI_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS")) if os.getenv("OPENAI_MAX_TOKENS") else 16384 # https://platform.openai.com/docs/models

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or OpenaiAI.DEFAULT_API_KEY:
            config.openai_client = OpenAI(api_key=api_key if api_key else OpenaiAI.DEFAULT_API_KEY)
            return config.openai_client
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
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> ChatCompletion:
        if not api_key and not OpenaiAI.DEFAULT_API_KEY:
            raise ValueError("OpenAI API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        # tweaks for reasoning models
        model = model if model else OpenaiAI.DEFAULT_MODEL
        extras = {"stream": stream,} if re.search("^o[0-9]", model) else {
            "temperature": temperature if temperature is not None else OpenaiAI.DEFAULT_TEMPERATURE,
            "max_tokens": max_tokens if max_tokens else OpenaiAI.DEFAULT_MAX_TOKENS,
            "stream": stream,
        }
        return OpenaiAI.getClient(api_key=api_key).chat.completions.create(
            model=model if model else OpenaiAI.DEFAULT_MODEL,
            messages=messages,
            #temperature=temperature if temperature is not None else OpenaiAI.DEFAULT_TEMPERATURE,
            #max_tokens=max_tokens if max_tokens else OpenaiAI.DEFAULT_MAX_TOKENS,
            tools=[{"type": "function", "function": schema}] if schema else None,
            tool_choice={"type": "function", "function": {"name": schema["name"]}} if schema else None,
            #stream=stream,
            stop=stop,
            timeout=api_timeout,
            **extras,
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
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = OpenaiAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
