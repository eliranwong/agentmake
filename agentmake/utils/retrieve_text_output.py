from .text_wrapper import TextWrapper
from typing import Optional, Any
import threading, traceback, shutil, textwrap

def wrapText(content, terminal_width=None):
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns
    return "\n".join([textwrap.fill(line, width=terminal_width) for line in content.split("\n")])

def getChatCompletionText(
        backend: str,
        completion: Any,
        stream: Optional[bool]=False,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
    ) -> str:
    if stream:
        text_output = readStreamingChunks(backend, completion, print_on_terminal, word_wrap)
        # TODO: ensure client connection, e.g. llama.cpp client, is closed properly
    else:
        if backend == "anthropic":
            text_output = completion.content[0].text
        elif backend == "ollama":
            text_output = completion.message.content
        elif backend in ("genai", "vertexai"):
            text_output = completion.candidates[0].content.parts[0].text
        elif backend in ("azure", "custom", "deepseek", "github", "googleai", "groq", "llamacpp", "mistral", "openai", "xai"):
            text_output = completion.choices[0].message.content
        if print_on_terminal:
            print(wrapText(text_output) if word_wrap else text_output)
    return text_output

def readStreamingChunks(
        backend: str,
        completion: Any,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
    ) -> str:
    openai_style = True if backend in ("azure", "custom", "deepseek", "github", "googleai", "groq", "llamacpp", "mistral", "openai", "xai") else False
    try:
        text_wrapper = TextWrapper(word_wrap)
        streaming_event = threading.Event()
        streaming_thread = threading.Thread(target=text_wrapper.streamOutputs, args=(streaming_event, completion, openai_style, print_on_terminal))
        # Start the streaming thread
        streaming_thread.start()
        # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
        text_wrapper.keyToStopStreaming(streaming_event)
        # when streaming is done or when user press "ctrl+q"
        streaming_thread.join()
    except:
        print(traceback.format_exc())
        return "" # Incomplete streaming
    return text_wrapper.text_output # completion streaming is successful