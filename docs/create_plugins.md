# How to Create a Plugin?

You may create custom plugins, to work with the `plugin` parameter of the `agentmake` function.

A `agentmake` plugin can process either user input or assistant output or both.

It is a simple to create a plugin to meet your own needs. Each plugin is written as a python file, in which one parameter is specified:

1. `CONTENT_PLUGIN`
    It is the funciton object being called to work on either user input or assistant output or both.
    This functions takes user input or assistant output as its first parameter and returns the processed result.

For practical examples, check our built-in tools at https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins