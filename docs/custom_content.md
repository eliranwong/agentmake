# Custom Content

You can keep your custom content, such as predefined system messages, prompts, predefined messages, and tools, in a directory that you prefer.

Set the value of the environment variable `TOOLMATE_PATH` to the path you prefer.  Otherwise, the path `~/toolmate` is used as the default.

Inside the directory, specified in `TOOLMATE_PATH`, create four folders for storing your own content, just like built-in contexts, prompts, systems and tools are placed in the package directory:

`contexts` - [predefined contexts](https://github.com/eliranwong/agentmake/tree/main/agentmake/contexts)

`plugins` - [custom plugins](https://github.com/eliranwong/agentmake/blob/main/docs/create_plugins.md)

`prompts` - [predefined prompts](https://github.com/eliranwong/agentmake/tree/main/agentmake/prompts)

`systems` - [predefined system messages](https://github.com/eliranwong/agentmake/tree/main/agentmake/systems)

`tools` - [custom tools](https://github.com/eliranwong/agentmake/blob/main/docs/create_tools.md)

`agents`