# AgentMake AI

AgentMake AI: a software developement kit for developing agentic AI applications that support 16 AI backends and work with 7 agentic components, such as tools and agents. (Developer: Eliran Wong)

Supported backends: anthropic, azure, cohere, custom, deepseek, genai, github, googleai, groq, llamacpp, mistral, ollama, openai, vertexai, xai

# Audio Introduction

[![Watch the video](https://img.youtube.com/vi/JyJxrvrJyqM/maxresdefault.jpg)](https://youtu.be/JyJxrvrJyqM)

[9-min introduction](https://youtu.be/JyJxrvrJyqM) [24-min introduction](https://youtu.be/NMmuuWm2ixY)

# Sibling Projects

This SDK incorporates the best aspects of our favorite projects, [LetMeDoIt AI](https://github.com/eliranwong/letmedoit), [Toolmate AI](https://github.com/eliranwong/toolmate) and [TeamGen AI](https://github.com/eliranwong/teamgenai), to create a library aimed at further advancing the development of agentic AI applications.

# Supported Platforms

Windows, macOS, Linux, ChromeOS, [Android](https://github.com/eliranwong/agentmake/blob/main/docs/android_termux_setup.md)

# Supported backends

`anthropic` - [Anthropic API](https://console.anthropic.com/) [[docs](https://docs.anthropic.com/en/home)]

`azure` - [Azure OpenAI Service API](https://ai.azure.com/github) [[docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)]

`azure_any` - [Azure AI Inference API](https://ai.azure.com/github) [[docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)]

`cohere` - [Cohere API](https://cohere.com/) [[docs](https://docs.cohere.com/docs/the-cohere-platform)]

`custom` - any openai-compatible backends that support function calling

`deepseek` - [DeepSeek API](https://platform.deepseek.com/) [[docs](https://api-docs.deepseek.com/)]

`genai` - [Vertex AI](https://cloud.google.com/vertex-ai) or [Google AI](https://ai.google.dev/) [[docs](https://github.com/googleapis/python-genai)]

`github` - [Azure OpenAI Service via Github Token](https://docs.github.com/en/github-models/prototyping-with-ai-models#experimenting-with-ai-models-using-the-api) [[docs](https://github.com/marketplace/models/azure-openai/gpt-4o)]

`github_any` - [Azure AI Inference via Github Token](https://ai.azure.com/github) [[docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)]

`googleai` - [Google AI](https://ai.google.dev/) [[docs](https://ai.google.dev/gemini-api/docs/openai)]

`groq` - [Groq Cloud API](https://console.groq.com) [[docs](https://console.groq.com/docs/overview)]

`llamacpp` - [Llama.cpp Server](https://github.com/ggml-org/llama.cpp) [[docs](https://github.com/ggml-org/llama.cpp#llama-server)] - [local setup](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md) required

`mistral` - [Mistral API](https://console.mistral.ai/api-keys/) [[docs](https://docs.mistral.ai/)]

`ollama` - [Ollama](https://ollama.com/) [[docs](https://github.com/ollama/ollama-python)] - [local setup](https://ollama.com/download) required

`openai` - [OpenAI API](https://platform.openai.com/) [[docs](https://platform.openai.com/)]

`vertexai` - [Vertex AI](https://cloud.google.com/vertex-ai) [[docs](https://github.com/googleapis/python-genai)]

`xai` - [XAI API](https://x.ai/api) [[docs](https://docs.x.ai/docs/overview)]

For simplicity, `agentmake` uses `ollama` as the default backend, if parameter `backend` is not specified. Ollama models are automatically downloaded if they have not already been downloaded. Users can change the default backend by modifying environment variable `DEFAULT_AI_BACKEND`.

# Introducing Agentic Components

`agentmake` is designed to work with seven kinds of components for building agentic applications:

1. `system` - System messages are crucial for defining the roles of the AI agents and guiding how AI agents interact with users. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/systems). `agentmake` supports the use of `fabric` patterns as `system` components for running `agentmake` function or CLI options [READ HERE](https://github.com/eliranwong/agentmake#fabric-integration).

2. `instruction` - Predefined instructions that are added to users' prompts as prefixes, before they are passed to the AI models. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/instructions). `agentmake` supports the use of `fabric` patterns as `instruction` components for running `agentmake` function or CLI options [READ HERE](https://github.com/eliranwong/agentmake#fabric-integration).

3. `input_content_plugin` - Input content plugins process or transform user inputs before they are passed to the AI models. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins).

4. `output_content_plugin` - Output content plugins process or transform assistant responses after they are generated by AI models. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins).

5. `tool` - Tools take simple structured actions in response to users' requests, with the use of `schema` and `function calling`. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/tools).

6. `agent` - Agents are agentic applications automate multiple-step actions or decisions, to fulfill complicated requests.  They can be executed on their own or integrated into an agentic workflow, supported by `agentmake`, to work collaboratively with other agents or components. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/agents).

7. `follow_up_prompt` - Predefined prompts that are helpful for automating a series of follow-up responses after the first assistant response is generated. Check out our [examples](https://github.com/eliranwong/agentmake/tree/main/agentmake/prompts).

# Built-in and Custom Agentic Components

`agentmake` supports both built-in agentic components, created by our developers or contributors, and cutoms agentic components, created by users to meet their own needs.

## Built-in Agentic Components

Built-in agents components are placed into the following six folders inside the `agentmake` folders:

`agents`, `instructions`, `plugins`, `prompts`, `systems`, `tools`

To use the built-in components, you only need to specify the component filenames, without parent paths or file extensions, when you run the `agentmake` signature function or CLI options.

## Custom Agentic Components

`agentmake` offers two options for users to use their custom components.

Option 1: Specify the full file path of inidividual components

Given the fact that each component can be organised as a single file, to use their own custom components, users only need to specify the file paths of the components they want to use, when they run the `agentmake` signature function or CLI options.

Option 2: Place custom components into `agentmake` user directory

The default `agentmake` user directory is `~/agentmake`, i.e. a folder named `agentmake`, created under user's home directory. Uses may define their own path by modifying the environment variable `AGENTMAKE_USER_DIR`.

After creating a folder named `agentmake` under user directory, create six sub-folders in it, according to the following names and place your custom components in relevant folders, as we do with our built-in components.

If you organize the custom agentic components in this way, you only need to specify the component filenames, without parent paths or file extensions, when you run the `agentmake` signature function or CLI options.

## Priorities

In cases where a built-in tool and a custom tool have the same name, the custom tool takes priority over the built-in one. This allows for flexibility, enabling users to copy a built-in tool, modify its content, and retain the same name, thereby effectively overriding the built-in tool.

# Agentic Application that Built on AgentMake AI

Below are a few examples to illustrate how easy to build agentic applications with AgentMake AI.

## Example 1 - ToolMate AI

[ToolMate AI version 2.0](https://github.com/eliranwong/toolmate) is completely built on AgentMake AI, based on the following two agentic workflows, to reolve both complex and simple tasks.

To resolve complex tasks:

<img width="794" alt="Image" src="https://github.com/user-attachments/assets/c79efda7-5da5-41fe-af67-e48ea32e5af6" />

To resolve simple tasks:

<img width="881" alt="Image" src="https://github.com/user-attachments/assets/7809fa98-83e1-4a82-af80-2706895d4985" />

## Example 2 - TeamGen AI

[TeamGenAI AI version 2.0](https://github.com/eliranwong/teamgenai) is completely built on AgentMake AI, based on the following agentic workflow, to create multi-agents for collaboration on resolving user requests.

<img width="832" alt="Image" src="https://github.com/user-attachments/assets/cf27cf97-ea7a-42bd-a050-3663064dc07d" />

## Example 3 - LetMeDoIt AI

[LetMeDoIt AI version 3.0](https://github.com/eliranwong/letmedoit) is completely built on AgentMake AI, based on the following agentic workflow, to resolve tasks with default and custom tools.

<img width="708" alt="Image" src="https://github.com/user-attachments/assets/5a7240ae-dd17-48a6-b4e2-712309b4b130" />

# Installation

## Disclaimer

In response to your instructions, AgentMake AI is capable of applying tools to generate files or make changes on your devices. Please use it with your sound judgment and at your own risk. We will not take any responsibility for any negative impacts, such as data loss or other issues.

## Basic:

> pip install --upgrade agentmake

Basic installation supports all AI backends mentioned above, except for `vertexai`.

## Extras:

To install the web UI `AgentMake Studio`:

> pip install --upgrade "agentmake[studio]"

We support Vertex AI via [Google GenAI SDK](https://pypi.org/project/google-genai/).  As this package supports most platforms, except for Android Termux, we separate this package `google-genai` as an extra.  To support Vertex AI with `agentmake`, install with running:

> pip install --upgrade "agentmake[genai]"

## Virtual Environment and PATH Setup

It is recommended to set up a virtual environment for running AgentMake AI, read:

Read https://github.com/eliranwong/agentmake/blob/main/docs/add_path.md

## Remarks

It is recommended not to install `agentmake` inside the directory `~/agentmake`, as `~/agentmake` is used by default for placing user custom content.

# Usage

This SDK is designed to offer a single signature function `agentmake` for interacting with all AI backends, delivering a unified experience for generating AI responses. The main APIs are provided with the function `agentmake` located in this [file](https://github.com/eliranwong/agentmake/blob/main/agentmake/__init__.py#L71).

Find documentation at https://github.com/eliranwong/agentmake/blob/main/docs/README.md

# Examples

The following examples assumes [Ollama](https://ollama.com/) is [installed](https://ollama.com/download) as the default backend.

To import:

> from agentmake import agentmake

To run, e.g.:

> agentmake("What is AI?")

To work with parameter `tool`, e.g.:

> agentmake("What is AgentMake AI?", tool="search/google")

> agentmake("How many 'r's are there in the word 'strawberry'?", tool="magic")

> agentmake("What time is it right now?", tool="magic")

> agentmake("Open github.com in a web browser.", tool="magic")

> agentmake("Convert file 'music.wav' into mp3 format.", tool="magic")

> agentmake("Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work.", tool="email/gmail")

To work with parameters `input_content_plugin` and `output_content_plugin`, e.g.:

> agentmake("what AI model best", input_content_plugin="styles/british_english", output_content_plugin="chinese/translate_tc_deepseek", stream=True)

To work with `plugin` that is placed in a sub-folder, e.g.:

> agentmake("你好吗？", output_content_plugin="chinese/convert_simplified")

To automate prompt engineering:

> agentmake("what best LLM training method", system="auto", input_content_plugin="improve_prompt")

To work with parameter `system`, `instruction`, `follow_up_prompt`, e.g.:

> agentmake("Is it better to drink wine in the morning, afternoon, or evening?", instruction="reflect", stream=True)

> agentmake("Is it better to drink wine in the morning, afternoon, or evening?", instruction="think", follow_up_prompt=["review", "refine"], stream=True)

> agentmake("Provide a detailed introduction to generative AI.", system=["create_agents", "assign_agents"], follow_up_prompt="Who is the best agent to contribute next?", stream=True, model="llama3.3:70b")

To work with parameter `agent`, e.g.:

> agentmake("Write detailed comments about the works of William Shakespeare, focusing on his literary contributions, dramatic techniques, and the profound impact he has had on the world of literature and theatre.", agent="teamwork", stream=True, model="llama3.3:70b")

> agentmake("Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work", agent="auto_tool_selection")

> agentmake("Write brief introductions to the Gospels of Mark, Luke, and John, and save each introduction in a separate file, placing them in three different folders named after the respective Gospel book.", agent="super", backend="azure")

Remarks: the agent `super` is designed to resolve complex tasks that involve multiple steps, tools and agents. It fully automates task plan, tool selection, execution and quality control. Read more at https://github.com/eliranwong/agentmake/blob/main/examples/automate_task_execution.py and https://github.com/eliranwong/agentmake/blob/main/examples/automate_task_execution_tools_specified.md

To specify an AI backend:

> agentmake("What is Microsoft stock price today?", tool="search/finance", backend="azure")

To work collaboratively with different backends, e.g.

> messages = agentmake("What is the most effective method for training AI models?", backend="openai")

> messages = agentmake(messages, backend="googleai", follow_up_prompt="Can you give me some different options?")

> messages = agentmake(messages, backend="xai", follow_up_prompt="What are the limitations or potential biases in this information?")

> agentmake(messages, backend="mistral", follow_up_prompt="Please provide a summary of the discussion so far.")

As you may see, the `agentmake` function returns the `messages` list, which is passed to the next `agentmake` function in turns.

Therefore, it is very simple to create a chatbot application, you can do it as few as five lines or less, e.g.:

> messages = [{"role": "system", "content": "You are an AI assistant."}]

> user_input = "Hello!"

> while user_input:

>     messages = agentmake(messages, follow_up_prompt=user_input, stream=True)

>     user_input = input("Enter your query:\n(enter a blank entry to exit)\n>>> ")

Read our [web UI chatbot example](https://github.com/eliranwong/agentmake/blob/main/examples/webui_with_mesop.py) at:

https://github.com/eliranwong/agentmake/blob/main/examples/webui_with_mesop.py

You may take a look at out our built-in components for more ideas:

[systems](https://github.com/eliranwong/agentmake/tree/main/agentmake/systems)

[instructions](https://github.com/eliranwong/agentmake/tree/main/agentmake/instructions)

[plugins](https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins)

[tools](https://github.com/eliranwong/agentmake/tree/main/agentmake/tools).

[agents](https://github.com/eliranwong/agentmake/tree/main/agentmake/agents).

[prompts](https://github.com/eliranwong/agentmake/tree/main/agentmake/prompts).

# Web UI Studio

![Image](https://github.com/user-attachments/assets/3e8dbe05-855d-4c0a-a581-bc262443b452)

To install:

> pip install --upgrade "agentmake[studio]"

To run the AgentMake Studio:

> agentmakestudio

Then, open `http://localhost:32123` in a web browser.

Read more at: https://github.com/eliranwong/agentmakestudio

# CLI Options

Command CLI are designed for quick run of AI features.

To work with CLI options without activating virtual environment, read https://github.com/eliranwong/agentmake/blob/main/docs/add_path.md

Check for CLI options, run:

> agentmark -h

Two shortcut commands:

`ai` == `agentmake`

`aic` == `agentmake -c` with chat features enabled

The available CLI options use the same parameter names as the `agentmake` function for AI backend configurations, to offer users a unified experience. Below are some CLI examples, that are equivalent to some of the examples mentioned above:

> ai What is AI?

> ai What is AgentMake AI --tool search/google

> ai Convert file music.wav into mp3 format. --tool task

> ai Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work --tool email/gmail

> ai Extract text from image file sample.png. --tool=ocr/openai

> ai What is Microsoft stock price today? -t search/finance -b azure

> ai what AI model best --input_content_plugin styles/british_english --output_content_plugin chinese/translate_tc_deepseek

> ai what best LLM training method --system auto --input_content_plugin improve_prompt

> ai 你好吗？ --output_content_plugin=chinese/convert_simplified

> ai Is it better to drink wine in the morning, afternoon, or evening? --instruction think --follow_up_prompt review --follow_up_prompt refine

> ai Write detailed comments about the works of William Shakespeare, focusing on his literary contributions, dramatic techniques, and the profound impact he has had on the world of literature and theatre --agent teamwork --model "llama3.3:70b"

> ai -a auto_tool_selection "Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work"

> ai -a super -b azure "Write brief introductions to the Gospels of Mark, Luke, and John, and save each introduction in a separate file, placing them in three different folders named after the respective Gospel book."

## More Examples

More examples at https://github.com/eliranwong/agentmake/tree/main/examples

## Work with Text Selection and Clipboard

CLI options allow you to work with selected or copied text easily.

A setup example on Linux: https://github.com/eliranwong/AMD_iGPU_AI_Setup#test-with-selected-or-copied-text

A setup example on macOS: https://github.com/eliranwong/agentmake/blob/main/docs/work_with_text_selection.md#macos-setup

## CLI for Testing

CLI options are handy for testing, e.g. simply use a newly developed `tool` file with `-t` option and run:

> ai What is AgentMake AI? -t ~/my_folder/perplexica.py

# Interactive Mode

AgentMake AI offers a simple interactive mode, run:

> ai -i

![Image](https://github.com/user-attachments/assets/e4872498-0cef-48e7-a550-55c0c4234929)

It works with selected or copied text for desktop integration, read https://github.com/eliranwong/agentmake/blob/main/docs/work_with_text_selection.md

# AI Backends Configurations

For quick start, run:

> agentmake -ec

For more options:

To use `ollama` as the default backend, you need to [download and install](https://ollama.com/download) Ollama. To use backends other than Ollama, you need to use your own API keys.  There are a few options you may configure the AI backends to work with `agentmake`.

## Option 1 - Use the `agentmake` function

Specify AI backend configurations as [parameters](https://github.com/eliranwong/agentmake/tree/main/docs#usage) when you run the `agentmake` signature function `agentmake`.

Setting configurations via option 1 overrides the default configurations set by option 2 and option 3, but the overriding is effective only when you run the function, with the specified configurations. Default configurations described below in option 2 and 3 still apply next time when you run the `agentmake` function, without specifying the AI backend parameters. This gives you flexibility to specify different settings in addition to the default ones.

## Option 2 - Export individual environment variables

You may manually export individual environment variables listed in https://github.com/eliranwong/agentmake/blob/main/agentmake.env

## Option 3 - Export default environment variables once for all

1.  Make a copy of the [file](https://github.com/eliranwong/agentmake/blob/main/agentmake/agentmake.env) `agentmake.env`, located in the package directory, as:

either `~/agentmake/agentmake.env`

```
cd agentmake # where you installed agentmake
cp agentmake.env ~/agentmake/agentmake.env
```

or `<package_directory>/.env`:

```
cd agentmake # where you installed agentmake
cp agentmake.env .env
```

2. Edit the file manually with a text editor, e.g.

> etextedit ~/agentmake/agentmake.env

3. Save the changes

The changes apply next time when you run `agentmake` function or cli.

## Option 4 - Run built-in CLI option

Use built-in `agentmake` cli option to edit the variables:

> agentmake -ec

What does this command do?

* It automatically makes a copy of [file](https://github.com/eliranwong/agentmake/blob/main/agentmake/agentmake.env) `agentmake.env` and save it as `<package_directory>/.env` if both `<package_directory>/.env` and `~/agentmake/agentmake.env` do not exist.
* It uses the text editor, specified in `DEFAULT_TEXT_EDITOR`, to open the configuration file `~/agentmake/agentmake.env` if it exists or `<package_directory>/.env` if `~/agentmake/agentmake.env` does not exist.

Remember to save your changes to make them effective.

## Note about Ollama AI Setup on Linux

Configure Ollama, run:

> sudo nano /etc/systemd/system/ollama.service

Add the following three lines at the end of the [Service] session:

```
Environment="OLLAMA_HOST=0.0.0.0"
```

Reload and restart Ollama service, run:

> sudo systemctl daemon-reload

> sudo systemctl restart ollama

To work with AgentMake CLI option `--get_model`, add user to user group `ollama` for access of Ollama model directory:

> sudo usermod -a -G ollama $LOGNAME

> sudo reboot

## Note about Azure AI Setup

An easy way to deploy AI models via Azure service:

1. Sign in https://ai.azure.com/github
2. All resources > Create New
3. Overview > copy an API key, Azure OpenAI Service and Azure AI inference endpoints

* Use Azure OpenAI Service endpoint for running OpenAI models; the endpoint should look like https://resource_name.openai.azure.com/

* Use Azure AI inference endpoint for running DeepSeek-R1 and Phi-4; the endpoint should look like https://resource_name.services.ai.azure.com/models

To configure AgentMake AI, run:

> ai -ec

You can check the configurable variables at https://github.com/eliranwong/agentmake/blob/main/agentmake/agentmake.env

## Note about Vertex AI Setup

Make sure the extra package `genai` is installed with the command mentioned above:

> pip install --upgrade "agentmake[genai]"

To configure, run:

> ai -ec

Enter the path of your Google application credentials JSON file as the value of `VERTEXAI_API_KEY`. You need to specify your project ID and service location, in the configurations, as well. e.g.:

```
VERTEXAI_API_KEY=~/agentmake/google_application_credentials.json
VERTEXAI_API_PROJECT_ID=my_project_id
VERTEXAI_API_SERVICE_LOCATION=us-central1
```

Remarks: If `VERTEXAI_API_KEY` is blank, `~/agentmake/google_application_credentials.json` is used by default.

To test Gemini 2.0 with Vertex AI, e.g.:

> ai -b vertexai -m gemini-2.0-flash Hi!

## Remarks

1. Please do not edit the file `agentmake.env`, that is located in the package directory, directly, as it is restored to its default values upon each upgrade.  It is recommended to make a copy of it and edit the copied file.
2. Multiple API keys are supported for running backends `cohere`, `github`, `groq` and `mistral`. You may configure API keys for these backend in the `.env` file by using commas `,` as separators, e.g. `COHERE_API_KEY=cohere_api_key_1,cohere_api_key_2,cohere_api_key_3`

# Fabric Integration

`fabric` is a fantastic [third-party project](https://github.com/danielmiessler/fabric/tree/main/patterns) that offers [a great collection of patterns](https://github.com/danielmiessler/fabric/tree/main/patterns).

`agentmake` supports the use of `fabric` patterns as entries for the `system` or `instruction` parameters when running the `agentmake` signature function or CLI options.

To use a fabric pattern in `agentmake`:

1. Install [fabric](https://github.com/danielmiessler/fabric/tree/main/patterns)
2. Specify a fabric pattern in `agentmake` parameter `system` or `instruction`, by prefixing the selected pattern with `fabric.`

> agentmake("The United Kingdom is a Christian country.", tool="search/searxng", system="fabric.analyze_claims")

# Local Backends with GPU Acceleration

Both local backends `ollama` and `llamacpp` support GPU accelerations.
