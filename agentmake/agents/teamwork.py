"""
TeamGen AI, developed by [Eliran Wong](https://github.com/eliranwong), automates creation of a team of AI agents that work collaborately to address user requests.

Modify from source: https://github.com/eliranwong/teamgenai
"""

from agentmake import DEFAULT_AI_BACKEND
from typing import Optional, Union, Any, List, Dict

def teamwork(
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

    from agentmake import DEFAULT_TEXT_EDITOR, PACKAGE_PATH, AGENTMAKE_USER_DIR, DEFAULT_FOLLOW_UP_PROMPT, DEVELOPER_MODE, agentmake, readTextFile, showErrors, writeTextFile, getCurrentDateTime
    from pathlib import Path
    from copy import deepcopy
    import re, os

    def generate_teamwork_record(backend, messages, userRequest, agents, agents_description, print_on_terminal):
        timestamp = getCurrentDateTime()
        storagePath = os.path.join(AGENTMAKE_USER_DIR, "teamwork", timestamp)
        Path(storagePath).mkdir(parents=True, exist_ok=True)
        if print_on_terminal:
            print()
            print("# User Request Resolved")
        agents_description_file = os.path.join(storagePath, "agents_configurations.py")
        if print_on_terminal:
            print(f"Saving agents' configurations in '{agents_description_file}' ...")
        writeTextFile(agents_description_file, str(agents))
        agents_discussion_file = os.path.join(storagePath, "agents_discussion.py")
        if print_on_terminal:
            print(f"Saving agents discussion in '{agents_discussion_file}' ...")
        writeTextFile(agents_discussion_file, str(messages))
        plain_record_file = os.path.join(storagePath, "plain_record.md")
        plain_record = f"""# Datetime

{timestamp}

# AI Backend

{backend}

# User Request

{userRequest}

# Agents Generated

{agents_description}

# Agents Discussion
"""
        for i in messages:
            role = i.get("role", "")
            content = i.get("content", "")
            if content:
                plain_record += f"""
```{role}
{content}
```
"""
        print(f"Saving plain record in '{plain_record_file}' ...")
        writeTextFile(plain_record_file, plain_record)
        print("Done!")
        try:
            os.system(f'''{DEFAULT_TEXT_EDITOR} "{plain_record_file}"''')
        except Exception as e:
            showErrors(e)

    # set initial message chain
    if isinstance(messages, str):
        userRequest = messages
        messages = [{"role": "system", "content": ""}, {"role": "user", "content": userRequest}]
    elif messages[-1].get("role", "") == "user":
        userRequest = messages[-1].get("content", "")
    else:
        userRequest = DEFAULT_FOLLOW_UP_PROMPT

    messages_copy = deepcopy(messages)

    if print_on_terminal:
        print("# Running TeamGen AI ...\n")
        print(f"# AI Backend\n{backend} ({model})\n" if model else f"# AI Backend\n{backend}\n")

        # display user request
        print(f"# User request\n{userRequest}\n")

    # agent configurations
    messages_copy = agentmake(
        messages_copy,
        system="create_agents",
        input_content_plugin="improve_prompt",
        backend=backend,
        model=model,
        model_keep_alive=model_keep_alive,
        temperature=temperature,
        max_tokens=max_tokens,
        context_window=context_window,
        batch_size=batch_size,
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
    
    # update user request with improved prompt
    userRequest = messages_copy[-2].get("content", "")
    
    # extract agent information
    create_agents_response = messages_copy[-1].get("content", "")
    create_agents_response = re.sub("```\n[Aa]gent", "```agent", create_agents_response)
    create_agents_response = re.sub("^[#]+? [Aa]gent", "```agent", create_agents_response, flags=re.M)
    agents = [i.rstrip() for i in create_agents_response.split("```") if re.search("^agent [0-9]", i)]
    if not agents:
        if DEVELOPER_MODE:
            print(f"Agents not found in:\n\n{create_agents_response}")
        else:
            print("Agents not found!")
        return messages
    notCalled = [i for i in range(1, len(agents)+1)] # a list of agents that haven't been called
    
    # update the last message
    messages_copy[-1]["content"] = "# Progress\n\nA team of AI agents has been created to resolve your requests, and they are waiting for your call to contribute in turn."

    # agent description
    agents_description = "```" + "\n```\n\n```".join(agents) + "\n```"
    if print_on_terminal:
        print("# Agents Generated")
        print(agents_description, "\n")

    # Agent assignment
    possible_system_file_path_2 = os.path.join(PACKAGE_PATH, "systems", "assign_agents.md")
    possible_system_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "systems", "assign_agents.md")
    assign_agents_system = readTextFile(possible_system_file_path_2 if os.path.isfile(possible_system_file_path_2) else possible_system_file_path_1).format(userRequest, agents_description)

    agent = 1

    while len(agents) >= agent > 0:

        messages_copy = agentmake(
            messages_copy,
            system=assign_agents_system,
            follow_up_prompt="Who is the best agent to contribute next?",
            backend=backend,
            model=model,
            model_keep_alive=model_keep_alive,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
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

        assign_agents_response = messages_copy[-1].get("content", "")
        if print_on_terminal:
            print("# Assignment")
            print(assign_agents_response, "\n")

        p = r"The best agent to contribute next is agent ([0-9]+?)[^0-9]"
        if found := re.search(p, assign_agents_response):
            agent = int(found.group(1))
            if agent > len(agents):
                agent = 0
            elif agent in notCalled:
                notCalled.remove(agent)
        elif notCalled:
            agent = notCalled.pop(0)
        else:
            agent = 0
        if agent == 0 and notCalled:
            agent = notCalled.pop(0)
        if agent == 0:
            break

        agent_system = re.sub("^agent [0-9]+?\n", "", agents[agent - 1]).replace("##", "#") + f"""# User request
{userRequest}
# Instruction
1. Examine carefully what has been done or dicussed so far toward resolving the user request and think about what is the best to do next.
2. On top of what has been done or discussed, contribute your expertise to work toward resolving the user request."""
        try:
            agent_role = re.search("""# Role(.+?)# Job description""", agent_system, re.DOTALL).group(1).strip()
        except:
            agent_role = f"Agent {agent}"
        agent_role = re.sub("^You are (a|an|the) (.*?)[.]*$", r"\2", agent_role)

        if print_on_terminal:
            print(f"# Calling Agent {agent} ...")
            print(agent_system, "\n")

        messages_copy = agentmake(
            messages_copy,
            system=agent_system,
            follow_up_prompt=f'''# Change Speaker\nThe best agent to contribute next is agent {agent}.\n{agent_role}, it is your turn to contribute.''',
            backend=backend,
            model=model,
            model_keep_alive=model_keep_alive,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
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

    # Conclusion
    messages_copy = agentmake(
        messages_copy,
        system="write_final_answer",
        follow_up_prompt=f"""# Instruction
Please provide me with the final answer to my original request based on the work that has been completed.

# Original Request
{userRequest}""",
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

    # backup before closing
    if not (stream and stream_events_only):
        generate_teamwork_record(backend, messages_copy, userRequest, agents, agents_description, print_on_terminal)
    if print_on_terminal:
        print("# Closing TeamGen AI ...\n")
    
    return messages_copy

AGENT_FUNCTION = teamwork