from groq import Groq
from groq.types.chat.chat_completion import ChatCompletion
from typing import Optional
import json, os


class GroqAI:

    DEFAULT_API_KEY = os.getenv("GROQ_API_KEY")
    DEFAULT_MODEL = os.getenv("GROQ_MODEL") if os.getenv("GROQ_MODEL") else "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE")) if os.getenv("GROQ_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS")) if os.getenv("GROQ_MAX_TOKENS") else 32768 # https://console.groq.com/docs/models

    @staticmethod
    def getChatCompletion(
        messages: list,
        model: Optional[str]=None,
        schema: Optional[dict]=None,
        temperature: Optional[float]=None,
        max_tokens: Optional[int]=None,
        #context_window: Optional[int]=None, # applicable to ollama only
        #batch_size: Optional[int]=None, # applicable to ollama only
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        stream: Optional[bool]=False,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> ChatCompletion:
        if not api_key and not GroqAI.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill})
        return Groq(api_key=api_key if api_key else GroqAI.DEFAULT_API_KEY).chat.completions.create(
            model=model if model else GroqAI.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else GroqAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else GroqAI.DEFAULT_MAX_TOKENS,
            tools=[{"type": "function", "function": schema}] if schema else None,
            tool_choice={"type": "function", "function": {"name": schema["name"]}} if schema else "none",
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
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = GroqAI.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
