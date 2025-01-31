from ..utils.online import get_local_ip
from ..utils.schema import getParameterSchema
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai import NotGiven
from typing import Optional
import json


class LlamacppLLM:

    DEFAULT_API_ENDPOINT = f"http://{get_local_ip()}:8080/v1"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 2048

    @staticmethod
    def getChatCompletion(
            messages: list,
            #model: Optional[str]=None,
            schema: Optional[dict]=None,
            temperature: Optional[float]=None,
            max_tokens: Optional[int]=None,
            #context_window: Optional[int]=None, # applicable to ollama only
            #batch_size: Optional[int]=None, # applicable to ollama only
            #prefill: Optional[str]=None,
            stop: Optional[list]=None,
            stream: Optional[bool]=False,
            #api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
            api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            api_timeout: Optional[float]=None,
            **kwargs,
    ) -> ChatCompletion:
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return OpenAI(api_key="agentmake", base_url=api_endpoint if api_endpoint else LlamacppLLM.DEFAULT_API_ENDPOINT).chat.completions.create(
            model="agentmake",
            messages=messages,
            temperature=temperature if temperature is not None else LlamacppLLM.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else LlamacppLLM.DEFAULT_MAX_TOKENS,
            response_format={
                "type": "json_object",
                "schema": getParameterSchema(schema),
            } if schema else NotGiven,
            stream=stream,
            stop=stop,
            timeout=api_timeout,
            **kwargs
        )

    @staticmethod
    def getDictionaryOutput(
            messages: list,
            schema: dict,
            #model: Optional[str]=None,
            temperature: Optional[float]=None, 
            max_tokens: Optional[int]=None,
            #context_window: Optional[int]=None, # applicable to ollama only
            #batch_size: Optional[int]=None, # applicable to ollama only
            #prefill: Optional[str]=None,
            stop: Optional[list]=None,
            #api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
            api_endpoint: Optional[str]=None,
            #api_project_id: Optional[str]=None, # applicable to Vertex AI only
            #api_service_location: Optional[str]=None, # applicable to Vertex AI only
            api_timeout: Optional[float]=None,
            **kwargs,
    ) -> dict:
        completion = LlamacppLLM.getChatCompletion(
            messages,
            #model=model,
            schema=schema,
            temperature=temperature,
            max_tokens=max_tokens,
            #prefill=prefill,
            stop=stop,
            #api_key=api_key,
            api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
        return json.loads(completion.choices[0].message.content)
