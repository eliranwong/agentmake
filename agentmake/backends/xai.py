from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json, codecs, os


class XaiLLM:

    DEFAULT_API_KEY = os.getenv("XAI_API_KEY")
    DEFAULT_API_ENDPOINT = "https://api.x.ai/v1"
    DEFAULT_MODEL = "grok-2-latest"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 127999 # visit https://docs.x.ai/docs#models to read about tokens limits. In our latest test, the maximum value accepts 127999.

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
        if not api_key and not XaiLLM.DEFAULT_API_KEY:
            raise ValueError("API key is required.")
        #if not api_endpoint and not XaiLLM.DEFAULT_API_ENDPOINT:
        #    raise ValueError("API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return OpenAI(api_key=api_key if api_key else XaiLLM.DEFAULT_API_KEY, base_url=XaiLLM.DEFAULT_API_ENDPOINT).chat.completions.create(
            model=model if model else XaiLLM.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else XaiLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else XaiLLM.DEFAULT_MAX_TOKENS,
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
            #api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            api_timeout: Optional[float]=None,
            **kwargs,
    ) -> dict:
        completion = XaiLLM.getChatCompletion(
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
        outputMessage = completion.choices[0].message
        if hasattr(outputMessage, "tool_calls") and outputMessage.tool_calls:
            function_arguments = outputMessage.tool_calls[0].function.arguments
            return json.loads(codecs.decode(function_arguments, "unicode_escape"))
        else:
            #print("Failed to output structered data!")
            if hasattr(outputMessage, "content") and outputMessage.content:
                return codecs.decode(outputMessage.content, "unicode_escape")
        return {}
