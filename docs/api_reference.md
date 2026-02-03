# API Reference

The core functionality of AgentMake is exposed through the `agentmake` function. This function provides a unified interface for interacting with various AI backends.

## `agentmake`

```python
from agentmake import agentmake
```

Generates an AI assistant response.

### parameters

#### `messages`
**Type:** `Union[List[Dict[str, str]], str]`

User request or messages containing user request.
- Accepts either a single string or a list of dictionaries.
- Use a single string to specify user request without chat history.
- Use a list of dictionaries to provide the ongoing interaction between user and assistant.
- When a list is given:
    - Each dictionary in the list should contain keys `role` and `content`.
    - Specify the latest user request in the last item content.
    - List format example:
        ```python
        [
            {"role": "system", "content": "You are an AI assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hello! How can I assist you today?"},
            {"role": "user", "content": "What is generative AI?"}
        ]
        ```
- **Remarks:** If the last item is not a user message, one of the following is added as the user message:
    1. The first item of the list `follow_up_prompt` if there is one.
    2. Default follow-up prompt (value of environment variable `DEFAULT_FOLLOW_UP_PROMPT`).
    3. A single string "Please tell me more." if none of the above.

#### `backend`
**Type:** `Optional[str]`
**Default:** `"ollama"`

The AI backend to use.
**Supported backends:**
- `anthropic`
- `azure_anthropic`
- `azure_openai`
- `azure_cohere`
- `azure_deepseek`
- `azure_mistral`
- `azure_xai`
- `azure_sdk`
- `cohere`
- `custom`, `custom1`, `custom2`
- `deepseek`
- `genai`
- `github`, `github_any`
- `googleai`
- `groq`
- `llamacpp`
- `mistral`
- `ollama`
- `ollamacloud`
- `openai`
- `vertexai`
- `xai`

#### `model`
**Type:** `Optional[str]`
**Default:** `None`

The AI model name.
- Applicable to all backends **except** `llamacpp`.
- For `llamacpp`, specify a model file in the command line running the llama.cpp server.
- For `ollama`, the model is automatically downloaded if it is not in the downloaded model list.

#### `model_keep_alive`
**Type:** `Optional[str]`
**Default:** `None`

Time to keep the model loaded in memory. **Applicable to `ollama` only.**

#### `system`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

System message that defines how the model should generally behave and respond.
- Accepts a list of strings or a single string.
- Runs multi-turn inferences, looping through multiple system messages, if given as a list.
- Each item must be one of the following:
    1. File name (without extension) of a markdown file in `systems` folder under package directory.
    2. File name (without extension) of a markdown file in `systems` folder under user directory (`~/agentmake/systems`).
    3. A valid plain text file path.
    4. `"auto"` - automate generation of system message based on user request (saved at `~/agentmake/systems`).
    5. A string starting with `"role."` (e.g., `"role.Programmer"`) - automate generation of system message based on role (saved at `~/agentmake/systems/roles`).
    6. A string of the system message itself.
- **Fabric Integration:** Supports `fabric` patterns as system components. [Read More](https://github.com/eliranwong/agentmake#fabric-integration).

#### `instruction`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Predefined instruction added to the user prompt as a prefix.
- Accepts a list of strings or a single string.
- Runs multi-turn inferences, looping through multiple instructions, if given as a list.
- Each item must be one of the following:
    1. File name (without extension) of a markdown file in `instructions` folder under package directory.
    2. File name (without extension) of a markdown file in `instructions` folder under user directory (`~/agentmake/instructions`).
    3. A valid plain text file path.
    4. A string of the instruction.
- **Fabric Integration:** Supports `fabric` patterns.

#### `follow_up_prompt`
**Type:** `Optional[Union[List[str], str]]`
**Default:** `None`

Follow-up prompt used after an assistant message is generated.
- Accepts a list of strings or a single string.
- Runs multi-turn inferences, looping through multiple prompts, if given as a list.
- Options similar to `instruction` (file in `prompts` folder, file path, or string).
- **Remarks:** If the last item of `messages` is NOT a user message, the first follow-up prompt is used as the user message.

#### `input_content_plugin`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Plugins to process user input content.
- Accepts a list or single string.
- Runs all specified plugins on every single turn.
- Options:
    1. File name (without extension) of a python file in `plugins` folder (package or user dir).
    2. Valid plain text file path.
    3. A python script containing a `CONTENT_PLUGIN` variable (function object).

#### `output_content_plugin`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Plugins to process assistant output. Similar to `input_content_plugin` but acts on the response.
- Options: Same as `input_content_plugin`.
- Python script must contain `CONTENT_PLUGIN` variable.

#### `agent`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Agent that automates multi-turn work and decisions.
- Accepts a list or single string.
- Loops through agents if a list is given.
- Options:
    1. File name (without extension) of a python file in `agents` folder (package or user dir).
    2. Valid plain text file path.
    3. Python script containing `AGENT_FUNCTION` variable.
- **Remarks:** Parameters like `system`, `instruction`, `tool`, etc., are ignored for a single turn when `agent` is provided.

#### `tool`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Tool that calls a function in response.
- Accepts a list or single string.
- Loops through tools if a list is given.
- Options:
    1. File name (without extension) of a python file in `tools` folder (package or user dir).
    2. Valid plain text file path.
    3. Python script containing:
        - `TOOL_SCHEMA`: JSON schema for function calling.
        - `TOOL_FUNCTION`: The function object.
        - `TOOL_SYSTEM` (Optional): System message for the tool.
        - `TOOL_DESCRIPTION` (Optional): Tool description.
- **Remarks:** `schema` and `func` parameters are ignored when `tool` is given.

#### `schema`
**Type:** `Optional[dict]`
**Default:** `None`

JSON schema for structured output or function calling.

#### `func`
**Type:** `Optional[Callable[..., Optional[str]]]`
**Default:** `None`

Function to be called (used with `schema`).

#### `temperature`
**Type:** `Optional[float]`
**Default:** `None`

Temperature for sampling.

#### `max_tokens`
**Type:** `Optional[int]`
**Default:** `None`

Maximum number of tokens to generate.

#### `context_window`
**Type:** `Optional[int]`
**Default:** `None`

Context window size (**Ollama only**).

#### `batch_size`
**Type:** `Optional[int]`
**Default:** `None`

Batch size (**Ollama only**).

#### `prefill`
**Type:** `Optional[Union[List[Optional[str]], str]]`
**Default:** `None`

Prefill of assistant message.
- **Applicable to:** `deepseek`, `mistral`, `ollama`, `groq`.

#### `stop`
**Type:** `Optional[list]`
**Default:** `None`

Stop sequences.

#### `stream`
**Type:** `Optional[bool]`
**Default:** `False`

Stream partial message deltas as they are available.

#### `stream_events_only`
**Type:** `Optional[bool]`
**Default:** `False`

Return streaming events object only.

#### `api_key`
**Type:** `Optional[str]`
**Default:** `None`

API key or credentials JSON file path (for Vertex AI).
- Applicable to most cloud backends (`anthropic`, `openai`, `azure`, etc.).

#### `api_endpoint`
**Type:** `Optional[str]`
**Default:** `None`

API endpoint.
- Applicable to `azure`, `custom`, `llamacpp`, `ollama`.

#### `api_project_id`
**Type:** `Optional[str]`
**Default:** `None`

Project ID (**Vertex AI only**).

#### `api_service_location`
**Type:** `Optional[str]`
**Default:** `None`

Cloud service location (**Vertex AI only**).

#### `api_timeout`
**Type:** `Optional[Union[int, float]]`
**Default:** `None`

Timeout for API request.

#### `print_on_terminal`
**Type:** `Optional[bool]`
**Default:** `True`

Print output on terminal.

#### `word_wrap`
**Type:** `Optional[bool]`
**Default:** `True`

Word wrap output according to current terminal width.

### Return Value

Returns **either**:
1. `List[Dict[str, str]]`: List of messages containing multi-turn interaction. The latest assistant response is in the last item.
2. `Any`: Streaming events object if `stream=True` and `stream_events_only=True`.
