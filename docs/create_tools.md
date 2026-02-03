# How to Create a Tool?

You can create custom tools to work with the `tool` parameter of the `agentmake` function.

An `agentmake` tool takes actions to resolve user requests through function calling.

Each tool is defined in a Python file (`.py`) specifying the following variables:

### 1. `TOOL_SCHEMA` (Required)

The JSON schema describing the parameters for function calling.
- If you want to pass the whole conversation for the tool to process, assign an empty dictionary (`{}`) to `TOOL_SCHEMA`. In this case, `agentmake` passes the `messages` parameter to `TOOL_FUNCTION`.

### 2. `TOOL_FUNCTION` (Required)

The function object called by the tool.

**Arguments:**
1.  **Structured Output:** Unpacked arguments from the dictionary generated according to `TOOL_SCHEMA`.
2.  **`**kwargs`:** REQUIRED. The `agentmake` function passes runtime parameters (e.g., `backend`, `model`, `api_key`) providing the ability to run nested `agentmake` calls within your tool.

**Return Values:**
- **Empty string (`""`)**: User request resolved without needed chat extension. Any printed output is taken as the assistant's response.
- **Non-empty string**: Provides context to extend the chat conversation.
- **`None`**: Fall back to regular chat completion (useful for error handling).

### 3. `TOOL_SYSTEM` (Optional)

System message for running the tool.
- Specify a string for the system message.
- Assign an empty string `""` to avoid using a tool system message.
- Omit to use the default `agentmake` tool system message.

### 4. `TOOL_DESCRIPTION` (Optional)

Description of the tool.
- Optional if the tool description is already specified within `TOOL_SCHEMA`.

---

**Example Structure:**

```python
def my_tool_function(param1, **kwargs):
    # Tool logic
    return "Result"

TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "param1": {"type": "string"}
    }
}

TOOL_FUNCTION = my_tool_function
```

For practical examples, check our built-in tools at [https://github.com/eliranwong/agentmake/tree/main/agentmake/tools](https://github.com/eliranwong/agentmake/tree/main/agentmake/tools).