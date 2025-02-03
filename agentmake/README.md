# AgentMake AI

AgentMake AI: a software developement kit for developing agentic AI applications that support 14 AI backends and integrate tools and agents. (Developer: Eliran Wong)

Supported backends: anthropic, azure, cohere, custom, deepseek, genai, github, googleai, groq, llamacpp, mistral, ollama, openai, vertexai, xai

# Sibling Projects

This SDK incorporates the best aspects of our favorite projects, [LetMeDoIt AI](https://github.com/eliranwong/letmedoit), [Toolmate AI](https://github.com/eliranwong/toolmate) and [TeamGen AI](https://github.com/eliranwong/teamgenai), to create a library aimed at further advancing the development of agentic AI applications.

# Supported backends

`anthropic` - [Anthropic API](https://console.anthropic.com/)

`azure` - [Azure OpenAI API](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference)

`cohere` - [Cohere API](https://docs.cohere.com/docs/the-cohere-platform)

`custom` - any openai-compatible backends that support function calling

`deepseek` - [DeepSeek API](https://platform.deepseek.com/)

`genai` - [Vertex AI](https://cloud.google.com/vertex-ai) or [Google AI](https://ai.google.dev/)

`github` - [Github API](https://docs.github.com/en/github-models/prototyping-with-ai-models#experimenting-with-ai-models-using-the-api)

`googleai` - [Google AI](https://ai.google.dev/)

`groq` - [Groq Cloud API](https://console.groq.com)

`llamacpp` - [Llama.cpp Server](https://github.com/ggerganov/llama.cpp) - [locat setup](https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md) required

`mistral` - [Mistral API](https://console.mistral.ai/api-keys/)

`ollama` - [Ollama](https://ollama.com/) - [local setup](https://ollama.com/download) required

`openai` - [OpenAI API](https://platform.openai.com/)

`vertexai` - [Vertex AI](https://cloud.google.com/vertex-ai)

`xai` - [XAI API](https://x.ai/api)

For simplicity, `agentmake` uses `ollama` as the default backend, if parameter `backend` is not specified. Ollama models are automatically downloaded if they have not already been downloaded. Users can change the default backend by modifying environment variable `DEFAULT_AI_BACKEND`.

# Installation

Basic:

> pip install --upgrade agentmake

Basic installation supports all AI backends mentioned above, except for `vertexai`.

Extras:

We support Vertex AI via [Google GenAI SDK](https://pypi.org/project/google-genai/).  As this package supports most platforms, except for Android Termux, we separate this package `google-genai` as an extra.  To support Vertex AI with `agentmake`, install with running:

> pip install --upgrade agentmake[genai]

# Usage

This SDK is designed to offer a single function `generate` for interacting with all AI backends, delivering a unified experience for generating AI responses. The main APIs are provided with the function `generate` located in this [file](https://github.com/eliranwong/agentmake/blob/main/agentmake/__init__.py#L29).

Find documentation at https://github.com/eliranwong/agentmake/blob/main/docs/README.md

# Examples

The following examples assumes [Ollama](https://ollama.com/) is [installed](https://ollama.com/download) as the default backend.

To import:

> from agentmake import generate

To generate, e.g.:

> generate("What is AI?")

To work with parameter `tool`, e.g.:

> generate("What is ToolMate AI?", tool="search_google")

> generate("How many 'r's are there in the word 'strawberry'?", tool="task")

> generate("What time is it right now?", tool="task")

> generate("Open github.com in a web browser.", tool="task")

> generate("Convert file 'music.wav' into mp3 format.", tool="task")

> generate("Send an email to Eliran Wong at eliran.wong@domain.com to express my gratitude for his work.", tool="send_gmail")

To work with parameters `input_content_plugin` and `output_content_plugin`, e.g.:

> generate("what AI model best", input_content_plugin="improve_writing", output_content_plugin="translate_into_chinese", stream=True)

To work with parameter `system`, `context`, `follow_up_prompt`, e.g.:

> generate("Is it better to drink wine in the morning, afternoon, or evening?", context="reflect", stream=True)

> generate("Is it better to drink wine in the morning, afternoon, or evening?", context="think", follow_up_prompt=["review", "refine"], stream=True)

> generate("Provide a detailed introduction to generative AI.", system=["create_agents", "assign_agents"], follow_up_prompt="Who is the best agent to contribute next?", stream=True, model="llama3.3:70b")

To work with parameter `agent`, e.g.:

> generate("Write detailed comments about the works of William Shakespeare, focusing on his literary contributions, dramatic techniques, and the profound impact he has had on the world of literature and theatre.", agent="teamgenai", stream=True, model="llama3.3:70b")

To work collaboratively with different backends, e.g.

> messages = generate("What is the most effective method for training AI models?", backend="openai")

> messages = generate(messages, backend="googleai", follow_up_prompt="Can you give me some different options?")

> messages = generate(messages, backend="xai", follow_up_prompt="What are the limitations or potential biases in this information?")

> generate(messages, backend="mistral", follow_up_prompt="Please provide a summary of the discussion so far.")


As you may see, the `generate` function returns the `messages` list, which is passed to the next `generate` function in turns.

Therefore, it is very simple to create a chatbot application, you can do it as few as five lines or less, e.g.:

> messages = [{"role": "system", "content": "You are an AI assistant."}]

> user_input = "Hello!"

> while user_input:

>     messages = generate(messages, follow_up_prompt=user_input, stream=True)

>     user_input = input("Enter your query:\n(enter a blank entry to exit)\n>>> ")

These are just a few simple and straightforward examples.  You may find more examples at:

https://github.com/eliranwong/agentmake/tree/main/agentmake/examples

# AI Backends Configurations

## Option 1 - Use the `generate` function

Specify AI backend configurations as [parameters](https://github.com/eliranwong/agentmake/tree/main/docs#usage) when you run the `agentmake` signature function `generate`.

Setting configurations via option 1 overrides the default configurations set by option 2 and option 3, but the overriding is effective only when you run the function, with the specified configurations. Default configurations described below in option 2 and 3 still apply next time when you run the `generate` function, without specifying the configurations. This gives you flexibility to specify different settings in addition to the default ones.

## Option 2 - Export individual environment variables

You may manually export individual environment variables listed in https://github.com/eliranwong/agentmake/blob/main/agentmake.env

## Option 3 - Export default environment variables once for all

You may edit a copy of `agentmake.env`, e.g.

```
cd agentmake
cp agentmake.env .env
nano .env
```

To load the configurations:

```
from agentmake import load_configurations
load_configurations()
```

To use a custom path, e.g.:

```
cd agentmake
cp agentmake.env my_path.env
nano my_path.env
```

Specify the path of the `.env` file in the `load_configurations` function, e.g.:

```
from agentmake import load_configurations
load_configurations("my_path.env")
```

Remarks: Avoid editing the file `agentmake.env` directly, as it is restored to its default values upon each upgrade.  It is recommended to make a copy of it and edit the copied file.

# TODO

* add documentation about tool creation
* add examples
* convert availble ToolMate AI tools into tools that runable with this SDK
* add built-in system messages
* add built-in predefined contexts
* add built-in prompts
* add cli options for running simple inference, tools or testing
* improve code generation handling
* add backend support of Cohere API
