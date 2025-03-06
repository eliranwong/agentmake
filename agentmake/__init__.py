from dotenv import load_dotenv
import os, shutil, getpass

PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
AGENTMAKE_USER_DIR = os.getenv("AGENTMAKE_USER_DIR") if os.getenv("AGENTMAKE_USER_DIR") else os.path.join(os.path.expanduser("~"), "agentmake") # It is where users store their custom components, i.e. `tools`, `agents`, `plugins`, `systems`, `instructions`, and `prompts`.Custom components are placed outside the package directory, to avoid overriding upon upgrades.

def load_configurations(env_file=""):
    if not env_file:
        backup_env = os.path.join(AGENTMAKE_USER_DIR, "agentmake.env")
        if os.path.isfile(backup_env):
            env_file = backup_env
        else:
            default_env_file = os.path.join(PACKAGE_PATH, ".env")
            if not os.path.isfile(default_env_file):
                shutil.copy(os.path.join(PACKAGE_PATH, "agentmake.env"), default_env_file)
            env_file = default_env_file
    if os.path.isfile(env_file):
        load_dotenv(env_file)
load_configurations()

from .backends.anthropic import AnthropicAI
from .backends.azure import AzureAI
from .backends.cohere import CohereAI
from .backends.custom import OpenaiCompatibleAI
from .backends.deepseek import DeepseekAI
from .backends.genai import GenaiAI
from .backends.github import GithubAI
from .backends.googleai import GoogleaiAI
from .backends.groq import GroqAI
from .backends.llamacpp import LlamacppAI
from .backends.mistral import MistralAI
from .backends.ollama import OllamaAI
from .backends.openai import OpenaiAI
from .backends.xai import XaiAI

from .utils.rag import getRagPrompt
from .utils.read_assistant_response import getChatCompletionText, closeConnections
from .utils.handle_text import readTextFile, writeTextFile
from .utils.system import getCurrentDateTime

from typing import Optional, Callable, Union, Any, List, Dict
from io import StringIO
from markitdown import MarkItDown
from pathlib import Path
from copy import deepcopy
import sys, re, platform, atexit, json, traceback

AGENTMAKE_ASSISTANT_NAME = os.getenv("AGENTMAKE_ASSISTANT_NAME") if os.getenv("AGENTMAKE_ASSISTANT_NAME") else "AI"
AGENTMAKE_USERNAME = os.getenv("AGENTMAKE_USERNAME") if os.getenv("AGENTMAKE_USERNAME") else getpass.getuser().capitalize()
USER_OS = platform.system()
DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") and os.getenv("DEVELOPER_MODE").upper() == "TRUE" else False
SUPPORTED_AI_BACKENDS = ["anthropic", "azure", "cohere", "custom", "deepseek", "genai", "github", "googleai", "groq", "llamacpp", "mistral", "ollama", "openai", "vertexai", "xai"]
DEFAULT_AI_BACKEND = os.getenv("DEFAULT_AI_BACKEND") if os.getenv("DEFAULT_AI_BACKEND") else "ollama"
RAW_SYSTEM_MESSAGE = f"You are my personal AI assistant. I am your user, {AGENTMAKE_USERNAME}. I will give you both text-based and non-text-based tasks, and the necessary tools to resolve my requests. Therefore, do not tell me that you are only a text-based language model. Try your best to resolve my requests. Do not address my name more than once in a single conversation unless I request it."
DEFAULT_SYSTEM_MESSAGE = os.getenv("DEFAULT_SYSTEM_MESSAGE") if os.getenv("DEFAULT_SYSTEM_MESSAGE") else RAW_SYSTEM_MESSAGE
DEFAULT_FOLLOW_UP_PROMPT = os.getenv("DEFAULT_FOLLOW_UP_PROMPT") if os.getenv("DEFAULT_FOLLOW_UP_PROMPT") else "Please tell me more."
DEFAULT_TEXT_EDITOR = os.getenv("DEFAULT_TEXT_EDITOR") if os.getenv("DEFAULT_TEXT_EDITOR") else "etextedit"
DEFAULT_MARKDOWN_THEME = os.getenv("DEFAULT_MARKDOWN_THEME") if os.getenv("DEFAULT_MARKDOWN_THEME") else "github-dark"
DEFAULT_FABRIC_PATTERNS_PATH = os.getenv("DEFAULT_FABRIC_PATTERNS_PATH") if os.getenv("DEFAULT_FABRIC_PATTERNS_PATH") else os.path.join(os.path.expanduser("~"), ".config", "fabric", "patterns")

def override_DEFAULT_SYSTEM_MESSAGE(system_instruction):
    # override default system message without changing the environment variable
    global DEFAULT_SYSTEM_MESSAGE
    DEFAULT_SYSTEM_MESSAGE = system_instruction

def override_DEFAULT_FOLLOW_UP_PROMPT(prompt):
    # override default follow-up prompt without changing the environment variable
    global DEFAULT_FOLLOW_UP_PROMPT
    DEFAULT_FOLLOW_UP_PROMPT = refine_follow_up_prompt_content(prompt)

def edit_configurations(env_file=""):
    if not env_file:
        user_env = os.path.join(AGENTMAKE_USER_DIR, "agentmake.env")
        env_file = user_env if os.path.isfile(user_env) else os.path.join(PACKAGE_PATH, ".env")
    os.system(f'''{DEFAULT_TEXT_EDITOR} "{env_file}"''')
    # reload
    load_configurations()

def agentmake(
    messages: Union[List[Dict[str, str]], str], # user request or messages containing user request; accepts either a single string or a list of dictionaries
    backend: Optional[str]=DEFAULT_AI_BACKEND, # AI backend; check SUPPORTED_AI_BACKENDS for supported backends
    model: Optional[str]=None, # AI model name; applicable to all backends, execept for llamacpp
    model_keep_alive: Optional[str]=None, # time to keep the model loaded in memory; applicable to ollama only
    system: Optional[Union[List[Optional[str]], str]]=None, # system message; define how the model should generally behave and respond; accepts a list of strings or a single string; loop through multiple system messages for multi-turn inferences if it is a list
    instruction: Optional[Union[List[Optional[str]], str]]=None, # predefined instruction, being added to the user prompt as prefix; accepts a list of strings or a single string; loop through multiple predefined instructions for multi-turn inferences if it is a list
    follow_up_prompt: Optional[Union[List[str], str]]=None, # follow-up prompts after an assistant message is generated; accepts a list of strings or a single string; loop through multiple follow-up prompts for multi-turn inferences if it is a list
    input_content_plugin: Optional[Union[List[Optional[str]], str]]=None, # plugin that works on user input; accepts a list of strings or a single string; loop through multiple follow-up prompts for multi-turn inferences if it is a list
    output_content_plugin: Optional[Union[List[Optional[str]], str]]=None, # plugin that works on assistant output; accepts a list of strings or a single string; loop through multiple follow-up prompts for multi-turn inferences if it is a list
    agent: Optional[Union[List[Optional[str]], str]]=None,
    tool: Optional[Union[List[Optional[str]], str]]=None, # a tool either a built-in tool name under the folder `tools` in the package directory or a file path of the tool; accepts a list of strings or a single string; loop through multiple tools for multi-turn actions if it is a list; parameters of both `schema` and `func` are ignored when `tool` parameter is given
    schema: Optional[dict]=None, # json schema for structured output or function calling
    func: Optional[Callable[..., Optional[str]]]=None, # function to be called
    temperature: Optional[float]=None, # temperature for sampling
    max_tokens: Optional[int]=None, # maximum number of tokens to generate
    context_window: Optional[int]=None, # context window size; applicable to ollama only
    batch_size: Optional[int]=None, # batch size; applicable to ollama only
    prefill: Optional[Union[List[Optional[str]], str]]=None, # prefill of assistant message; applicable to deepseek, mistral, ollama and groq only; accepts a list of strings or a single string; loop through multiple prefills for multi-turn inferences if it is a list
    stop: Optional[list]=None, # stop sequences
    stream: Optional[bool]=False, # stream partial message deltas as they are available
    stream_events_only: Optional[bool]=False, # return streaming events object only
    api_key: Optional[str]=None, # API key or credentials json file path in case of using Vertex AI as backend; applicable to anthropic, custom, deepseek, genai, github, googleai, groq, mistral, openai, xai
    api_endpoint: Optional[str]=None, # API endpoint; applicable to azure, custom, llamacpp, ollama
    api_project_id: Optional[str]=None, # project id; applicable to Vertex AI only, i.e., vertexai or genai
    api_service_location: Optional[str]=None, # cloud service location; applicable to Vertex AI only, i.e., vertexai or genai
    api_timeout: Optional[Union[int, float]]=None, # timeout for API request; applicable to all backends, execept for ollama
    print_on_terminal: Optional[bool]=True, # print output on terminal
    word_wrap: Optional[bool]=True, # word wrap output according to current terminal width
    **kwargs, # pass extra options supported by individual backends
) -> Union[List[Dict[str, str]], Any]:
    """
    Generate AI assistant response.

    Args:
        messages:
            type: Union[List[Dict[str, str]], str]
            user request or messages containing user request
            accepts either a single string or a list of dictionaries
            use a single string string to specify user request without chat history
            use a list of dictionaries to provide with the onging interaction between user and assistant
            when a list is given:
                each dictionary in the list should contain keys `role` and `content`
                specify the latest user request in the last item content
                list format example:
                    [
                        {"role": "system", "You are an AI assistant."},
                        {"role": "user", "Hello!"},
                        {"role": "assistant", "Hello! How can I assist you today?"},
                        {"role": "user", "What is generative AI?"}
                    ]
            remarks: if the last item is not a user message, either of the following is added as the user message:
                1. the first item of the list `follow_up_prompt` if there is one
                2. default follow-up prompt, i.e. the value of the environment variable `DEFAULT_FOLLOW_UP_PROMPT` if it is defined
                3. a single string "Please tell me more." if none of the above

        backend:
            type: Optional[str]="ollama"
            AI backend
            supported backends: "anthropic", "azure", "cohere", "custom", "deepseek", "genai", "github", "googleai", "groq", "llamacpp", "mistral", "ollama", "openai", "vertexai", "xai"

        model:
            type: Optional[str]=None
            AI model name
            applicable to all backends, execept for `llamacpp`
            for backend `llamacpp`, specify a model file in the command line running the llama.cpp server
            for backend `ollama`, model is automatically downloaded if it is not in the downloaded model list

        model_keep_alive:
            type: Optional[str]=None
            time to keep the model loaded in memory
            applicable to ollama only

        system:
            type: Optional[Union[List[Optional[str]], str]]=None
            system message that defines how the model should generally behave and respond
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple system messages, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a markdown file, placed in folder `systems` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a markdown file, placed in folder `systems` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. "auto" - automate generation of system message based on user request
                    remarks: newly generated system message is saved at `~/agentmake/systems` by default
                5. a string that starts with "role.", e.g. "role.Programmer", "role.Finance Expert", "role.Church Pastor", "role.Accountant" - automate generation of system message based on the specified role
                    remarks: newly generated system message is saved at `~/agentmake/systems/roles` by default
                6. a string of a system message
            Fabric integration: `agentmake` supports the use of `fabric` patterns as `system` components for running `agentmake` function or CLI options [READ HERE](https://github.com/eliranwong/agentmake#fabric-integration).

        instruction:
            type: Optional[Union[List[Optional[str]], str]]=None
            predefined instruction, being added to the user prompt as prefix
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple predefined instructions, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a markdown file, placed in folder `instructions` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a markdown file, placed in folder `instructions` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a string of a predefined instruction
            Fabric integration: `agentmake` supports the use of `fabric` patterns as `instruction` components for running `agentmake` function or CLI options [READ HERE](https://github.com/eliranwong/agentmake#fabric-integration).

        follow_up_prompt:
            type: Optional[Union[List[str], str]]=None
            follow-up prompt after an assistant message is generated
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple follow-up prompts, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a markdown file, placed in folder `prompts` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a markdown file, placed in folder `prompts` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a string of a prompt
            remarks: if the last item of the given messages is not a user message, the first item in the follow_up_prompt list, if there is one, is used as the user message.

        input_content_plugin:
            type: Optional[Union[List[Optional[str]], str]]=None
            plugin that contain functions to process user input content
            accepts a list of strings or a single string
            run all specified plugins to process user input content on every single turn
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `plugins` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `plugins` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. CONTENT_PLUGIN - the function object that processes user input content and returns the processed content

        output_content_plugin:
            type: Optional[Union[List[Optional[str]], str]]=None
            plugin that contain functions to process assistant output
            accepts a list of strings or a single string
            run all specified plugins to process assistant output content on every single turn
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `plugins` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `plugins` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. CONTENT_PLUGIN - the function object that processes assistant output content and returns the processed content

        agent:
            type: Optional[Union[List[Optional[str]], str]]=None
            agent that automates multi-turn work and decision
            accepts a list of strings or a single string
            runs multi-turn actions, to loop through multiple agents, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `agents` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `agents` under agentmate directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. AGENT_FUNCTION - the funciton object being called with the agent
            remarks: parameters of both `system`, `instructions`, `prefill`, `follow_up_prompt`, `input_content_plugin`, `output_content_plugin`, `agent`, `schema` and `func` are ignored for a single turn when `agent` parameter is given

        tool:
            type: Optional[Union[List[Optional[str]], str]]=None
            tool that calls a function in response
            accepts a list of strings or a single string
            runs multi-turn actions, to loop through multiple tools, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `tools` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `tools` under agentmake user directory, i.e. the value of AGENTMAKE_USER_DIR
                3. a valid plain text file path
                4. a python script containing two to four variables:
                    I. TOOL_SCHEMA - the json schema that describes the parameters for function calling
                        Remarks: It is allowed to provide an empty dictionary as a TOOL_SCHEMA. In this case, the `agentmake` function passes the parameter `messages` to the TOOL_FUNCTION.
                    II. TOOL_FUNCTION - the funciton object being called with the tool
                        Args:
                            i. The structured output, generated as a dictionary according to the TOOL_SCHEMA, is unpacked as arguments for the function.
                            ii. Each TOOL_FUNCTION must include `**kwargs` as part of its arguments, as the `agentmake` function passes the following parameters to the TOOL_FUNCTION, offering possibility to run nested `agentmake` functions within the TOOL_FUNCTION:
                                backend, model, model_keep_alive, temperature, max_tokens, context_window, batch_size, prefill, stop, stream, api_key, api_project_id, api_service_location, api_timeout, print_on_terminal, word_wrap
                        Return
                            i. Empty string - User request is resolved without the need of chat extension. Any printed content or terminal output resulting from the execution of the function is taken as the assistant's response.
                            ii. Non-empty string - Provide context to extend chat conversation.
                            iii. None - Fall back to regular chat completion. It is useful for handling errors encounted when the function is executed.
                    III. TOOL_SYSTEM - This is optional. You may either:
                        i. specifie the system message for running the tool.
                        ii. assign an empty string to it if you do not want to use a tool system message.
                        iii. omit this parameter to use `agentmake` default tool system message.
                    IV. TOOL_DESCRIPTION - the tool description. This is optional if tool description is specified in the `TOOL_SCHEMA` variable.
            remarks: parameters of both `schema` and `func` are ignored for a single turn when `tool` parameter is given

        schema:
            type: Optional[dict]=None
            json schema for structured output or function calling

        func:
            type: Optional[Callable[..., Optional[str]]]=None
            function to be called

        temperature:
            type: Optional[float]=None
            temperature for sampling

        max_tokens:
            type: Optional[int]=None
            maximum number of tokens to generate

        context_window:
            type: Optional[int]=None
            context window size
            applicable to ollama only

        batch_size:
            type: Optional[int]=None
            batch size
            applicable to ollama only

        prefill:
            type: Optional[Union[List[Optional[str]], str]]=None
            prefill of assistant message
            applicable to deepseek, mistral, ollama and groq only
            accepts a list of strings or a single string
            loop through multiple prefills for multi-turn inferences if it is a list

        stop:
            type: Optional[list]=None
            stop sequences

        stream:
            type: Optional[bool]=False
            stream partial message deltas as they are available

        stream_events_only:
            type: Optional[bool]=False
            return streaming events object only

        api_key:
            type: Optional[str]=None
            API key or credentials json file path in case of using Vertex AI as backend
            applicable to anthropic, cohere, custom, deepseek, genai, github, googleai, groq, mistral, openai, xai

        api_endpoint:
            type: Optional[str]=None
            API endpoint
            applicable to azure, custom, llamacpp, ollama

        api_project_id:
            type: Optional[str]=None
            project id
            applicable to Vertex AI only, i.e., vertexai or genai

        api_service_location:
            type: Optional[str]=None
            cloud service location
            applicable to Vertex AI only, i.e., vertexai or genai

        api_timeout:
            type: Optional[Union[int, float]]=None
            timeout for API request
            applicable to all backends, execept for ollama

        print_on_terminal:
            type: Optional[bool]=True
            print output on terminal

        word_wrap:
            type: Optional[bool]=True
            word wrap output according to current terminal width

        **kwargs,
            pass extra options supported by individual backends

    Return:
        either:
            list of messages containing multi-turn interaction between user and the AI assistant
            find the latest assistant response in the last item of the list
        or:
            streaming events object of AI assistant response when both parameters `stream` and `stream_events_only` are set to `True`
    """
    if backend not in SUPPORTED_AI_BACKENDS:
        raise ValueError(f"Backend {backend} is not supported. Supported backends are {SUPPORTED_AI_BACKENDS}")
    # placeholders
    original_system = ""
    chat_system = ""
    # deep copy messages to avoid modifying the original one
    messages_copy = deepcopy(messages) if isinstance(messages, list) else [{"role": "system", "content": DEFAULT_SYSTEM_MESSAGE}, {"role": "user", "content": messages}]
    # convert follow-up-prompt to a list if it is given as a string
    if follow_up_prompt and isinstance(follow_up_prompt, str):
        follow_up_prompt = [follow_up_prompt]
    elif not follow_up_prompt:
        follow_up_prompt = []
    # ensure user message is placed in the last item in the message list
    if messages_copy[-1].get("role", "") == "user":
        user_input = messages_copy[-1].get("content", "")
    else:
        user_input = follow_up_prompt.pop(0) if follow_up_prompt else DEFAULT_FOLLOW_UP_PROMPT
        messages_copy.append({"role": "user", "content": user_input})
    # echo the last assistant response if no user input is given
    if not user_input and len(messages_copy) > 1 and messages_copy[-2].get("role", "") == "assistant":
        messages_copy[-1]["content"] = messages_copy[-2].get("content", "")
    # handle user input content plugin(s)
    if input_content_plugin:
        if isinstance(input_content_plugin, str):
            input_content_plugin = [input_content_plugin]
        for input_content_plugin_object in input_content_plugin:
            input_content_plugin_func = None
            input_content_plugin_name = input_content_plugin_object[:20]

            # check if it is a predefined plugin message built-in with this SDK
            possible_input_content_plugin_file_path_2 = os.path.join(PACKAGE_PATH, "plugins", f"{input_content_plugin_object}.py")
            possible_input_content_plugin_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "plugins", f"{input_content_plugin_object}.py")
            if input_content_plugin_object is None:
                pass
            elif os.path.isfile(possible_input_content_plugin_file_path_1):
                input_content_plugin_file_content = readTextFile(possible_input_content_plugin_file_path_1)
                if input_content_plugin_file_content:
                    input_content_plugin_object = input_content_plugin_file_content
            elif os.path.isfile(possible_input_content_plugin_file_path_2):
                input_content_plugin_file_content = readTextFile(possible_input_content_plugin_file_path_2)
                if input_content_plugin_file_content:
                    input_content_plugin_object = input_content_plugin_file_content
            elif os.path.isfile(input_content_plugin_object): # input_content_plugin_object itself is a valid filepath
                input_content_plugin_file_content = readTextFile(input_content_plugin_object)
                if input_content_plugin_file_content:
                    input_content_plugin_object = input_content_plugin_file_content
            if input_content_plugin_object:
                glob = {}
                loc = {}
                try:
                    exec(input_content_plugin_object, glob, loc)
                    input_content_plugin_func = loc.get("CONTENT_PLUGIN")
                except Exception as e:
                    print(f"Failed to execute input content plugin `{input_content_plugin_name}`! An error occurred: {e}")
                    if DEVELOPER_MODE:
                        print(traceback.format_exc())
            # run user input content plugin
            if input_content_plugin_func:
                if user_input := messages_copy[-1].get("content", ""):
                    messages_copy[-1]["content"] = input_content_plugin_func(
                        user_input,
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
                        api_project_id=api_project_id,
                        api_service_location=api_service_location,
                        api_timeout=api_timeout,
                        print_on_terminal=print_on_terminal,
                        word_wrap=word_wrap,
                        **kwargs,
                    )
    # handle agent(s)
    agent_response = None
    agent_func = None
    if agent:
        if isinstance(agent, list):
            agent_object = agent.pop(0)
        else: # a string instead
            agent_object = agent
            agent = []
        agent_name = agent_object[:20]
        # check if it is a predefined plugin message built-in with this SDK
        possible_agent_file_path_2 = os.path.join(PACKAGE_PATH, "agents", f"{agent_object}.py")
        possible_agent_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "agents", f"{agent_object}.py")
        if agent_object is None:
            pass
        elif os.path.isfile(possible_agent_file_path_1):
            agent_file_content = readTextFile(possible_agent_file_path_1)
            if agent_file_content:
                agent_object = agent_file_content
        elif os.path.isfile(possible_agent_file_path_2):
            agent_file_content = readTextFile(possible_agent_file_path_2)
            if agent_file_content:
                agent_object = agent_file_content
        elif os.path.isfile(agent_object): # agent_object itself is a valid filepath
            agent_file_content = readTextFile(agent_object)
            if agent_file_content:
                agent_object = agent_file_content
        if agent_object:
            glob = {}
            loc = {}
            try:
                exec(agent_object, glob, loc)
                agent_func = loc.get("AGENT_FUNCTION")
            except Exception as e:
                print(f"Failed to run agent `{agent_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
        # run user input content plugin
        if agent_func:
            agent_response = agent_func(
                messages_copy,
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
    # handle given system message(s)
    if system and not agent_response:
        if isinstance(system, list):
            system_instruction = system.pop(0)
        else: # a string instead
            system_instruction = system
            system = []
        if system_instruction is None:
            pass
        else:
            user_prompt = messages_copy[-1].get("content", "")
            system_instruction = refine_system_instruction(
                system_instruction,
                user_prompt=user_prompt,
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
                **kwargs
            )
        if system_instruction:
            original_system = updateSystemMessage(messages_copy, system_instruction)
    elif not system and not agent_response and DEFAULT_SYSTEM_MESSAGE:
        user_prompt = messages_copy[-1].get("content", "")
        system_instruction = refine_system_instruction(
            DEFAULT_SYSTEM_MESSAGE,
            user_prompt=user_prompt,
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
            **kwargs
        )
        if system_instruction:
            original_system = updateSystemMessage(messages_copy, system_instruction)
    # handle given predefined instruction(s)
    if instruction and not agent_response:
        if isinstance(instruction, list):
            instruction_content = instruction.pop(0)
        else: # a string instead
            instruction_content = instruction
            instruction = []
        # check if it is a predefined instruction built-in with this SDK
        possible_instruction_file_path_2 = os.path.join(PACKAGE_PATH, "instructions", f"{instruction_content}.md")
        possible_instruction_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "instructions", f"{instruction_content}.md")
        if instruction_content is None:
            pass
        elif isFabricPattern(instruction_content): # fabric integration
            instruction_content = getFabricPatternSystem(instruction_content[7:], instruction=True)
        elif os.path.isfile(possible_instruction_file_path_1):
            instruction_file_content = readTextFile(possible_instruction_file_path_1)
            if instruction_file_content:
                instruction_content = instruction_file_content
        elif os.path.isfile(possible_instruction_file_path_2):
            instruction_file_content = readTextFile(possible_instruction_file_path_2)
            if instruction_file_content:
                instruction_content = instruction_file_content
        elif os.path.isfile(instruction_content): # instruction_content itself is a valid filepath
            instruction_file_content = readTextFile(instruction_content)
            if instruction_file_content:
                instruction_content = instruction_file_content
        if instruction_content:
            messages_copy[-1]["content"] = instruction_content + "\n" + messages_copy[-1]["content"]
    # handle given prefill(s)
    if prefill and not agent_response:
        if isinstance(prefill, list):
            prefill_content = prefill.pop(0)
        else: # a string instead
            prefill_content = prefill
            prefill = None
    else:
        prefill_content = None
    # handle given tools
    if tool and not agent_response:
        if isinstance(tool, list):
            tool_object = tool.pop(0)
        else: # a string instead
            tool_object = tool
            tool = []
        tool_name = tool_object[:20]
        # check if it is a predefined tool built-in with this SDK
        possible_tool_file_path_2 = os.path.join(PACKAGE_PATH, "tools", f"{tool_object}.py")
        possible_tool_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "tools", f"{tool_object}.py")
        if tool_object is None:
            pass
        elif os.path.isfile(possible_tool_file_path_1):
            tool_file_content = readTextFile(possible_tool_file_path_1)
            if tool_file_content:
                tool_object = tool_file_content
        elif os.path.isfile(possible_tool_file_path_2):
            tool_file_content = readTextFile(possible_tool_file_path_2)
            if tool_file_content:
                tool_object = tool_file_content
        elif os.path.isfile(tool_object): # tool_object itself is a valid filepath
            tool_file_content = readTextFile(tool_object)
            if tool_file_content:
                tool_object = tool_file_content
        if tool_object:
            glob = {}
            loc = {}
            try:
                exec(tool_object, glob, loc)
                schema = loc.get("TOOL_SCHEMA")
                try:
                    func = loc.get("TOOL_FUNCTION")
                except:
                    # TOOL_FUNCTION is optional
                    pass
                try:
                    tool_system = loc.get("TOOL_SYSTEM")
                except:
                    tool_system = getDefaultToolSystem(schema)
                if tool_system:
                    chat_system = updateSystemMessage(messages_copy, tool_system)
            except Exception as e:
                print(f"Failed to execute tool `{tool_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())

    # check if it is last request
    is_last_request = True if not follow_up_prompt and not system and not instruction and not tool and not agent and not prefill else False

    # deep copy schema avoid modifying the original one
    schemaCopy = None if schema is None else deepcopy(schema)
    # run AI
    if agent_response is not None:
        if stream and stream_events_only and is_last_request:
            return agent_response
        else:
            messages_copy = agent_response
            output = agent_response[-1].get("content", "")
    elif schemaCopy is not None: # structured output or function calling; allow schema to be an empty dict
        dictionary_output = {"messages": messages_copy} if not schemaCopy else getDictionaryOutput(
            messages_copy,
            schemaCopy,
            backend,
            model=model,
            model_keep_alive=model_keep_alive,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
            prefill=prefill_content,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            api_timeout=api_timeout,
            **kwargs
        )
        if chat_system:
            updateSystemMessage(messages_copy, chat_system)
            chat_system = ""
        if func:
            # Create a StringIO object to capture the output
            terminal_output = StringIO()
            # Redirect stdout to the StringIO object
            old_stdout = sys.stdout
            sys.stdout = terminal_output
            # placeholder for function text output
            function_text_output = ""
            try:
                # execute the function
                function_response = func() if not dictionary_output else func(
                    **dictionary_output,
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
                    api_project_id=api_project_id,
                    api_service_location=api_service_location,
                    api_timeout=api_timeout,
                    print_on_terminal=print_on_terminal,
                    word_wrap=word_wrap,
                    **kwargs,
                ) # returned response can be either 1) an empty string: no chat extension 2) a non-empty string: chat extension 3) none: errors encountered in executing the function
                function_text_output = terminal_output.getvalue().replace("```output\n```\n", "Done!") # capture the function text output for function calling without chat extension
                # Restore the original stdout
                sys.stdout = old_stdout
            except Exception as e:
                sys.stdout = old_stdout
                function_name = re.sub("<function (.*?) .*?$", r"\1", str(func))
                print(f"Failed to run tool function `{function_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
                function_response = None # due to unexpected errors encountered in executing the function; fall back to regular completion
            # handle function response
            if function_response is None or function_response: # fall back to regular completion if function_response is None; chat extension if function_response
                if function_response:
                    # added function response as provided information to the original prompt
                    addContextToMessages(messages_copy, function_response)
                return agentmake(
                    messages_copy,
                    backend,
                    model=model,
                    model_keep_alive=model_keep_alive,
                    system=None if function_response else system,
                    instruction=None if function_response else instruction,
                    follow_up_prompt=None if function_response else follow_up_prompt,
                    input_content_plugin=None if function_response else input_content_plugin,
                    output_content_plugin=output_content_plugin,
                    agent=None if function_response else agent,
                    tool=None if function_response else tool,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    context_window=context_window,
                    batch_size=batch_size,
                    prefill=None if function_response else prefill_content,
                    stop=stop,
                    stream=stream,
                    stream_events_only=stream_events_only,
                    api_key=api_key,
                    api_endpoint=api_endpoint,
                    api_project_id=api_project_id,
                    api_service_location=api_service_location,
                    api_timeout=api_timeout,
                    print_on_terminal=print_on_terminal,
                    word_wrap=word_wrap,
                    **kwargs
                )
            else: # empty str; function executed successfully without chat extension
                output = function_text_output if function_text_output else "Done!"
        else: # structured output
            output = json.dumps(dictionary_output)
        if print_on_terminal:
            print(output)
    else: # regular completion
        if backend == "anthropic":
            completion = AnthropicAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "azure":
            completion = AzureAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_endpoint=api_endpoint,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "cohere":
            completion = CohereAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "custom":
            completion = OpenaiCompatibleAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_endpoint=api_endpoint,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "deepseek":
            completion = DeepseekAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                prefill=prefill_content,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend in ("genai", "vertexai"):
            completion = GenaiAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_project_id=api_project_id,
                api_service_location=api_service_location,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "github":
            completion = GithubAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "googleai":
            completion = GoogleaiAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "groq":
            completion = GroqAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                prefill=prefill_content,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "llamacpp":
            completion = LlamacppAI.getChatCompletion(
                messages_copy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_endpoint=api_endpoint,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "mistral":
            completion = MistralAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                prefill=prefill_content,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                stream_events_only=stream_events_only,
                print_on_terminal=print_on_terminal,
                word_wrap=word_wrap,
                **kwargs
            )
        elif backend == "ollama":
            completion = OllamaAI.getChatCompletion(             
                messages_copy,
                model=model,
                model_keep_alive=model_keep_alive,
                temperature=temperature,
                max_tokens=max_tokens,
                context_window=context_window,
                batch_size=batch_size,
                prefill=prefill_content,
                stop=stop,
                stream=stream,
                api_endpoint=api_endpoint,
                **kwargs
            )
        elif backend == "openai":
            completion = OpenaiAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "xai":
            completion = XaiAI.getChatCompletion(
                messages_copy,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        if stream and stream_events_only and is_last_request:
            return completion
        output = getChatCompletionText(backend, completion, stream=stream, print_on_terminal=print_on_terminal, word_wrap=word_wrap)

    # close connection
    closeConnections(backend)

    # handle user output content plugin(s)
    if output_content_plugin:
        if isinstance(output_content_plugin, str):
            output_content_plugin = [output_content_plugin]
        for output_content_plugin_object in output_content_plugin:
            output_content_plugin_func = None
            output_content_plugin_name = output_content_plugin_object[:20]

            # check if it is a predefined plugin message built-in with this SDK
            possible_output_content_plugin_file_path_2 = os.path.join(PACKAGE_PATH, "plugins", f"{output_content_plugin_object}.py")
            possible_output_content_plugin_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "plugins", f"{output_content_plugin_object}.py")
            if output_content_plugin_object is None:
                pass
            elif os.path.isfile(possible_output_content_plugin_file_path_1):
                output_content_plugin_file_content = readTextFile(possible_output_content_plugin_file_path_1)
                if output_content_plugin_file_content:
                    output_content_plugin_object = output_content_plugin_file_content
            elif os.path.isfile(possible_output_content_plugin_file_path_2):
                output_content_plugin_file_content = readTextFile(possible_output_content_plugin_file_path_2)
                if output_content_plugin_file_content:
                    output_content_plugin_object = output_content_plugin_file_content
            elif os.path.isfile(output_content_plugin_object): # output_content_plugin_object itself is a valid filepath
                output_content_plugin_file_content = readTextFile(output_content_plugin_object)
                if output_content_plugin_file_content:
                    output_content_plugin_object = output_content_plugin_file_content
            if output_content_plugin_object:
                glob = {}
                loc = {}
                try:
                    exec(output_content_plugin_object, glob, loc)
                    output_content_plugin_func = loc.get("CONTENT_PLUGIN")
                except Exception as e:
                    print(f"Failed to execute output content plugin `{output_content_plugin_name}`! An error occurred: {e}")
                    if DEVELOPER_MODE:
                        print(traceback.format_exc())
            # run user output content plugin
            if output_content_plugin_func and output:
                output = output_content_plugin_func(
                    output,
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
                    api_project_id=api_project_id,
                    api_service_location=api_service_location,
                    api_timeout=api_timeout,
                    print_on_terminal=print_on_terminal,
                    word_wrap=word_wrap,
                    **kwargs,
                )

    # update the message list
    if not agent_response:
        messages_copy.append({"role": "assistant", "content": output if output else "Done!"})

    # restore system message
    if original_system:
        updateSystemMessage(messages_copy, original_system)
    # work on follow-up prompts
    if not is_last_request and not follow_up_prompt:
        follow_up_prompt = DEFAULT_FOLLOW_UP_PROMPT
    if follow_up_prompt:
        follow_up_prompt_content = follow_up_prompt.pop(0)
        follow_up_prompt_content = refine_follow_up_prompt_content(follow_up_prompt_content)
        messages_copy.append({"role": "user", "content": follow_up_prompt_content})
        return agentmake(
            messages=messages_copy,
            backend=backend,
            model=model,
            model_keep_alive=model_keep_alive,
            system=system,
            instruction=instruction,
            follow_up_prompt=follow_up_prompt,
            input_content_plugin=input_content_plugin,
            output_content_plugin=output_content_plugin,
            agent=agent,
            tool=tool,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
            prefill=prefill,
            stop=stop,
            stream=stream,
            stream_events_only=stream_events_only,
            api_key=api_key,
            api_endpoint=api_endpoint,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            api_timeout=api_timeout,
            print_on_terminal=print_on_terminal,
            word_wrap=word_wrap,
            **kwargs
        )
    # For debugging
    #print(messages_copy)
    return messages_copy

def refine_system_instruction(
    system_instruction,
    user_prompt: Optional[str]=None, # user prompt
    backend: Optional[str]=DEFAULT_AI_BACKEND, # AI backend; check SUPPORTED_AI_BACKENDS for supported backends
    model: Optional[str]=None, # AI model name; applicable to all backends, execept for llamacpp
    model_keep_alive: Optional[str]=None, # time to keep the model loaded in memory; applicable to ollama only
    temperature: Optional[float]=None, # temperature for sampling
    max_tokens: Optional[int]=None, # maximum number of tokens to generate
    context_window: Optional[int]=None, # context window size; applicable to ollama only
    batch_size: Optional[int]=None, # batch size; applicable to ollama only
    stream: Optional[bool]=False, # stream partial message deltas as they are available
    api_key: Optional[str]=None, # API key or credentials json file path in case of using Vertex AI as backend; applicable to anthropic, custom, deepseek, genai, github, googleai, groq, mistral, openai, xai
    api_endpoint: Optional[str]=None, # API endpoint; applicable to azure, custom, llamacpp, ollama
    api_project_id: Optional[str]=None, # project id; applicable to Vertex AI only, i.e., vertexai or genai
    api_service_location: Optional[str]=None, # cloud service location; applicable to Vertex AI only, i.e., vertexai or genai
    api_timeout: Optional[Union[int, float]]=None, # timeout for API request; applicable to all backends, execept for ollama
    print_on_terminal: Optional[bool]=True, # print output on terminal
    word_wrap: Optional[bool]=True, # word wrap output according to current terminal width
    **kwargs, # pass extra options supported by individual backends
) -> str:
    # check if it is a predefined system message built-in with this SDK
    possible_system_file_path_2 = os.path.join(PACKAGE_PATH, "systems", f"{system_instruction}.md")
    possible_system_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "systems", f"{system_instruction}.md")

    if system_instruction in ("auto", "reasoning") and user_prompt:
        if print_on_terminal:
            print(">>> Generating system instruction ...\n")
        system_instruction = agentmake(
            user_prompt,
            system="create_reasoning_agent" if system_instruction == "reasoning" else "create_agent",
            instruction=os.path.join("system", "auto"),
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
        )[-1].get("content", "")
        if agent := re.search("""```agent(.+?)```""", system_instruction, re.DOTALL):
            system_instruction = agent.group(1).strip()
        try:
            user_systems_file = saveUserSystemMessage(system_instruction)
            if print_on_terminal:
                print(f">>> System instruction saved: {user_systems_file}")
        except:
            pass
        if print_on_terminal:
            print(">>> System instruction updated!\n")
    elif system_instruction.startswith("role."):
        role = system_instruction[5:]
        filename = re.sub("[^A-Za-z_]", "", role.replace(" ", "_"))
        custom_role = os.path.join(AGENTMAKE_USER_DIR, "systems", "roles", f"{filename}.md")
        builtin_role = os.path.join(PACKAGE_PATH, "systems", "roles", f"{filename}.md")
        if os.path.isfile(custom_role):
            # reuse previously generated sytem message
            system_instruction = readTextFile(custom_role)
        elif os.path.isfile(builtin_role):
            # use built-in role system message
            system_instruction = readTextFile(builtin_role)
        else:
            # generate new role
            if print_on_terminal:
                print(">>> Generating system instruction ...\n")
            system_instruction = agentmake(
                role,
                instruction=os.path.join("system", "role"),
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
            )[-1].get("content", "")
        try:
            user_systems_file = saveUserSystemMessage(system_instruction, subfolder="roles", filename=role)
            if print_on_terminal:
                print(f">>> System instruction saved: {user_systems_file}")
        except:
            pass
        if print_on_terminal:
            print(">>> System instruction updated!\n")
    elif isFabricPattern(system_instruction): # fabric integration
        system_instruction = getFabricPatternSystem(system_instruction[7:])
    elif os.path.isfile(possible_system_file_path_1):
        system_file_content = readTextFile(possible_system_file_path_1)
        if system_file_content:
            system_instruction = system_file_content
    elif os.path.isfile(possible_system_file_path_2):
        system_file_content = readTextFile(possible_system_file_path_2)
        if system_file_content:
            system_instruction = system_file_content
    elif os.path.isfile(system_instruction): # system_instruction itself is a valid filepath
        system_file_content = readTextFile(system_instruction)
        if system_file_content:
            system_instruction = system_file_content
    return system_instruction

def refine_follow_up_prompt_content(follow_up_prompt_content):
    # check if it is a predefined follow_up_prompt built-in with this SDK
    possible_follow_up_prompt_file_path_2 = os.path.join(PACKAGE_PATH, "prompts", f"{follow_up_prompt_content}.md")
    possible_follow_up_prompt_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "prompts", f"{follow_up_prompt_content}.md")
    if os.path.isfile(possible_follow_up_prompt_file_path_1):
        follow_up_prompt_file_content = readTextFile(possible_follow_up_prompt_file_path_1)
        if follow_up_prompt_file_content:
            follow_up_prompt_content = follow_up_prompt_file_content
    elif os.path.isfile(possible_follow_up_prompt_file_path_2):
        follow_up_prompt_file_content = readTextFile(possible_follow_up_prompt_file_path_2)
        if follow_up_prompt_file_content:
            follow_up_prompt_content = follow_up_prompt_file_content
    elif os.path.isfile(follow_up_prompt_content): # follow_up_prompt_content itself is a valid filepath
        follow_up_prompt_file_content = readTextFile(follow_up_prompt_content)
        if follow_up_prompt_file_content:
            follow_up_prompt_content = follow_up_prompt_file_content
    return follow_up_prompt_content

def getDictionaryOutput(
    messages: List[Dict[str, str]],
    schema: dict,
    backend: str,
    model: Optional[str]=None,
    model_keep_alive: Optional[str]=None,
    temperature: Optional[float]=None, 
    max_tokens: Optional[int]=None,
    context_window: Optional[int]=None,
    batch_size: Optional[int]=None,
    prefill: Optional[str]=None,
    stop: Optional[list]=None,
    api_key: Optional[str]=None,
    api_endpoint: Optional[str]=None,
    api_project_id: Optional[str]=None,
    api_service_location: Optional[str]=None,
    api_timeout: Optional[Union[int, float]]=None,
    **kwargs,
) -> dict:
    """
    Returns dictionary in response to user message
    """
    if backend == "anthropic":
        return AnthropicAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "azure":
        return AzureAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "cohere":
        return CohereAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "custom":
        return OpenaiCompatibleAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "deepseek":
        return DeepseekAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend in ("genai", "vertexai"):
        return GenaiAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "github":
        return GithubAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "googleai":
        return GoogleaiAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "groq":
        return GroqAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "llamacpp":
        return LlamacppAI.getDictionaryOutput(
            messages,
            schema,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_endpoint=api_endpoint,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "mistral":
        return MistralAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            prefill=prefill,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "ollama":
        return OllamaAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            model_keep_alive=model_keep_alive,
            temperature=temperature,
            max_tokens=max_tokens,
            context_window=context_window,
            batch_size=batch_size,
            prefill=prefill,
            stop=stop,
            api_endpoint=api_endpoint,
            **kwargs
        )
    elif backend == "openai":
        return OpenaiAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    elif backend == "xai":
        return XaiAI.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_timeout=api_timeout,
            **kwargs
        )
    return {}

def saveUserSystemMessage(system: str, subfolder="", filename=""):
    user_systems_dir = os.path.join(AGENTMAKE_USER_DIR, "systems", subfolder) if subfolder else os.path.join(AGENTMAKE_USER_DIR, "systems")
    Path(user_systems_dir).mkdir(parents=True, exist_ok=True)
    if not filename:
        filename = system[:50]
    filename = filename.replace(" ", "_")
    filename = re.sub("[^A-Za-z_]", "", filename)
    if not filename:
        filename = getCurrentDateTime()
    user_systems_file = os.path.join(user_systems_dir, f"{filename}.md")
    writeTextFile(user_systems_file, system)
    return user_systems_file

def updateSystemMessage(messages: List[Dict[str, str]], system: str) -> str:
    """
    update system message content in the given message list
    and return the original system message
    """
    original_system = ""
    for i in messages:
        if i.get("role", "") == "system":
            original_system = i.get("content", "")
            i["content"] = system
            break
    return original_system

def addContextToMessages(messages: List[Dict[str, str]], context: str):
    """
    add context to user prompt
    assuming user prompt is placed in the last item of the given message list
    """
    messages[-1] = {"role": "user", "content": getRagPrompt(messages[-1].get("content", ""), context)}

def showErrors(e=None, message=""):
    if message:
        trace = message
    else:
        trace = f"An error occurred: {e}" if e else "An error occurred!"
    print(trace)
    if DEVELOPER_MODE:
        details = traceback.format_exc()
        trace += "\n"
        trace += details
        print("```error")
        print(details)
        print("```")
    return trace

def getOpenCommand():
    if shutil.which("termux-share"):
        return "termux-share"
    elif USER_OS == "Linux":
        return "xdg-open"
    elif USER_OS == "Darwin":
        return "open"
    elif USER_OS == "Windows":
        return "start"
    return "open"

def extractText(item: Any, image_backend: str=""):
    def getBackendClient(image_backend):
        if image_backend == "openai":
            return OpenaiAI.getClient()
        elif image_backend == "github":
            return GithubAI.getClient()
        elif image_backend == "azure":
            return AzureAI.getClient()
        elif client := AzureAI.getClient():
            return client
        elif client := GithubAI.getClient():
            return client
        else:
            return OpenaiAI.getClient()
    try:
        md = MarkItDown(llm_client=getBackendClient(image_backend), llm_model="gpt-4o") if re.search(r"(\.jpg|\.jpeg|\.png)$", item.lower()) else MarkItDown()
        text_content = md.convert(item).text_content
    except Exception as e:
        showErrors(e)
        return f"An error occurred: {e}"
    return text_content

def getDefaultToolSystem(schema):
    try:
        required = schema["parameters"].get("required", [])
        properties = schema["parameters"]["properties"]
        if not properties:
            return ""
        system = """You are a structured output expert. Your expertise lies in identifying the following parameters from user input.
If any required parameters are not provided by the users, you should either:
1. Generate content for them based on the parameter descriptions, or
2. Return an empty string '' if explicitly instructed to do so in their descriptions when they are not provided."""
        for key, value in properties.items():
            system += f"""

# {key} [{"required" if key in required else "optional"}]

{value.get("description", "")}"""
        return system
    except:
        return ""

def getToolInfo(tool_path):
    content = readTextFile(tool_path)
    glob = {}
    loc = {}
    exec(content, glob, loc)
    schema = loc.get("TOOL_SCHEMA")
    tool = re.sub(r"^.*?tools[/\\](.*?)\.[^.]+?$", r"\1", tool_path)
    if not schema:
        description = loc.get("TOOL_DESCRIPTION", "")
        return f"`@{tool}` {description}"
    description = schema["description"]
    required = schema["parameters"]["required"]
    optional = [i for i in schema["parameters"]["properties"] if not i in required]
    required = f""" (Required parameters: {str(required)[1:-1]})""" if required else ""
    optional = f""" [Optional parameters: {str(optional)[1:-1]}]""" if optional else ""
    info = f"""`@{tool}` {description}{required}{optional}"""
    return info

# list available components
def listResources(folder: str, ext: str="md", info: bool=False, display_func: Optional[Callable]=None):
    items = []
    folder1 = os.path.join(AGENTMAKE_USER_DIR, folder)
    folder2 = os.path.join(PACKAGE_PATH, folder)
    for i in (folder1, folder2):
        if os.path.isdir(i):
            for ii in os.listdir(i):
                fullPath = os.path.join(i, ii)
                if os.path.isfile(fullPath) and not ii.lower() == "readme.md" and ii.endswith(f".{ext}"):
                    component = os.path.join(folder, ii)
                    if info:
                        try:
                            #print(getToolInfo(fullPath))
                            info = getToolInfo(fullPath)
                            items.append(info)
                            if display_func:
                                display_func(info)
                        except:
                            # skipped unsupported tools
                            pass
                    else:
                        item = re.sub(r"^.*?[/\\]", "", component)[:-(len(ext)+1)]
                        items.append(item)
                        if display_func:
                            display_func(item)
                elif os.path.isdir(fullPath) and not os.path.basename(fullPath) == "lib":
                    items += listResources(os.path.join(folder, ii), ext=ext, info=info, display_func=display_func)
    return items

def getMultipleTools(content, info=False):
    all_tools = listResources("tools", ext="py")
    tool_pattern = "|".join(all_tools)
    tool_pattern = f"""@({tool_pattern})[\n`'" ]"""
    tools = re.findall(tool_pattern, f"{content} ")
    if not info:
        return tools if tools else all_tools
    if not tools:
        return (all_tools, listResources("tools", ext="py", info=True))
    tools_description = []
    for tool in tools:
        possible_tool_file_path_1 = os.path.join(AGENTMAKE_USER_DIR, "tools", f"{tool}.py")
        possible_tool_file_path_2 = os.path.join(PACKAGE_PATH, "tools", f"{tool}.py")
        tool_path = possible_tool_file_path_1 if os.path.isfile(possible_tool_file_path_1) else possible_tool_file_path_2
        tools_description.append(getToolInfo(tool_path))
    return (tools, tools_description)

def exportPlainConversation(messages: list, filepath: str):
    export_content = []
    for i in messages:
        role = i.get("role", "")
        content = i.get("content", "")
        if role in ("user", "assistant") and content.strip():
            content = f"```{role}\n{content}\n```"
            export_content.append(content)
    try:
        writeTextFile(filepath, "\n".join(export_content))
        os.system(f'''{getOpenCommand()} "{filepath}"''')
    except Exception as e:
        raise ValueError("An error occurred: {e}" if e else f"Error! Failed to export conversation to '{filepath}'!")

# fabric integration
def isFabricPattern(item):
    return True if item.startswith("fabric.") and os.path.isfile(os.path.join(os.path.expanduser(DEFAULT_FABRIC_PATTERNS_PATH), item[7:], "system.md")) else False

def getFabricPatternSystem(pattern, instruction=False):
    system = None
    fabricPattern = os.path.join(os.path.expanduser(DEFAULT_FABRIC_PATTERNS_PATH), pattern, "system.md")
    if os.path.isfile(fabricPattern):
        system = readTextFile(fabricPattern)
        if not instruction:
            system = re.sub(r'# INPUT.*', '', system, flags=re.DOTALL).rstrip()
    return system

def ignore_warnings():
    from warnings import filterwarnings
    #filterwarnings("ignore", category=ResourceWarning, message=r"unclosed <socket.socket.*, 11434\)") # ollama # resolved
    filterwarnings("ignore", category=ResourceWarning, message="unclosed <ssl.SSLSocket.*'34.96.76.122'") # cohere # https://github.com/cohere-ai/cohere-python/issues/650
atexit.register(ignore_warnings)