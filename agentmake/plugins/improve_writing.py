from agentmake import generate, DEFAULT_AI_BACKEND
from typing import Optional, Union, List
import os, json

WRITING_STYLE = os.getenv('WRITING_STYLE') if os.getenv('WRITING_STYLE') else 'standard English'

TOOL_SYSTEM = f"""# Role
You are an excellent writer.

# Job description
Your job is to improve my writing sytle only, without extra comments or explantions.

# Expertise
Your expertise lies in proofreading and improving my writing.

# Instruction
You improve the writing in the user's input, according to {WRITING_STYLE}.
Remember, do NOT give me extra comments explanations.  I want only the 'improved_writing'"""

TOOL_SCHEMA = {
    "name": "improve_writing",
    "description": f"Improve user writing, according to {WRITING_STYLE}",
    "parameters": {
        "type": "object",
        "properties": {
            "improved_writing": {
                "type": "string",
                "description": "The improved version of my writing",
            },
        },
        "required": ["improved_writing"],
    },
}

def improve_writing(
    content,
    backend: Optional[str]=DEFAULT_AI_BACKEND,
    model: Optional[str]=None,
    model_keep_alive: Optional[str]=None,
    temperature: Optional[float]=None,
    max_tokens: Optional[int]=None,
    context_window: Optional[int]=None,
    batch_size: Optional[int]=None,
    prefill: Optional[Union[List[Optional[str]], str]]=None,
    stop: Optional[list]=None,
    stream: Optional[bool]=False,
    api_key: Optional[str]=None,
    api_endpoint: Optional[str]=None,
    api_project_id: Optional[str]=None,
    api_service_location: Optional[str]=None,
    api_timeout: Optional[Union[int, float]]=None,
    print_on_terminal: Optional[bool]=True,
    word_wrap: Optional[bool]=True,
    **kwargs,
):
    messages = generate(
        content,
        system=TOOL_SYSTEM,
        schema=TOOL_SCHEMA,
        backend=backend,
        model=model,
        model_keep_alive=model_keep_alive,
        temperature=temperature,
        max_tokens=max_tokens,
        context_window=context_window,
        batch_size=batch_size,
        prefill=prefill,
        stop=stop,
        stream=stream,
        api_key=api_key,
        api_endpoint=api_endpoint,
        api_project_id=api_project_id,
        api_service_location=api_service_location,
        api_timeout=api_timeout,
        print_on_terminal=print_on_terminal,
        word_wrap=word_wrap,
        **kwargs,
    )
    improved_writing = json.loads(messages[-1]["content"])["improved_writing"]
    return improved_writing

CONTENT_PLUGIN = improve_writing