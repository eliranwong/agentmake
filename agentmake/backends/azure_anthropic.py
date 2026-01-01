from agentmake import config
from anthropic import Anthropic, NOT_GIVEN
from anthropic import AnthropicFoundry
from anthropic.types import Message
from typing import Optional
from copy import deepcopy
import os


class AzureAnthropicAI:
    # docs: https://docs.anthropic.com/en/home
    DEFAULT_API_VERSION = os.getenv("AZURE_ANTHROPIC_API_VERSION") if os.getenv("AZURE_ANTHROPIC_API_VERSION") else "2024-10-21" # check the latest api version at https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#data-plane-inference
    DEFAULT_API_KEY = os.getenv("AZURE_ANTHROPIC_API_KEY") if os.getenv("AZURE_ANTHROPIC_API_KEY") else ""
    DEFAULT_API_ENDPOINT = os.getenv("AZURE_ANTHROPIC_API_ENDPOINT") if os.getenv("AZURE_ANTHROPIC_API_ENDPOINT") else ""
    DEFAULT_MODEL = os.getenv("AZURE_ANTHROPIC_MODEL") if os.getenv("AZURE_ANTHROPIC_MODEL") else "claude-sonnet-4-5"
    DEFAULT_TEMPERATURE = float(os.getenv("AZURE_ANTHROPIC_TEMPERATURE")) if os.getenv("AZURE_ANTHROPIC_TEMPERATURE") else 0.3
    DEFAULT_MAX_TOKENS = int(os.getenv("AZURE_ANTHROPIC_MAX_TOKENS")) if os.getenv("AZURE_ANTHROPIC_MAX_TOKENS") else 8192

    @staticmethod
    def getClient(api_key: Optional[str]=None, api_endpoint: Optional[str]=None):
        if api_key or AzureAnthropicAI.DEFAULT_API_KEY:
            config.azure_anthropic_client = AnthropicFoundry(
                api_key=api_key if api_key else AzureAnthropicAI.DEFAULT_API_KEY,
                base_url=api_endpoint if api_endpoint else AzureAnthropicAI.DEFAULT_API_ENDPOINT,
            )
            return config.azure_anthropic_client
        return None

    @staticmethod
    def removeSystemMessage(messages: list) -> str:
        for index, message in enumerate(messages):
            if message.get("role", "") == "system":
                return messages.pop(index).get("content", "")
        return ""

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
        api_endpoint: Optional[str]=None,
        #api_project_id: Optional[str]=None, # applicable to Vertex AI only
        #api_service_location: Optional[str]=None, # applicable to Vertex AI only
        api_timeout: Optional[float]=None,
        **kwargs,
    ) -> Message:
        if not api_key and not AzureAnthropicAI.DEFAULT_API_KEY:
            raise ValueError("Anthropic API key is required.")
        #if prefill:
        #    messages.append({'role': 'assistant', 'content': prefill})
        if schema:
            schema["input_schema"] = schema.pop("parameters")
        messagesCopy = deepcopy(messages)
        systemMessage = AzureAnthropicAI.removeSystemMessage(messagesCopy)
        return AzureAnthropicAI.getClient(api_key=api_key, api_endpoint=api_endpoint).messages.create(
            model=model if model else AzureAnthropicAI.DEFAULT_MODEL,
            messages=messagesCopy,
            system=systemMessage,
            temperature=temperature if temperature is not None else AzureAnthropicAI.DEFAULT_TEMPERATURE,
            max_tokens=max_tokens if max_tokens else AzureAnthropicAI.DEFAULT_MAX_TOKENS,
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
        completion = AzureAnthropicAI.getChatCompletion(
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
