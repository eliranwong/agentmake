from agentmake import config
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional
import traceback
import json
import os

DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False

class GithubAI:

    DEFAULT_API_KEY = os.getenv("GITHUB_API_KEY").split(",") if os.getenv("GITHUB_API_KEY") else [""]
    DEFAULT_MODEL = os.getenv("GITHUB_MODEL") if os.getenv("GITHUB_MODEL") else "gpt-4o"
    DEFAULT_TEMPERATURE = float(os.getenv("GITHUB_TEMPERATURE")) if os.getenv("GITHUB_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("GITHUB_MAX_TOKENS")) if os.getenv("GITHUB_MAX_TOKENS") else 4000 # https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits

    @staticmethod
    def getApiKey():
        # rotate multiple API keys
        if len(GithubAI.DEFAULT_API_KEY) > 1:
            first_item = GithubAI.DEFAULT_API_KEY.pop(0)
            GithubAI.DEFAULT_API_KEY.append(first_item)
        return GithubAI.DEFAULT_API_KEY[0]

    @staticmethod
    def getClient(api_key: Optional[str]=None):
        if api_key or GithubAI.DEFAULT_API_KEY[0]:
            config.github_client = OpenAI(api_key=api_key if api_key else GithubAI.getApiKey(), base_url="https://models.inference.ai.azure.com")
            return config.github_client
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
        if not api_key and not GithubAI.DEFAULT_API_KEY[0]:
            raise ValueError("Github API key is required.")
        #if not api_endpoint and not GithubAI.DEFAULT_API_ENDPOINT:
        #    raise ValueError("API endpoint is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        completion = None
        used_api_keys = []
        while completion is None:
            this_api_key = api_key if api_key else GithubAI.getApiKey()
            if this_api_key in used_api_keys:
                break
            else:
                used_api_keys.append(this_api_key)
            try:
                completion = GithubAI.getClient(api_key=this_api_key).chat.completions.create(
                    model=model if model else GithubAI.DEFAULT_MODEL,
                    messages=messages,
                    temperature=temperature if temperature is not None else GithubAI.DEFAULT_TEMPERATURE,
                    max_tokens=max_tokens if max_tokens else GithubAI.DEFAULT_MAX_TOKENS,
                    tools=[{"type": "function", "function": schema}] if schema else None,
                    tool_choice={"type": "function", "function": {"name": schema["name"]}} if schema else None,
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
        #prefill: Optional[str]=None,
        stop: Optional[list]=None,
        api_key: Optional[str]=None, # api key for backends that require one; enter credentials json file path if using Vertex AI
        #api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> dict:
        completion = GithubAI.getChatCompletion(
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
        return json.loads(completion.choices[0].message.tool_calls[0].function.arguments)
