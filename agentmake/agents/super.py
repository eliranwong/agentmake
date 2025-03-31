"""
automates action plan, tool selection, tool use, multiple-step actions, and quality control, for resolving complex tasks.
All available tools are used as the default tool choice.
Users can limit tool options, by declaring selected tools in the prompt.
Use `@` followed by a tool nmae to declare a tool in the prompt.
Read more at https://github.com/eliranwong/letmedoit
"""

from agentmake import DEFAULT_AI_BACKEND
from typing import Optional, Union, Any, List, Dict
import os

def super_agent(
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
        agent_directory: str="super",
        **kwargs,
) -> Union[List[Dict[str, str]], Any]:
    from agentmake import AGENTMAKE_USER_DIR, RAW_SYSTEM_MESSAGE, agentmake, getMultipleTools, updateSystemMessage, exportPlainConversation, getCurrentDateTime
    from copy import deepcopy
    from pathlib import Path
    import json, os, re

    # original user request
    user_request = messages[-1].get("content", "")
    if print_on_terminal:
        print(f"# User request\n{user_request}\n")

    tools, tools_description = getMultipleTools(f"{default_tool_choices+' ' if default_tool_choices else ''}{user_request}", info=True)
    tools_description_string = "\n\n".join(tools_description)

    # remove tools from user_request
    tool_pattern = "|".join(tools)
    tool_pattern_0 = f"""@({tool_pattern})[\n`'" ]"""
    tool_pattern_1 = f"""`@({tool_pattern})`"""
    tool_pattern_2 = f"""{tool_pattern}"""
    if tools:
        user_request = re.sub(tool_pattern_0, "", f"{user_request} ").strip()

    prompt = f"""Provide me with the `Preliminary Action Plan` and the `Measurable Outcome` for resolving `My Request`.
    
# Available Tools
Each tool name listed below is prefixed with "@" followed by their descriptions.

{tools_description_string}

# My Request

{user_request}"""

    if print_on_terminal:
        print("\n# Running Task Resolution Agent ...\n")
    messages_copy = deepcopy(messages)
    messages_copy[-1]["content"] = prompt
    messages_copy = agentmake(
        messages=messages_copy,
        system="create_action_plan",
        input_content_plugin="improve_prompt",
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
    updateSystemMessage(messages_copy, RAW_SYSTEM_MESSAGE)
    ask_for_plan = """Below is my request, please provide me with a preliminary action plan first:

# My Request

"""
    improved_prompt = messages_copy[-2].get("content")
    messages_copy[-2]["content"] = f"""{ask_for_plan}{improved_prompt}"""

    progress_schema = {
        "name": "quality_control",
        "description": "Assess the progress and completion of the task, provide feedback, and suggest next SINGLE step to ensure the task is fully resolved.",
        "parameters": {
            "type": "object",
            "properties": {
                "resolved_or_not": {
                    "type": "string",
                    "description": "answer must be either 'yes' or 'no', indicating whether your original request has been resolved or not.",
                    "enum": ["yes", "no"],
                },
                "comment_on_progress": {
                    "type": "string",
                    "description": "comments to update me on the progress made towards resolving your original request.",
                },
                "suggestions_for_next_step": {
                    "type": "string",
                    "description": "make suggestions for the next SINGLE step based on the results achieved so far. If no further steps are expected once your original request is resolved, suggest closing the conversation.",
                },
                "instruction_for_next_step": {
                    "type": "string",
                    "description": "write the instructions for an AI model to follow in its next SINGLE step.",
                },
            },
            "required": ["resolved_or_not", "comment_on_progress", "suggestions_for_next_step", "instruction_for_next_step"],
        },
    }

    max_round = int(os.getenv("MAXIMUM_ACTION_ROUND")) if os.getenv("MAXIMUM_ACTION_ROUND") else 20
    num_round = 0
    while num_round < max_round:
        """
        1. check progress
        2. select a tool for the next step
        3. refine the next step instruction
        4. execute the next step
        """
        # 1. check progress
        if print_on_terminal:
            print("\n# Running Quality Control Agent ...\n")
        messages_copy = agentmake(
            messages=messages_copy,
            system="quality_control",
            schema=progress_schema,
            follow_up_prompt="What is the progress so far?",
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
        progress_response = json.loads(messages_copy[-1].get("content", ""))
        if (progress_response.get("resolved_or_not", "no").lower() == "yes"):
            comment_on_progress = progress_response.get("comment_on_progress", "")
            suggestions_for_next_step = progress_response.get("suggestions_for_next_step", "")
            messages_copy[-1]["content"] = f"""# Resolved\n\n{comment_on_progress}\n\n{suggestions_for_next_step}"""
            break
        # 2. select a tool for the next step
        instruction_for_next_step = progress_response.get("instruction_for_next_step", "")
        if not instruction_for_next_step:
            continue

        instruction_for_next_step_for_checking = f"""Recommend which is the best `Tool` that can resolve `My Requests`. Each tool name listed below is prefixed with "@" followed by their descriptions.

{tools_description}

# My Request

{instruction_for_next_step}"""

        if print_on_terminal:
            print("\n# Running Tool Recommendation Agent ...\n")
        messages_copy = agentmake(
            messages=messages_copy[:-2],
            system="recommend_tool",
            follow_up_prompt=instruction_for_next_step_for_checking,
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
        selected_tool = None
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
        
        # 3. refine the next step instruction
        if selected_tool:

            if print_on_terminal:
                print("\n# Running Instruction Refinement Agent ...\n")
            tool_instruction_schema = {
                "name": "quality_control",
                "description": "Improve tool instruction",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "improved_instruction_for_next_step": {
                            "type": "string",
                            "description": "Review the requirements of a given tool, refine a provided instruction, and produce a clearer guidance in JSON format for an AI agent to execute the subsequent step using the specified tool.",
                        },
                    },
                    "required": ["improved_instruction_for_next_step"],
                },
            }
            for i in tools_description:
                if i.startswith(f"`@{selected_tool}`"):
                    tool_description = i
                    break
            follow_up_prompt = f"""Review the `Tool Description` of the tool `@{selected_tool}` and refine the `Instruction for Next Step` to provide clearer guidance for an AI agent using the tool `@{selected_tool}` to execute the subsequent step. Provide me with the `improved_instruction_for_next_step` in JSON format in your response.

# Tool Description

{tool_description}

# Instruction for Next Step

{instruction_for_next_step}"""

            messages_copy = agentmake(
                messages=messages_copy[:-2],
                system="tool_instruction",
                schema=tool_instruction_schema,
                follow_up_prompt=follow_up_prompt,
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
            try:
                instruction_for_next_step = json.loads(messages_copy[-1].get("content", instruction_for_next_step)).get("improved_instruction_for_next_step")
            except:
                instruction_for_next_step = messages_copy[-1].get("content", instruction_for_next_step)
            if isinstance(instruction_for_next_step, dict):
                instruction_for_next_step = json.dumps(instruction_for_next_step)
            messages_copy = messages_copy[:-2]

        # 4. execute the next step
        if print_on_terminal:
            print("\n# Executing tool instruction ...\n")
        messages_copy = agentmake(
            messages=messages_copy,
            system=RAW_SYSTEM_MESSAGE if selected_tool and not selected_tool == "chat" else "reasoning",
            follow_up_prompt=instruction_for_next_step,
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

        num_round += 1

    # Save conversation record
    storagePath = os.path.join(AGENTMAKE_USER_DIR, agent_directory, "history")
    Path(storagePath).mkdir(parents=True, exist_ok=True)
    filepath = os.path.join(storagePath, f"{getCurrentDateTime()}.md")
    for i in messages_copy:
        content = i.get("content")
        if content.startswith(ask_for_plan):
            i["content"] = i["content"][len(ask_for_plan):]
            break
    exportPlainConversation(messages_copy, filepath)
    if print_on_terminal:
        print(f"Saving conversation in '{filepath}' ...")
    
    return messages_copy

AGENT_FUNCTION = super_agent