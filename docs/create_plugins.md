# How to Create a Plugin?

You can create custom plugins to work with the `input_content_plugin` or `output_content_plugin` parameters of the `agentmake` function.

An `agentmake` plugin can process user input, assistant output, or both.

Each plugin is defined in a Python file (`.py`) specifying the following variable:

### 1. `CONTENT_PLUGIN`

The function object called to process content.
- Takes the content (str) as its first parameter.
- Returns the processed content (str).
- Can accept `**kwargs` for accessing `agentmake` runtime parameters.

**Example Structure:**

```python
def my_plugin(content, **kwargs):
    return content.upper()

CONTENT_PLUGIN = my_plugin
```

For practical examples, check our built-in plugins at [https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins](https://github.com/eliranwong/agentmake/tree/main/agentmake/plugins).