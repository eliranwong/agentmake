"""
LetMeDoIt Lite - automates use of a single tool to resolve a simple task.
Default tool choice: @chat @search/google @files/extract_text @install_python_package @magic
Users can specify additional tool options, by declaring additional tools in the prompt.
Use `@` followed by a tool nmae to declare a tool in the prompt.
Read more at https://github.com/eliranwong/letmedoit
"""

from agentmake import DEFAULT_AI_BACKEND
from typing import Optional, Union, Any, List, Dict

def letmedoit_lite(
        messages: Union[List[Dict[str, str]], str],
        backend: Optional[str]=DEFAULT_AI_BACKEND,
        model: Optional[str]=None,
        model_keep_alive: Optional[str]=None,
        temperature: Optional[float]=None,
        max_tokens: Optional[int]=None,
        context_window: Optional[int]=None,
        batch_size: Optional[int]=None,
        stream: Optional[bool]=False,
        stream_events_only: Optional[bool]=False,
        api_key: Optional[str]=None,
        api_endpoint: Optional[str]=None,
        api_project_id: Optional[str]=None,
        api_service_location: Optional[str]=None,
        api_timeout: Optional[Union[int, float]]=None,
        print_on_terminal: Optional[bool]=True,
        word_wrap: Optional[bool]=True,
        **kwargs,
) -> Union[List[Dict[str, str]], Any]:
    from agentmake.agents.auto_tool_selection import auto_tool_selection
    import os
    DEFAULT_ONLINE_SEARCH_TOOL=os.getenv("DEFAULT_ONLINE_SEARCH_TOOL") if os.getenv("DEFAULT_ONLINE_SEARCH_TOOL") else "search/google"
    return auto_tool_selection(
        messages=messages,
        backend=backend,
        model=model,
        model_keep_alive=model_keep_alive,
        temperature=temperature,
        max_tokens=max_tokens,
        context_window=context_window,
        batch_size=batch_size,
        stream=stream,
        stream_events_only=stream_events_only,
        api_key=api_key,
        api_endpoint=api_endpoint,
        api_project_id=api_project_id,
        api_service_location=api_service_location,
        api_timeout=api_timeout,
        print_on_terminal=print_on_terminal,
        word_wrap=word_wrap,
        default_tool_choices=os.getenv("DEFAULT_TOOL_CHOICES") if os.getenv("DEFAULT_TOOL_CHOICES") else f"@{DEFAULT_ONLINE_SEARCH_TOOL} @chat @files/extract_text @install_python_package @magic",
        **kwargs,
    )

AGENT_FUNCTION = letmedoit_lite