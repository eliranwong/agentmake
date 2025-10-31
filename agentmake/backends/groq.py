from agentmake import config
from groq import Groq
from groq.types.chat.chat_completion import ChatCompletion
from typing import Optional
import traceback
import json
import os

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class GroqAI:

    DEFAULT_API_KEY = os.getenv("GROQ_API_KEY").split(",") if os.getenv("GROQ_API_KEY") else [""]
    DEFAULT_MODEL = os.getenv("GROQ_MODEL") if os.getenv("GROQ_MODEL") else "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE")) if os.getenv("GROQ_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS")) if os.getenv("GROQ_MAX_TOKENS") else 32768 # https://console.groq.com/docs/models

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(GroqAI.DEFAULT_API_KEY) > 1:
            first_item = GroqAI.DEFAULT_API_KEY.pop(0)
            GroqAI.DEFAULT_API_KEY.append(first_item)
        return GroqAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or GroqAI.DEFAULT_API_KEY[0]:
            config.groq_client = Groq(api_key=api_key if api_key else GroqAI.getApiKey())
            return config.groq_client
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
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> ChatCompletion:
        if not api_key and not GroqAI.DEFAULT_API_KEY[0]:
            raise ValueError("Groq API key is required.")
        if prefill:
            messages.append({'role': 'assistant', 'content': prefill})
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else GroqAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                if schema:
                    if "code" in schema["parameters"]["properties"]:
                        schema["parameters"]["properties"]["code"]["description"] += " Ensure the code includes all necessary import statements."
                    '''# Structured output; supported by selected models only
                    parameters = schema["parameters"]
                    parameters["additionalProperties"] = False
                    schema = {
                        "name": schema["name"],
                        "schema": parameters,
                    }
                    completion = GroqAI.getClient(api_key=this_api_key).chat.completions.create(
                        model=model if model else GroqAI.DEFAULT_MODEL,
                        messages=messages,
                        temperature=temperature if temperature is not None else GroqAI.DEFAULT_TEMPERATURE,
                        max_tokens=max_tokens if max_tokens else GroqAI.DEFAULT_MAX_TOKENS,
                        response_format={
                            "type": "json_schema",
                            "json_schema": schema,
                        },
                        stream=stream,
                        stop=stop,
                        timeout=api_timeout,
                        **kwargs
                    )'''
                    completion = GroqAI.getClient(api_key=this_api_key).chat.completions.create(
                        model=model if model else GroqAI.DEFAULT_MODEL,
                        messages=messages,
                        temperature=temperature if temperature is not None else GroqAI.DEFAULT_TEMPERATURE,
                        max_tokens=max_tokens if max_tokens else GroqAI.DEFAULT_MAX_TOKENS,
                        tools=[{"type": "function", "function": schema}],
                        #tool_choice={"type": "function", "function": {"name": schema["name"]}}, # inconsistant; doesn't work sometimes
                        tool_choice="auto",
                        stream=stream,
                        stop=stop,
                        timeout=api_timeout,
                        **kwargs
                    )
                else:
                    completion = GroqAI.getClient(api_key=this_api_key).chat.completions.create(
                        model=model if model else GroqAI.DEFAULT_MODEL,
                        messages=messages,
                        temperature=temperature if temperature is not None else GroqAI.DEFAULT_TEMPERATURE,
                        max_tokens=max_tokens if max_tokens else GroqAI.DEFAULT_MAX_TOKENS,
                        stream=stream,
                        stop=stop,
                        timeout=api_timeout,
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
        if content:= completion.choices[0].message.content:
            if required := schema["parameters"]["required"]:
                dictionary_output = {}
                dictionary_output[required[0]] = content
                for i in range(1,len(required)):
                    dictionary_output[required[i]] = ""
                return dictionary_output
            else:
                return {}
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
