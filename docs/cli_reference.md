# CLI Reference

AgentMake provides a rich Command Line Interface (CLI) for interacting with AI models, managing resources, and processing text.

## Usage

```bash
agentmake [prompt] [options]
```

## Options

### Basic Options

- **`prompt`** (positional): The user prompt or request.
- **`-b`, `--backend`**: AI backend to use (e.g., `ollama`, `openai`, `anthropic`).
- **`-m`, `--model`**: AI model name (e.g., `gpt-4`, `llama3`).
- **`-mka`, `--model_keep_alive`**: Time to keep the model loaded in memory (Applicable to `ollama` only).
- **`-sys`, `--system`**: System message(s). Can be specified multiple times.
- **`-ins`, `--instruction`**: Predefined instruction(s) added as prefix to user prompt. Can be specified multiple times.
- **`-fup`, `--follow_up_prompt`**: Follow-up prompt(s) after assistant message.
- **`-icp`, `--input_content_plugin`**: Plugin(s) that work on user input.
- **`-ocp`, `--output_content_plugin`**: Plugin(s) that work on assistant response.
- **`-a`, `--agent`**: AgentMake-compatible agent(s).
- **`-t`, `--tool`**: AgentMake-compatible tool(s).
- **`-sch`, `--schema`**: JSON schema for structured output.
- **`-tem`, `--temperature`**: Temperature for sampling (float).
- **`-mt`, `--max_tokens`**: Maximum number of tokens to generate (int).
- **`-cw`, `--context_window`**: Context window size (Applicable to `ollama` only, int).
- **`-bs`, `--batch_size`**: Batch size (Applicable to `ollama` only, int).
- **`-pre`, `--prefill`**: Prefill of assistant message (Applicable to `deepseek`, `mistral`, `ollama`, `groq`).
- **`-sto`, `--stop`**: Stop sequences.
- **`-key`, `--api_key`**: API key.
- **`-end`, `--api_endpoint`**: API endpoint.
- **`-pi`, `--api_project_id`**: Project ID (Applicable to Vertex AI).
- **`-sl`, `--api_service_location`**: Cloud service location (Applicable to Vertex AI).
- **`-tim`, `--api_timeout`**: Timeout for API request (float).
- **`-ww`, `--word_wrap`**: Wrap output text according to current terminal width.

### Configuration Overrides

- **`-dsys`, `--default_system_message`**: Override default system message without changing configuration.
- **`-dfup`, `--default_follow_up_prompt`**: Override default follow-up prompt without changing configuration.
- **`-dtc`, `--default_tool_choices`**: Override default tool choices for agents (e.g., `'@chat @magic'`).
- **`-doc`, `--default_open_command`**: Override default open command (e.g., `'open'`).

### Prompts

- **`-i`, `--interactive`**: Interactive mode to select an instruction to work on selected or copied text.
- **`-p`, `--prompts`**: Enable multi-turn prompts for the user interface.

### Chat Features

- **`-c`, `--chat`**: Enable chat feature (keeps record).
- **`-o`, `--open_conversation`**: Open a saved conversation file.
- **`-n`, `--new_conversation`**: Start a new conversation (applicable when chat provided).
- **`-s`, `--save_conversation`**: Save conversation in a chat file (specify file path).
- **`-e`, `--export_conversation`**: Export conversation in plain text format (specify file path).
- **`-show`, `--show_conversation`**: Show current conversation.
- **`-edit`, `--edit_conversation`**: Edit conversation messages.
- **`-trim`, `--trim_conversation`**: Trim conversation history.

### Text Selection & Clipboard

- **`-x`, `--xsel`**: Use `xsel` command to obtain text selection as input.
- **`-pa`, `--paste`**: Paste clipboard text as user prompt suffix.
- **`-py`, `--copy`**: Copy assistant response to clipboard.

### Export Assistant Response

- **`-docx`, `--document`**: Save assistant response to a specified `.docx` file.
- **`-html`, `--webpage`**: Save assistant response to a specified `.html` file.
- **`-md`, `--markdown`**: Save assistant response to a specified `.md` file.
- **`-txt`, `--text`**: Save assistant response to a specified `.txt` file.

### List Resources

- **`-la`, `--list_agents`**: List available agents.
- **`-li`, `--list_instructions`**: List available instructions.
- **`-lpl`, `--list_plugins`**: List available plugins.
- **`-lpr`, `--list_prompts`**: List available prompts.
- **`-ls`, `--list_systems`**: List available systems.
- **`-lfs`, `--list_fabric_systems`**: List available fabric systems.
- **`-lt`, `--list_tools`**: List available tools.
- **`-lti`, `--list_tools_info`**: List tools with detailed information.
- **`-lm`, `--list_models`**: List downloaded GGUF models.

### Read Resources

- **`-ra`, `--read_agent`**: Read content of an agent.
- **`-ri`, `--read_instruction`**: Read content of an instruction.
- **`-rpl`, `--read_plugin`**: Read content of a plugin.
- **`-rpr`, `--read_prompt`**: Read content of a prompt.
- **`-rs`, `--read_system`**: Read content of a system.
- **`-rt`, `--read_tool`**: Read content of a tool.

### Find Resources

- **`-fa`, `--find_agents`**: Find agents by name pattern.
- **`-fi`, `--find_instructions`**: Find instructions by name pattern.
- **`-fpl`, `--find_plugins`**: Find plugins by name pattern.
- **`-fpr`, `--find_prompts`**: Find prompts by name pattern.
- **`-fs`, `--find_systems`**: Find systems by name pattern.
- **`-ft`, `--find_tools`**: Find tools by name pattern.

### Image Creation

- **`-iw`, `--image_width`**: Image width (int).
- **`-ih`, `--image_height`**: Image height (int).
- **`-iss`, `--image_sample_steps`**: Sample steps for image creation (int).

### Other Options

- **`-v`, `--version`**: Show version information.
- **`-u`, `--upgrade`**: Upgrade `agentmake` pip package.
- **`-gm`, `--get_model`**: Download Ollama models if they don't exist; export to user directory.
- **`-ed`, `--editor`**: Specify text editor for editing features.
- **`-ec`, `--edit_configurations`**: Edit default configurations.
- **`-ei`, `--edit_input`**: Edit user input with text editor.
- **`-eo`, `--edit_output`**: Edit assistant response with text editor.
- **`-mh`, `--markdown_highlights`**: Highlight markdown syntax in output.
