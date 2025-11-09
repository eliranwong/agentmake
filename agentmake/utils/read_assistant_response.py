from .. import config
from .text_wrapper import TextWrapper, wrapText
from typing import Optional, Any
import threading, traceback, os

def getChatCompletionText(
        backend: str,
        completion: Any,
        stream: Optional[bool]=False,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
        streaming_event: Optional[threading.Event]=None,
    ) -> str:
    if not completion:
        return ""
    stream_openai_reasoning_model = True if stream and backend=="openai" and hasattr(completion, "choices") else False
    if stream and not stream_openai_reasoning_model: # openai reasoning models do not support streaming
        text_output = readStreamingChunks(backend, completion, print_on_terminal, word_wrap, streaming_event)
    else:
        if backend == "anthropic":
            text_output = completion.content[0].text
        elif backend == "cohere":
            text_output = completion.message.content[0].text
        elif backend in ("ollama", "ollamacloud"):
            text_output = completion.message.content
        elif backend in ("azure_any", "github_any"):
            text_output = completion.choices[0].message.content
        elif backend in ("genai", "vertexai"):
            text_output = completion.candidates[0].content.parts[0].text
        elif backend in ("azure", "custom", "deepseek", "github", "googleai", "groq", "llamacpp", "mistral", "openai", "xai"):
            text_output = completion.choices[0].message.content
        if print_on_terminal:
            print(wrapText(text_output) if word_wrap else text_output)
            print()
    return text_output

def closeConnections(backend: str):
    if backend is None:
        backend = os.getenv("DEFAULT_AI_BACKEND") if os.getenv("DEFAULT_AI_BACKEND") else "ollama"
    # close connection
    if backend == "azure" and hasattr(config, "azure_client") and config.azure_client is not None:
        config.azure_client.close()
        config.azure_client = None
    elif backend == "anthropic" and hasattr(config, "anthropic_client") and config.anthropic_client is not None:
        config.anthropic_client.close()
        config.anthropic_client = None
    elif backend == "cohere" and hasattr(config, "cohere_client") and config.cohere_client is not None:
        config.cohere_client._client_wrapper.httpx_client.httpx_client.close()
        config.cohere_client = None
    elif backend == "custom" and hasattr(config, "custom_client") and config.custom_client is not None:
        config.custom_client.close()
        config.custom_client = None
    elif backend == "deepseek" and hasattr(config, "deepseek_client") and config.deepseek_client is not None:
        config.deepseek_client.close()
        config.deepseek_client = None
    elif backend == "github" and hasattr(config, "github_client") and config.github_client is not None:
        config.github_client.close()
        config.github_client = None
    elif backend in ("vertexai", "genai") and hasattr(config, "genai_client") and config.genai_client is not None:
        config.genai_client.close()
        config.genai_client = None
    elif backend == "googleai" and hasattr(config, "googleai_client") and config.googleai_client is not None:
        config.googleai_client.close()
        config.googleai_client = None
    elif backend == "groq" and hasattr(config, "groq_client") and config.groq_client is not None:
        config.groq_client.close()
        config.groq_client = None
    elif backend == "llamacpp" and hasattr(config, "llamacpp_client") and config.llamacpp_client is not None:
        config.llamacpp_client.close()
        config.llamacpp_client = None
    elif backend == "mistral" and hasattr(config, "mistral_client") and config.mistral_client is not None:
        #config.mistral_client.close()
        config.mistral_client = None
    elif backend == "openai" and hasattr(config, "openai_client") and config.openai_client is not None:
        config.openai_client.close()
        config.openai_client = None
    elif backend == "ollama" and hasattr(config, "ollama_client") and config.ollama_client is not None:
        config.ollama_client._client.close()
        config.ollama_client = None
    elif backend == "ollamacloud" and hasattr(config, "ollamacloud_client") and config.ollamacloud_client is not None:
        config.ollamacloud_client._client.close()
        config.ollamacloud_client = None
    elif backend == "xai" and hasattr(config, "xai_client") and config.xai_client is not None:
        config.xai_client.close()
        config.xai_client = None

def readStreamingChunks(
        backend: str,
        completion: Any,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
        streaming_event: Optional[threading.Event]=None,
    ) -> str:
    if isinstance(completion, str):
        # in case of mistral
        return completion
    openai_style = True if backend in ("azure", "azure_any", "custom", "deepseek", "github", "github_any", "googleai", "groq", "llamacpp", "mistral", "openai", "xai") else False
    try:
        text_wrapper = TextWrapper(word_wrap)
        if not streaming_event:
            streaming_event = threading.Event()
        streaming_thread = threading.Thread(target=text_wrapper.streamOutputs, args=(streaming_event, completion, openai_style, print_on_terminal))
        # Start the streaming thread
        streaming_thread.start()
        # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+c' to stop the streaming
        text_wrapper.keyToStopStreaming(streaming_event)
        # when streaming is done or when user press "ctrl+q" or "ctrl+c"
        streaming_thread.join()
    except:
        print(traceback.format_exc())
        return "" # Incomplete streaming
    return text_wrapper.text_output # completion streaming is successful