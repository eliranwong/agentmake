from agentmake import config
from mistralai import Mistral, ChatCompletionResponse, UNSET, CompletionEvent
from mistralai.utils.eventstreaming import EventStream
from typing import Optional, Union
import traceback
import json
import os

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class MistralAI:
    # docs: https://docs.mistral.ai/

    DEFAULT_API_KEY = os.getenv("MISTRAL_API_KEY").split(",") if os.getenv("MISTRAL_API_KEY") and "," in os.getenv("MISTRAL_API_KEY") else [os.getenv("MISTRAL_API_KEY")]
    DEFAULT_MODEL = os.getenv("MISTRAL_MODEL") if os.getenv("MISTRAL_MODEL") else "mistral-large-latest"
    DEFAULT_TEMPERATURE = float(os.getenv("MISTRAL_TEMPERATURE")) if os.getenv("MISTRAL_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("MISTRAL_MAX_TOKENS")) if os.getenv("MISTRAL_MAX_TOKENS") else 8000 # https://docs.mistral.ai/getting-started/models/models_overview/

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(MistralAI.DEFAULT_API_KEY) > 1:
            first_item = MistralAI.DEFAULT_API_KEY.pop(0)
            MistralAI.DEFAULT_API_KEY.append(first_item)
        return MistralAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or MistralAI.DEFAULT_API_KEY[0]:
            config.mistral_client = Mistral(api_key=api_key if api_key else MistralAI.getApiKey())
            return config.mistral_client
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
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        stream: Optional[bool]=False,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[int]=None,
        # to work with mistral streaming object
        stream_events_only: Optional[bool]=False,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
        **kwargs,
    ) -> Union[EventStream[CompletionEvent], ChatCompletionResponse]:
        if not api_key and not MistralAI.DEFAULT_API_KEY[0]:
            raise ValueError("Mistral API key is required.")
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill, "prefix": True})
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else MistralAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                client = MistralAI.getClient(api_key=this_api_key)
                completion = client.chat.stream(
                    model=model if model else MistralAI.DEFAULT_MODEL,
                    messages=messages,
                    temperature=temperature if temperature is not None else MistralAI.DEFAULT_TEMPERATURE,
                    max_tokens=max_tokens if max_tokens else MistralAI.DEFAULT_MAX_TOKENS,
                    stop=stop,
                    timeout_ms=api_timeout,
                    **kwargs
                ) if stream else client.chat.complete(
                    model=model if model else MistralAI.DEFAULT_MODEL,
                    messages=messages,
                    temperature=temperature if temperature is not None else MistralAI.DEFAULT_TEMPERATURE,
                    max_tokens=max_tokens if max_tokens else MistralAI.DEFAULT_MAX_TOKENS,
                    tools=[{"type": "function", "function": schema}] if schema else UNSET,
                    tool_choice="any" if schema else None,
                    stop=stop,
                    timeout_ms=api_timeout,
                    **kwargs
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
        prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[int]=None,
        **kwargs,
    ) -> dict:
        completion = MistralAI.getChatCompletion(
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
