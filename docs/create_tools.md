# How to Create a Tool?

You may create custom tools, to work with the `tool` parameter of the `generate` function.

A `agentmake` tool takes actions to resolve user requests with function calling.

It is a simple to create a tool to meet your own needs. Each tool is written as a python file, in which three parameters are specified:

1. `TOOL_SYSTEM` - It specifies the system message for running the tool.

2. `TOOL_SCHEMA` - It is the json schema that describes the parameters for function calling

3. `TOOL_FUNCTION` - It is the funciton object being called with the tool.

For practical examples, check our built-in tools at https://github.com/eliranwong/agentmake/tree/main/agentmake/tools