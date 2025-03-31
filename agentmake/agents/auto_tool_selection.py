"""
automate single tool selection for resolving a simple task.
All available tools are used as the default tool choice.
Users can limit tool options, by declaring selected tools in the prompt.
Use `@` followed by a tool nmae to declare a tool in the prompt.
"""

from agentmake import DEFAULT_AI_BACKEND
from typing import Optional, Union, Any, List, Dict

def auto_tool_selection(
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
        default_tool_choices: str="",
        **kwargs,
) -> Union[List[Dict[str, str]], Any]:
    from agentmake import RAW_SYSTEM_MESSAGE, agentmake, getMultipleTools
    from copy import deepcopy
    import re

    user_request = messages[-1].get("content", "")
    tools, tools_description = getMultipleTools(f"{default_tool_choices+' ' if default_tool_choices else ''}{user_request}", info=True)

    prompt = f"""Recommend which is the best `Tool` that can resolve `My Requests`. Each tool name listed below is prefixed with "@" followed by their descriptions.

{tools_description}

# My Request

{user_request}"""

    print("Running tool selection agent ...\n")
    messages_copy = deepcopy(messages)
    messages_copy[-1]["content"] = prompt
    messages_copy = agentmake(
        messages=messages_copy,
        system="recommend_tool",
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
        **kwargs,
    )
    tool_selection_response = messages_copy[-1].get("content", "")
    if not tool_selection_response:
        return messages
    tool_pattern = "|".join(tools)
    tool_pattern_1 = f"""`@({tool_pattern})`"""
    tool_pattern_2 = f"""{tool_pattern}"""
    selected_tool = ""
    if re.search("THE BEST TOOL FOR RESOLVING THIS REQUEST IS", tool_selection_response, re.IGNORECASE):
        tool_selection_response = re.sub(r"^[\d\D]+?THE BEST TOOL FOR RESOLVING THIS REQUEST IS", "", tool_selection_response, re.IGNORECASE)
        if found_1 := re.search(tool_pattern_1, f"{tool_selection_response} "):
            selected_tool = found_1.group(1)
        elif found_2 := re.search(tool_pattern_2, f"{tool_selection_response} "):
            selected_tool = found_2.group(0)
    else:
        if found_1 := re.findall(tool_pattern_1, f"{tool_selection_response} "):
            selected_tool = found_1[-1]
        elif found_2 := re.findall(tool_pattern_2, f"{tool_selection_response} "):
            selected_tool = found_2[-1]

    if selected_tool:
        print(f"\n```\nTool selected: {selected_tool}\n```")
    else:
        print(f"\n```\nThe provided tools are not suitable for the task!\n```")
        return messages

    return agentmake(
        messages=messages,
        system=RAW_SYSTEM_MESSAGE if selected_tool and not selected_tool == "chat" else "reasoning",
        tool=selected_tool,
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
        **kwargs,
    )

AGENT_FUNCTION = auto_tool_selection