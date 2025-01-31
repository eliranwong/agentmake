from .backends.anthropic import AnthropicLLM
from .backends.azure import AzureLLM
from .backends.custom import OpenaiCompatibleLLM
from .backends.deepseek import DeepseekLLM
from .backends.genai import GenaiLLM
from .backends.github import GithubLLM
from .backends.googleai import GoogleaiLLM
from .backends.groq import GroqLLM
from .backends.llamacpp import LlamacppLLM
from .backends.mistral import MistralLLM
from .backends.ollama import OllamaLLM
from .backends.openai import OpenaiLLM
from .backends.xai import XaiLLM

from .utils.instructions import getRagPrompt
from .utils.retrieve_text_output import getChatCompletionText
from .utils.handle_text import readTextFile

from typing import Optional, Callable, Union, Any, List, Dict
from copy import deepcopy
from io import StringIO
import sys, os, json, traceback

TOOLMATE_PATH = os.getenv("TOOLMATE_PATH") if os.getenv("TOOLMATE_PATH") else os.path.join(os.path.expanduser("~"), "toolmate") # It is where users store their custom tools, keeping them outside the package directory.
PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
PACKAGE_NAME = os.path.basename(PACKAGE_PATH)
DEVELOPER_MODE = True if os.getenv("DEVELOPER_MODE") == "TRUE" else False
SUPPORTED_AI_BACKENDS = ["anthropic", "azure", "custom", "deepseek", "genai", "github", "googleai", "groq", "llamacpp", "mistral", "ollama", "openai", "vertexai", "xai"]
DEFAULT_AI_BACKEND = os.getenv("DEFAULT_AI_BACKEND") if os.getenv("DEFAULT_AI_BACKEND") else "ollama"
DEFAULT_FOLLOW_UP_PROMPT = os.getenv("DEFAULT_FOLLOW_UP_PROMPT") if os.getenv("DEFAULT_FOLLOW_UP_PROMPT") else "Please tell me more."

def generate(
        messages: Union[List[Dict[str, str]], str], # user request or messages containing user request; accepts either a single string or a list of dictionaries
        backend: Optional[str]=DEFAULT_AI_BACKEND, # AI backend; check SUPPORTED_AI_BACKENDS for supported backends
        model: Optional[str]=None, # AI model name; applicable to all backends, execept for llamacpp
        model_keep_alive: Optional[str]=None, # time to keep the model loaded in memory; applicable to ollama only
        system: Optional[Union[List[Optional[str]], str]]=None, # system message; define how the model should generally behave and respond; accepts a list of strings or a single string; loop through multiple system messages for multi-turn inferences if it is a list
        context: Optional[Union[List[Optional[str]], str]]=None, # predefined context to be added to the user prompt as prefix; accepts a list of strings or a single string; loop through multiple predefined contexts for multi-turn inferences if it is a list
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
        api_endpoint: Optional[str]=None, # API endpoint; applicable to anthropic, azure, custom, llamacpp, ollama
        api_project_id: Optional[str]=None, # project id; applicable to Vertex AI only, i.e., vertexai or genai
        api_service_location: Optional[str]=None, # cloud service location; applicable to Vertex AI only, i.e., vertexai or genai
        api_timeout: Optional[Union[int, float]]=None, # timeout for API request; applicable to backends, execept for ollama, genai and vertexai
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
            supported backends: "anthropic", "azure", "custom", "deepseek", "genai", "github", "googleai", "groq", "llamacpp", "mistral", "ollama", "openai", "vertexai", "xai"

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
                2. file name, without extension, of a markdown file, placed in folder `systems` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a string of a system message

        context:
            type: Optional[Union[List[Optional[str]], str]]=None
            predefined context to be added to the user prompt as prefix
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple predefined contexts, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a markdown file, placed in folder `contexts` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a markdown file, placed in folder `contexts` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a string of a predefined context

        follow_up_prompt:
            type: Optional[Union[List[str], str]]=None
            follow-up prompt after an assistant message is generated
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple follow-up prompts, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a markdown file, placed in folder `prompts` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a markdown file, placed in folder `prompts` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a string of a prompt
            remarks: if the last item of the given messages is not a user message, the first item in the follow_up_prompt list, if there is one, is used as the user message.

        input_content_plugin:
            type: Optional[Union[List[Optional[str]], str]]=None
            plugin that contain functions to process user input content
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple plugins, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `plugins` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `plugins` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. CONTENT_PLUGIN - the function object that processes user input content

        output_content_plugin:
            type: Optional[Union[List[Optional[str]], str]]=None
            plugin that contain functions to process assistant output
            accepts a list of strings or a single string
            runs multi-turn inferences, to loop through multiple plugins, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `plugins` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `plugins` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. CONTENT_PLUGIN - the function object that processes assistant output content

        agent:
            type: Optional[Union[List[Optional[str]], str]]=None
            agent that automates multi-turn work and decision
            accepts a list of strings or a single string
            runs multi-turn actions, to loop through multiple agents, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `agents` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `agents` under agentmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a python script containing at least one variable:
                    i. AGENT_FUNCTION - the funciton object being called with the agent
            remarks: parameters of both `system`, `context`, `prefill`, `follow_up_prompt`, `input_content_plugin`, `output_content_plugin`, `agent`, `schema` and `func` are ignored for a single turn when `agent` parameter is given

        tool:
            type: Optional[Union[List[Optional[str]], str]]=None
            tool that calls a function in response
            accepts a list of strings or a single string
            runs multi-turn actions, to loop through multiple tools, if it is given as a list
            each item must be either one of the following options:
                1. file name, without extension, of a python file, placed in folder `tools` under package directory, i.e. the value of PACKAGE_PATH
                2. file name, without extension, of a python file, placed in folder `tools` under toolmate directory, i.e. the value of TOOLMATE_PATH
                3. a valid plain text file path
                4. a python script containing at least three variables:
                    i. TOOL_SYSTEM - the system message for running the tool
                    ii. TOOL_SCHEMA - the json schema that describes the parameters for function calling
                    iii. TOOL_FUNCTION - the funciton object being called with the tool
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
            applicable to anthropic, custom, deepseek, genai, github, googleai, groq, mistral, openai, xai

        api_endpoint:
            type: Optional[str]=None
            API endpoint
            applicable to anthropic, azure, custom, llamacpp, ollama

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
            applicable to backends, execept for ollama, genai and vertexai

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
    # deep copy messages avoid modifying the original one
    messages_copy = deepcopy(messages) if isinstance(messages, list) else [{"role": "system", "content": "You are a helpful AI assistant."}, {"role": "user", "content": messages}]
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
    # handle user input content plugin(s)
    given_input_content_plugin = None
    input_content_plugin_func = None
    if input_content_plugin:
        given_input_content_plugin = deepcopy(input_content_plugin)
        if isinstance(input_content_plugin, list):
            input_content_plugin_object = input_content_plugin.pop(0)
        else: # a string instead
            input_content_plugin_object = input_content_plugin
            input_content_plugin = []
        input_content_plugin_name = input_content_plugin_object[:20]
        # check if it is a predefined plugin message built-in with this SDK
        possible_input_content_plugin_file_path_1 = os.path.join(PACKAGE_PATH, "plugins", f"{input_content_plugin_object}.py")
        possible_input_content_plugin_file_path_2 = os.path.join(TOOLMATE_PATH, "plugins", f"{input_content_plugin_object}.py")
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
            try:
                exec(input_content_plugin_object, globals())
                input_content_plugin_func = CONTENT_PLUGIN
            except Exception as e:
                print(f"Failed to execute input content plugin `{input_content_plugin_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
        # run user input content plugin
        if input_content_plugin_func and user_input:
            messages_copy[-1]["content"] = input_content_plugin_func(user_input)
        try:
            del CONTENT_PLUGIN
        except:
            pass
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
        possible_agent_file_path_1 = os.path.join(PACKAGE_PATH, "agent", f"{agent_object}.py")
        possible_agent_file_path_2 = os.path.join(TOOLMATE_PATH, "agent", f"{agent_object}.py")
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
            try:
                exec(agent_object, globals())
                agent_func = AGENT_FUNCTION
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
        try:
            del AGENT_FUNCTION
        except:
            pass
    # handle given system message(s)
    if system and not agent_response:
        if isinstance(system, list):
            system_instruction = system.pop(0)
        else: # a string instead
            system_instruction = system
            system = []
        # check if it is a predefined system message built-in with this SDK
        possible_system_file_path_1 = os.path.join(PACKAGE_PATH, "systems", f"{system_instruction}.md")
        possible_system_file_path_2 = os.path.join(TOOLMATE_PATH, "systems", f"{system_instruction}.md")
        if system_instruction is None:
            pass
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
        if system_instruction:
            original_system = updateSystemMessage(messages_copy, system_instruction)
    # handle given predefined context(s)
    if context and not agent_response:
        if isinstance(context, list):
            context_content = context.pop(0)
        else: # a string instead
            context_content = context
            context = []
        # check if it is a predefined context built-in with this SDK
        possible_context_file_path_1 = os.path.join(PACKAGE_PATH, "contexts", f"{context_content}.md")
        possible_context_file_path_2 = os.path.join(TOOLMATE_PATH, "contexts", f"{context_content}.md")
        if context_content is None:
            pass
        elif os.path.isfile(possible_context_file_path_1):
            context_file_content = readTextFile(possible_context_file_path_1)
            if context_file_content:
                context_content = context_file_content
        elif os.path.isfile(possible_context_file_path_2):
            context_file_content = readTextFile(possible_context_file_path_2)
            if context_file_content:
                context_content = context_file_content
        elif os.path.isfile(context_content): # context_content itself is a valid filepath
            context_file_content = readTextFile(context_content)
            if context_file_content:
                context_content = context_file_content
        if context_content:
            messages_copy[-1]["content"] = context_content + messages_copy[-1]["content"]
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
        possible_tool_file_path_1 = os.path.join(PACKAGE_PATH, "tools", f"{tool_object}.py")
        possible_tool_file_path_2 = os.path.join(TOOLMATE_PATH, "tools", f"{tool_object}.py")
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
            try:
                exec(tool_object, globals())
                tool_system = TOOL_SYSTEM
                schema = TOOL_SCHEMA
                func = TOOL_FUNCTION
                if tool_system:
                    chat_system = updateSystemMessage(messages_copy, tool_system)
            except Exception as e:
                print(f"Failed to execute tool `{tool_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())

    # check if it is last request
    is_last_request = True if not follow_up_prompt and not system and not context and not tool and not agent and not input_content_plugin and not output_content_plugin and not prefill else False

    # deep copy schema avoid modifying the original one
    schemaCopy = None if schema is None else deepcopy(schema)
    # run LLM
    if agent_response is not None:
        if stream and stream_events_only and is_last_request:
            return agent_response
        else:
            messages_copy = agent_response
            output = agent_response[-1].get("content", "")
    elif schemaCopy is not None: # structured output or function calling; allow schema to be an empty dict
        dictionary_output = {} if not schemaCopy else getDictionaryOutput(
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
                function_response = func() if not dictionary_output else func(**dictionary_output) # returned response can be either 1) an empty string: no chat extension 2) a non-empty string: chat extension 3) none: errors encountered in executing the function
                function_text_output = terminal_output.getvalue() # capture the function text output for function calling without chat extension
            except:
                function_response = None # due to unexpected errors encountered in executing the function; fall back to regular completion
            # Restore the original stdout
            sys.stdout = old_stdout
            # handle function response
            if function_response is None or function_response: # fall back to regular completion if function_response is None; chat extension if function_response
                if function_response:
                    # added function response as context to the original prompt
                    addContextToMessages(messages_copy, function_response)
                return generate(
                    messages_copy,
                    backend,
                    model=model,
                    model_keep_alive=model_keep_alive,
                    system=None if function_response else system,
                    context=None if function_response else context,
                    follow_up_prompt=None if function_response else follow_up_prompt,
                    input_content_plugin=None if function_response else given_input_content_plugin,
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
        try:
            del TOOL_SYSTEM
        except:
            pass
        try:
            del TOOL_SCHEMA
        except:
            pass
        try:
            del TOOL_FUNCTION
        except:
            pass
        if print_on_terminal:
            print(output)
    else: # regular completion
        if backend == "anthropic":
            completion = AnthropicLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "azure":
            completion = AzureLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_endpoint=api_endpoint,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "custom":
            completion = OpenaiCompatibleLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
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
            completion = DeepseekLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
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
            completion = GenaiLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_project_id=api_project_id,
                api_service_location=api_service_location,
                **kwargs
            )
        elif backend == "github":
            completion = GithubLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "googleai":
            completion = GoogleaiLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "groq":
            completion = GroqLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
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
            completion = LlamacppLLM.getChatCompletion(
                messages_copy,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_endpoint=api_endpoint,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "mistral":
            completion = MistralLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                prefill=prefill_content,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "ollama":
            completion = OllamaLLM.getChatCompletion(             
                messages_copy,
                model=model,
                model_keep_alive=model_keep_alive,
                schema=schemaCopy,
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
            completion = OpenaiLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stop,
                stream=stream,
                api_key=api_key,
                api_timeout=api_timeout,
                **kwargs
            )
        elif backend == "xai":
            completion = XaiLLM.getChatCompletion(
                messages_copy,
                model=model,
                schema=schemaCopy,
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

    # handle assistant output content plugin(s)
    output_content_plugin_func = None
    if output_content_plugin:
        if isinstance(output_content_plugin, list):
            output_content_plugin_object = output_content_plugin.pop(0)
        else: # a string instead
            output_content_plugin_object = output_content_plugin
            output_content_plugin = []
        output_content_plugin_name = output_content_plugin_object[:20]
        # check if it is a predefined plugin message built-in with this SDK
        possible_output_content_plugin_file_path_1 = os.path.join(PACKAGE_PATH, "plugins", f"{output_content_plugin_object}.py")
        possible_output_content_plugin_file_path_2 = os.path.join(TOOLMATE_PATH, "plugins", f"{output_content_plugin_object}.py")
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
            try:
                exec(output_content_plugin_object, globals())
                output_content_plugin_func = CONTENT_PLUGIN
            except Exception as e:
                print(f"Failed to execute output content plugin `{output_content_plugin_name}`! An error occurred: {e}")
                if DEVELOPER_MODE:
                    print(traceback.format_exc())
        # run output plugin
        if output_content_plugin_func and output:
            output = output_content_plugin_func(output)
        try:
            del CONTENT_PLUGIN
        except:
            pass

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
        # check if it is a predefined follow_up_prompt built-in with this SDK
        possible_follow_up_prompt_file_path_1 = os.path.join(PACKAGE_PATH, "prompts", f"{follow_up_prompt_content}.md")
        possible_follow_up_prompt_file_path_2 = os.path.join(TOOLMATE_PATH, "prompts", f"{follow_up_prompt_content}.md")
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
        messages_copy.append({"role": "user", "content": follow_up_prompt_content})
        return generate(
            messages=messages_copy,
            backend=backend,
            model=model,
            model_keep_alive=model_keep_alive,
            system=system,
            context=context,
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
    return messages_copy

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
        return AnthropicLLM.getDictionaryOutput(
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
        return AzureLLM.getDictionaryOutput(
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
    elif backend == "custom":
        return OpenaiCompatibleLLM.getDictionaryOutput(
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
        return DeepseekLLM.getDictionaryOutput(
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
        return GenaiLLM.getDictionaryOutput(
            messages,
            schema,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            api_key=api_key,
            api_project_id=api_project_id,
            api_service_location=api_service_location,
            **kwargs
        )
    elif backend == "github":
        return GithubLLM.getDictionaryOutput(
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
        return GoogleaiLLM.getDictionaryOutput(
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
        return GroqLLM.getDictionaryOutput(
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
        return LlamacppLLM.getDictionaryOutput(
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
        return MistralLLM.getDictionaryOutput(
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
        return OllamaLLM.getDictionaryOutput(
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
        return OpenaiLLM.getDictionaryOutput(
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
        return XaiLLM.getDictionaryOutput(
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