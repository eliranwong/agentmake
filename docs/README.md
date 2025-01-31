# Usage

This SDK is designed to provide a single function for interacting with all AI backends, delivering a unified experience for generating AI responses. The main APIs are provided with the function `generate` located in this [file](https://github.com/eliranwong/agentmake/blob/main/agentmake/__init__.py#L28). Find its description below:

```
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
        run all specified plugins to process user input content on every single turn
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
        run all specified plugins to process assistant output content on every single turn
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
```

# More

[Custom Content](https://github.com/eliranwong/agentmake/blob/main/docs/custom_content.md)

[Create tools](https://github.com/eliranwong/agentmake/blob/main/docs/create_tools.md)

[Create agents](https://github.com/eliranwong/agentmake/blob/main/docs/create_agents.md)

[Create plugins](https://github.com/eliranwong/agentmake/blob/main/docs/create_plugins.md)