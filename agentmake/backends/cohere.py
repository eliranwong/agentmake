import cohere
from cohere import ChatResponse
from cohere.core.request_options import RequestOptions
from typing import Optional
import json, os


class CohereAI:

    DEFAULT_API_KEY = os.getenv("COHERE_API_KEY")
    DEFAULT_MODEL = os.getenv("COHERE_MODEL") if os.getenv("COHERE_MODEL") else "command-r-plus" # https://docs.cohere.com/docs/models
    DEFAULT_TEMPERATURE = float(os.getenv("COHERE_TEMPERATURE")) if os.getenv("COHERE_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("COHERE_MAX_TOKENS")) if os.getenv("COHERE_MAX_TOKENS") else 4000 # https://docs.cohere.com/docs/rate-limits

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
        if not api_key and not CohereAI.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        client = cohere.ClientV2(api_key=api_key if api_key else CohereAI.DEFAULT_API_KEY)
        func = client.chat_stream if stream else client.chat
        return func(
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
