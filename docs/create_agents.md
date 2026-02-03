# How to Create an Agent?

You may create custom agents to work with the `agent` parameter of the `agentmake` function.

An `agentmake` agent automates multi-turn work and decisions.

It is simple to create an agent to meet your needs. Each agent is defined in a Python file (`.py`) containing the following variable:

### `AGENT_FUNCTION`

This is the function object called to run the agent.

**Example Structure:**

```python
def my_agent_function(messages, **kwargs):
    # Your agent logic here
    pass

AGENT_FUNCTION = my_agent_function
```

For practical examples, check our built-in agents at [https://github.com/eliranwong/agentmake/tree/main/agentmake/agents](https://github.com/eliranwong/agentmake/tree/main/agentmake/agents).