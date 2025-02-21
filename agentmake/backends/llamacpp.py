from agentmake import config
from ..utils.schema import getParameterSchema
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import json
import os


class LlamacppAI:

    # example command to run a llama.cpp server
    # ./llama-server --host 127.0.0.1 --port 8080 --threads $(lscpu | grep '^Core(s)' | awk '{print $NF}') --ctx-size 0 --chat-template chatml --parallel 2 --gpu-layers 999 --model 'llm.gguf'

    DEFAULT_API_ENDPOINT = os.getenv("LLAMACPP_API_ENDPOINT") if os.getenv("LLAMACPP_API_ENDPOINT") else "http://127.0.0.1:8080/v1"
    DEFAULT_TEMPERATURE = float(os.getenv("LLAMACPP_TEMPERATURE")) if os.getenv("LLAMACPP_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("LLAMACPP_MAX_TOKENS")) if os.getenv("LLAMACPP_MAX_TOKENS") else 2048

    @staticmethod
    def getClient(api_endpoint: Optional[str]=None):
        if api_endpoint or LlamacppAI.DEFAULT_API_ENDPOINT:
            config.llamacpp_client = OpenAI(api_key="agentmake", base_url=api_endpoint if api_endpoint else LlamacppAI.DEFAULT_API_ENDPOINT)
            return config.llamacpp_client
        return None

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
        return LlamacppAI.getClient(api_endpoint=api_endpoint).chat.completions.create(
            model="agentmake", # specify a model in the command line running llama.cpp
            messages=messages,
            temperature=temperature if temperature is not None else LlamacppAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else LlamacppAI.DEFAULT_MAX_TOKENS,
            response_format={
                "type": "json_object",
                "schema": getParameterSchema(schema),
            } if schema else None,
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
        completion = LlamacppAI.getChatCompletion(
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
