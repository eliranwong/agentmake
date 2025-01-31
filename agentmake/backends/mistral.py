from mistralai import Mistral, ChatCompletionResponse, UNSET, CompletionEvent
from mistralai.utils.eventstreaming import EventStream
from typing import Optional, Union
import json, os


class MistralLLM:
    # docs: https://docs.mistral.ai/

    DEFAULT_API_KEY = os.getenv("MISTRAL_API_KEY")
    DEFAULT_MODEL = "mistral-large-latest"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 8000 # https://docs.mistral.ai/getting-started/models/models_overview/

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
            api_timeout: Optional[int]=None,
            **kwargs,
    ) -> Union[EventStream[CompletionEvent], ChatCompletionResponse]:
        if not api_key and not MistralLLM.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill, "prefix": True})
        return Mistral(api_key=api_key if api_key else MistralLLM.DEFAULT_API_KEY).chat.stream(
            model=model if model else MistralLLM.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else MistralLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else MistralLLM.DEFAULT_MAX_TOKENS,
            stop=stop,
            timeout_ms=api_timeout,
            **kwargs
        ) if stream else Mistral(api_key=api_key if api_key else MistralLLM.DEFAULT_API_KEY).chat.complete(
            model=model if model else MistralLLM.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else MistralLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else MistralLLM.DEFAULT_MAX_TOKENS,
            tools=[{"type": "function", "function": schema}] if schema else UNSET,
            tool_choice="any" if schema else None,
            stop=stop,
            timeout_ms=api_timeout,
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
            api_timeout: Optional[int]=None,
            **kwargs,
    ) -> dict:
        completion = MistralLLM.getChatCompletion(
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
