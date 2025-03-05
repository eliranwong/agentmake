# How to Create a Tool?

You may create custom tools, to work with the `tool` parameter of the `agentmake` function.

A `agentmake` tool takes actions to resolve user requests with function calling.

It is a simple to create a tool to meet your own needs. Each tool is written as a python file, in which two or three parameters are specified:

1. `TOOL_SCHEMA` - It is the json schema that describes the parameters for function calling. This is a required parameter.

Remarks: It is allowed to provide an empty dictionary as a TOOL_SCHEMA. In this case, the `agentmake` function passes the parameter `messages` to the TOOL_FUNCTION.

2. `TOOL_FUNCTION` - It is the funciton object being called with the tool. This is a required parameter.

```
Args:
    i. The structured output, generated as a dictionary according to the TOOL_SCHEMA, is unpacked as arguments for the function.
    ii. Each TOOL_FUNCTION must include `**kwargs` as part of its arguments, as the `agentmake` function passes the following parameters to the TOOL_FUNCTION, offering possibility to run nested `agentmake` functions within the TOOL_FUNCTION:
        backend, model, model_keep_alive, temperature, max_tokens, context_window, batch_size, prefill, stop, stream, api_key, api_project_id, api_service_location, api_timeout, print_on_terminal, word_wrap
Return
    i. Empty string - User request is resolved without the need of chat extension. Any printed content or terminal output resulting from the execution of the function is taken as the assistant's response.
    ii. Non-empty string - Provide context to extend chat conversation.
    iii. None - Fall back to regular chat completion. It is useful for handling errors encounted when the function is executed.
```

3. `TOOL_SYSTEM` - This is optional. You may either:

i. specifie the system message for running the tool.

ii. assign an empty string to it if you do not want to use a tool system message.

iii. omit this parameter to use `agentmake` default tool system message.

For practical examples, check our built-in tools at https://github.com/eliranwong/agentmake/tree/main/agentmake/tools