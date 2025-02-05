# How to Create a Tool?

You may create custom tools, to work with the `tool` parameter of the `agentmake` function.

A `agentmake` tool takes actions to resolve user requests with function calling.

It is a simple to create a tool to meet your own needs. Each tool is written as a python file, in which two or three parameters are specified:

1. `TOOL_SCHEMA` - It is the json schema that describes the parameters for function calling. This is a required parameter.

2. `TOOL_FUNCTION` - It is the funciton object being called with the tool. This is a required parameter.

3. `TOOL_SYSTEM` - This is optional. You may either:

i. specifie the system message for running the tool.

ii. assign an empty string to it if you do not want to use a tool system message.

iii. omit this parameter to use `agentmake` default tool system message.

For practical examples, check our built-in tools at https://github.com/eliranwong/agentmake/tree/main/agentmake/tools