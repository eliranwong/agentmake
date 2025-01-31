from anthropic import Anthropic, NOT_GIVEN
from anthropic.types import Message
from typing import Optional
import os


class AnthropicLLM:
    # docs: https://docs.anthropic.com/en/home

    DEFAULT_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DEFAULT_MODEL = "claude-3-5-sonnet-latest"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 8192 # https://docs.mistral.ai/getting-started/models/models_overview/

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
    ) -> Message:
        if not api_key and not AnthropicLLM.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        if schema:
            schema["input_schema"] = schema.pop("parameters")
        return Anthropic(api_key=api_key if api_key else AnthropicLLM.DEFAULT_API_KEY).messages.create(
            model=model if model else AnthropicLLM.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else AnthropicLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else AnthropicLLM.DEFAULT_MAX_TOKENS,
            tools=[schema] if schema else NOT_GIVEN,
            tool_choice={"type": "tool", "name": schema["name"]} if schema else NOT_GIVEN,
            stream=stream,
            stop_sequences=stop,
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
            #api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            api_timeout: Optional[float]=None,
            **kwargs,
    ) -> dict:
        completion = AnthropicLLM.getChatCompletion(
            messages,
            model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            api_key=api_key,
            #api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
        outputDictionary = {}
        for i in completion.content:
            if hasattr(i, "input"):
                outputDictionary = i.input
                break
        return outputDictionary
