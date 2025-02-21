from agentmake import config
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import codecs, json, os


class GoogleaiAI:

    DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else os.getenv("GOOGLEAI_API_KEY")
    DEFAULT_MODEL = os.getenv("GOOGLEAI_MODEL") if os.getenv("GOOGLEAI_MODEL") else "gemini-1.5-pro"
    DEFAULT_TEMPERATURE = float(os.getenv("GOOGLEAI_TEMPERATURE")) if os.getenv("GOOGLEAI_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("GOOGLEAI_MAX_TOKENS")) if os.getenv("GOOGLEAI_MAX_TOKENS") else 8192 # https://ai.google.dev/gemini-api/docs/models/gemini

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or GoogleaiAI.DEFAULT_API_KEY:
            config.googleai_client = OpenAI(api_key=api_key if api_key else GoogleaiAI.DEFAULT_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai")
            return config.googleai_client
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
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> ChatCompletion:
        if not api_key and not GoogleaiAI.DEFAULT_API_KEY:
            raise ValueError("GoogleAI API key is required.")
        #if not api_endpoint and not GoogleaiAI.DEFAULT_API_ENDPOINT:
        #    raise ValueError("API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        return GoogleaiAI.getClient(api_key=api_key).chat.completions.create(
            model=model if model else GoogleaiAI.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature if temperature is not None else GoogleaiAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else GoogleaiAI.DEFAULT_MAX_TOKENS,
            tools=[{"type": "function", "function": schema}] if schema else None,
            tool_choice={"type": "function", "function": {"name": schema["name"]}} if schema else "none",
            stream=stream,
            #stop=stop,
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
        completion = GoogleaiAI.getChatCompletion(
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
