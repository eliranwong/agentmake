from agentmake import config
from cohere import ClientV2, ChatResponse
from cohere.core.request_options import RequestOptions
from typing import Optional
import json
import traceback
import os

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class CohereAI:

    DEFAULT_API_KEY = os.getenv("COHERE_API_KEY").split(",") if os.getenv("COHERE_API_KEY") and "," in os.getenv("COHERE_API_KEY") else [os.getenv("COHERE_API_KEY")]
    DEFAULT_MODEL = os.getenv("COHERE_MODEL") if os.getenv("COHERE_MODEL") else "command-r-plus" # https://docs.cohere.com/docs/models
    DEFAULT_TEMPERATURE = float(os.getenv("COHERE_TEMPERATURE")) if os.getenv("COHERE_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("COHERE_MAX_TOKENS")) if os.getenv("COHERE_MAX_TOKENS") else 4000 # https://docs.cohere.com/docs/rate-limits

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(CohereAI.DEFAULT_API_KEY) > 1:
            first_item = CohereAI.DEFAULT_API_KEY.pop(0)
            CohereAI.DEFAULT_API_KEY.append(first_item)
        return CohereAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or CohereAI.DEFAULT_API_KEY[0]:
            config.cohere_client = ClientV2(api_key=api_key if api_key else CohereAI.getApiKey())
            return config.cohere_client
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
        api_timeout: Optional[int]=None,
        **kwargs,
    ) -> ChatResponse:
        if not api_key and not CohereAI.DEFAULT_API_KEY[0]:
            raise ValueError("Cohere API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else CohereAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            client = CohereAI.getClient(api_key=this_api_key)
            func = client.chat_stream if stream else client.chat
            try:
                completion = func(
                    model=model if model else CohereAI.DEFAULT_MODEL,
                    messages=messages,
                    temperature=temperature if temperature is not None else CohereAI.DEFAULT_TEMPERATURE,
                    max_tokens=max_tokens if max_tokens else CohereAI.DEFAULT_MAX_TOKENS,
                    tools=[{"type": "function", "function": schema}] if schema else None,
                    tool_choice="REQUIRED" if schema else None,
                    strict_tools= True if schema else None,
                    #stream=stream,
                    stop_sequences=stop,
                    request_options=RequestOptions(timeout_in_seconds=api_timeout),
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
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[int]=None,
        **kwargs,
    ) -> dict:
        completion = CohereAI.getChatCompletion(
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
        return json.loads(completion.message.tool_calls[0].function.arguments)
