from agentmake import AGENTMAKE_USER_DIR, PACKAGE_PATH, DEFAULT_AI_BACKEND, DEFAULT_TEXT_EDITOR, DEFAULT_MARKDOWN_THEME, config, agentmake, edit_configurations, getOpenCommand, getToolInfo
from agentmake.etextedit import launch
from agentmake.utils.handle_text import readTextFile, writeTextFile
from agentmake.utils.files import searchFolder
from agentmake.utils.text_wrapper import wrapText
from agentmake.utils.system import getCliOutput
from pprint import pformat
from json import loads
from shutil import which
import argparse, os, sys, pyperclip, re


def chat():
    main(keep_chat_record=True)

def main(keep_chat_record=False):
    # Create the parser
    parser = argparse.ArgumentParser(description = """ToolMate AI API client `tm` cli options""")
    # Add arguments for running `agentmake` function
    parser.add_argument("default", nargs="*", default=None, help="user prompt")
    parser.add_argument("-b", "--backend", action="store", dest="backend", help="AI backend")
    parser.add_argument("-m", "--model", action="store", dest="model", help="AI model")
    parser.add_argument("-mka", "--model_keep_alive", action="store", dest="model_keep_alive", help="time to keep the model loaded in memory; applicable to ollama only")
    parser.add_argument("-sys", "--system", action='append', dest="system", help="system message(s)")
    parser.add_argument("-ins", "--instruction", action='append', dest="instruction", help="predefined instruction(s) that are added as the user prompt prefix")
    parser.add_argument("-fup", "--follow_up_prompt", action='append', dest="follow_up_prompt", help="follow-up prompt(s) after an assistant message is generated")
    parser.add_argument("-icp", "--input_content_plugin", action='append', dest="input_content_plugin", help="plugin(s) that work on user input")
    parser.add_argument("-ocp", "--output_content_plugin", action='append', dest="output_content_plugin", help="plugin(s) that work on assistant response")
    parser.add_argument("-a", "--agent", action='append', dest="agent", help="agentmake-compatible agent(s)")
    parser.add_argument("-t", "--tool", action='append', dest="tool", help="agentmake-compatible tool(s)")
    parser.add_argument("-sch", "--schema", action='store', dest="schema", help="json schema for structured output")
    parser.add_argument("-tem", "--temperature", action='store', dest="temperature", type=float, help="temperature for sampling")
    parser.add_argument("-mt", "--max_tokens", action='store', dest="max_tokens", type=int, help="maximum number of tokens to generate")
    parser.add_argument("-cw", "--context_window", action='store', dest="context_window", type=int, help="context window size; applicable to ollama only")
    parser.add_argument("-bs", "--batch_size", action='store', dest="batch_size", type=int, help="batch size; applicable to ollama only")
    parser.add_argument("-pre", "--prefill", action='append', dest="prefill", help="prefill of assistant message; applicable to deepseek, mistral, ollama and groq only")
    parser.add_argument("-sto", "--stop", action='append', dest="stop", help="stop sequences")
    parser.add_argument("-key", "--api_key", action="store", dest="api_key", help="API key")
    parser.add_argument("-end", "--api_endpoint", action="store", dest="api_endpoint", help="API endpoint")
    parser.add_argument("-pi", "--api_project_id", action="store", dest="api_project_id", help="project id; applicable to Vertex AI only")
    parser.add_argument("-sl", "--api_service_location", action="store", dest="api_service_location", help="cloud service location; applicable to Vertex AI only")
    parser.add_argument("-tim", "--api_timeout", action="store", dest="api_timeout", type=float, help="timeout for API request")
    parser.add_argument("-ww", "--word_wrap", action="store_true", dest="word_wrap", help="wrap output text according to current terminal width")
    # chat features
    parser.add_argument("-c", "--chat", action="store_true", dest="chat", help="enable chat feature")
    parser.add_argument("-cf", "--chat_file", action="store", dest="chat_file", help="load the conversation recorded in the given file")
    parser.add_argument("-n", "--new_conversation", action="store_true", dest="new_conversation", help="new conversation; applicable when chat feature is enabled")
    parser.add_argument("-s", "--save_conversation", action="store", dest="save_conversation", help="save conversation in a chat file; specify the file path for saving the file; applicable when chat feature is enabled")
    parser.add_argument("-e", "--export_conversation", action="store", dest="export_conversation", help="export conversation in plain text format; specify the file path for the export; applicable when chat feature is enabled")
    # clipboard
    parser.add_argument("-pa", "--paste", action="store_true", dest="paste", help="paste the clipboard text as a suffix to the user prompt")
    parser.add_argument("-py", "--copy", action="store_true", dest="copy", help="copy assistant response to the clipboard")
    # list
    parser.add_argument("-la", "--list_agents", action="store_true", dest="list_agents", help="list agents")
    parser.add_argument("-li", "--list_instructions", action="store_true", dest="list_instructions", help="list instructions")
    parser.add_argument("-lpl", "--list_plugins", action="store_true", dest="list_plugins", help="list plugins")
    parser.add_argument("-lpr", "--list_prompts", action="store_true", dest="list_prompts", help="list prompts")
    parser.add_argument("-ls", "--list_systems", action="store_true", dest="list_systems", help="list systems")
    parser.add_argument("-lt", "--list_tools", action="store_true", dest="list_tools", help="list tools")
    parser.add_argument("-lti", "--list_tools_info", action="store_true", dest="list_tools_info", help="list tools information")
    # find
    parser.add_argument("-fa", "--find_agents", action="store", dest="find_agents", help="find agents")
    parser.add_argument("-fi", "--find_instructions", action="store", dest="find_instructions", help="find instructions")
    parser.add_argument("-fpl", "--find_plugins", action="store", dest="find_plugins", help="find plugins")
    parser.add_argument("-fpr", "--find_prompts", action="store", dest="find_prompts", help="find prompts")
    parser.add_argument("-fs", "--find_systems", action="store", dest="find_systems", help="find systems")
    parser.add_argument("-ft", "--find_tools", action="store", dest="find_tools", help="find tools")
    # image creation
    parser.add_argument("-iw", "--image_width", action='store', dest="image_width", type=int, help="image width for image creation")
    parser.add_argument("-ih", "--image_height", action='store', dest="image_height", type=int, help="image height for image creation")
    parser.add_argument("-iss", "--image_sample_steps", action='store', dest="image_sample_steps", type=int, help="sample steps for image creation")
    # others
    parser.add_argument("-i", "--interactive", action="store_true", dest="interactive", help="interactive mode to select an instruction to work on selected or copied text")
    parser.add_argument("-u", "--upgrade", action="store_true", dest="upgrade", help="upgrade `agentmake` pip package")
    parser.add_argument("-gm", "--get_model", action="append", dest="get_model", help=f"download ollama models if they do not exist; export downloaded ollama models to `{os.path.join(AGENTMAKE_USER_DIR, 'models', 'gguf')}`")
    parser.add_argument("-ec", "--edit_configurations", action="store_true", dest="edit_configurations", help="edit default configurations with text editor")
    parser.add_argument("-ei", "--edit_input", action="store_true", dest="edit_input", help="edit user input with text editor")
    parser.add_argument("-mh", "--markdown_highlights", action="store_true", dest="markdown_highlights", help="highlight markdown syntax")
    # Parse arguments
    args = parser.parse_args()

    # upgrade
    if args.upgrade:
        if pip := which("pip"):
            try:
                from google.genai.types import Content
                genai_installed = True
            except:
                genai_installed = False
            cmd = f'''{pip} install --upgrade "agentmake[genai]"''' if genai_installed else f"{pip} install --upgrade agentmake"
            print(f"Upgrading ...\nRunning `{cmd}` ...")
            os.system(cmd)
            print("Done! Closing ...")
            exit(0)
        else:
            print("Upgrade aborted! `pip` command not found!")

    # edit configurations
    if args.edit_configurations:
        edit_configurations()

    # export ollama models
    if args.get_model:
        from agentmake.utils.export_gguf import exportOllamaModels
        from agentmake import OllamaAI
        for i in args.get_model:
            OllamaAI.downloadModel(i)
        exportOllamaModels(args.get_model)

    # interactive mode
    if args.interactive:
        instruction = selectInstruction()
        if instruction:
            args.default.insert(0, instruction)
            if instruction.startswith("Rewrite the following content in markdown format"):
                args.markdown_highlights = True

    # enable chat feature
    if args.chat:
        keep_chat_record = True

    # image creation
    if args.image_width:
        config.image_width = args.image_width
    if args.image_height:
        config.image_height = args.image_height
    if args.image_sample_steps:
        config.image_sample_steps = args.image_sample_steps

    # list
    if args.list_agents:
        listComponent("agents", ext="py")
    if args.list_instructions:
        listComponent("instructions")
    if args.list_plugins:
        listComponent("plugins", ext="py")
    if args.list_prompts:
        listComponent("prompts")
    if args.list_systems:
        listComponent("systems")
    if args.list_tools:
        listComponent("tools", ext="py")
    if args.list_tools_info:
        listComponent("tools", ext="py", info=True)

    # find
    if args.find_agents:
        user_agents = os.path.join(AGENTMAKE_USER_DIR, "agents")
        if os.path.isdir(user_agents):
            searchFolder(user_agents, args.find_agents, filter="*.py")
        searchFolder(os.path.join(PACKAGE_PATH, "agents"), args.find_agents, filter="*.py")
    if args.find_instructions:
        user_instructions = os.path.join(AGENTMAKE_USER_DIR, "instructions")
        if os.path.isdir(user_instructions):
            searchFolder(user_instructions, args.find_instructions, filter="*.md")
        searchFolder(os.path.join(PACKAGE_PATH, "instructions"), args.find_instructions, filter="*.md")
    if args.find_plugins:
        user_plugins = os.path.join(AGENTMAKE_USER_DIR, "plugins")
        if os.path.isdir(user_plugins):
            searchFolder(user_plugins, args.find_plugins, filter="*.py")
        searchFolder(os.path.join(PACKAGE_PATH, "plugins"), args.find_plugins, filter="*.py")
    if args.find_prompts:
        user_prompts = os.path.join(AGENTMAKE_USER_DIR, "prompts")
        if os.path.isdir(user_prompts):
            searchFolder(user_prompts, args.find_prompts, filter="*.md")
        searchFolder(os.path.join(PACKAGE_PATH, "prompts"), args.find_prompts, filter="*.md")
    if args.find_systems:
        user_systems = os.path.join(AGENTMAKE_USER_DIR, "systems")
        if os.path.isdir(user_systems):
            searchFolder(user_systems, args.find_systems, filter="*.md")
        searchFolder(os.path.join(PACKAGE_PATH, "systems"), args.find_systems, filter="*.md")
    if args.find_tools:
        user_tools = os.path.join(AGENTMAKE_USER_DIR, "tools")
        if os.path.isdir(user_tools):
            searchFolder(user_tools, args.find_tools, filter="*.py")
        searchFolder(os.path.join(PACKAGE_PATH, "tools"), args.find_tools, filter="*.py")

    user_prompt = " ".join(args.default) if args.default is not None else ""
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if stdin_text:
        stdin_text = f"\n\n{stdin_text.strip()}"
    if args.paste:
        clipboardText = getCliOutput("termux-clipboard-get") if which("termux-clipboard-get") else pyperclip.paste()
    else:
        clipboardText = ""
    if clipboardText:
        clipboardText = f"\n\n{clipboardText.strip()}"
    user_prompt = user_prompt + stdin_text + clipboardText
    # edit with text editor
    if args.edit_input and DEFAULT_TEXT_EDITOR:
        if DEFAULT_TEXT_EDITOR == "etextedit":
            user_prompt = launch(input_text=user_prompt, filename=None, exitWithoutSaving=True, customTitle="Edit instruction below; exit when you finish")
        else:
            tempTextFile = os.path.join(PACKAGE_PATH, "temp", "edit_instruction")
            writeTextFile(tempTextFile, user_prompt)
            os.system(f'''{DEFAULT_TEXT_EDITOR} "{tempTextFile}"''')
            user_prompt = readTextFile(tempTextFile)
    # new
    if args.new_conversation:
        config.messages = []
    # run
    if user_prompt:
        follow_up_prompt = args.follow_up_prompt if args.follow_up_prompt else []
        if keep_chat_record:
            if args.chat_file:
                if os.path.isfile(args.chat_file):
                    glob = {}
                    loc = {}
                    try:
                        content = "chat_file_messages = " + readTextFile(args.chat_file)
                        exec(content, glob, loc)
                        chat_file_messages = loc.get("chat_file_messages")
                        if not isinstance(chat_file_messages, dict):
                            raise ValueError("Error! Chat file format is invalid!")
                        config.messages = []
                        for i in chat_file_messages:
                            try:
                                config.messages({"role", i.get("role"), "content", i.get("content")})
                            except:
                                pass
                    except:
                        raise ValueError("Error! Chat file format is invalid!")
                else:
                    raise ValueError("Error! Given chat file path does not exist!")
        if keep_chat_record and config.messages:
            follow_up_prompt.insert(0, user_prompt)

        messages = config.messages if keep_chat_record and config.messages else user_prompt

        # run agentmake function
        config.messages = agentmake(
            messages=messages,
            backend=args.backend if args.backend else DEFAULT_AI_BACKEND,
            model=args.model,
            model_keep_alive=args.model_keep_alive,
            system=args.system,
            instruction=args.instruction,
            follow_up_prompt=follow_up_prompt,
            input_content_plugin=args.input_content_plugin,
            output_content_plugin=args.output_content_plugin,
            agent=args.agent,
            tool=args.tool,
            schema=loads(args.schema) if args.schema else None,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            context_window=args.context_window,
            batch_size=args.batch_size,
            prefill=args.prefill,
            stop=args.stop,
            api_key=args.api_key,
            api_endpoint=args.api_endpoint,
            api_project_id=args.api_project_id,
            api_service_location=args.api_service_location,
            api_timeout=int(args.api_timeout) if args.api_timeout and args.backend and args.backend in ("cohere", "mistral", "genai", "vertexai") else args.api_timeout,
            word_wrap=args.word_wrap,
            stream=False if args.markdown_highlights else True,
            print_on_terminal=False if args.markdown_highlights else True,
        )
        if args.copy or args.markdown_highlights:
            last_response = config.messages[-1].get("content", "")
            if args.markdown_highlights and last_response:
                highlightMarkdownSyntax(last_response)
    elif keep_chat_record and config.messages:
        # display the last assistant response when chat feature is enabled and there is no new user prompt
        last_response = config.messages[-1].get("content", "")
        if last_response:
            if args.markdown_highlights:
                highlightMarkdownSyntax(last_response)
            else:
                print(wrapText(last_response) if args.word_wrap else last_response)
    # copy response to the clipboard
    if args.copy and last_response:
        if which("termux-clipboard-set"):
            from pydoc import pipepager
            pipepager(last_response, cmd="termux-clipboard-set")
        else:
            pyperclip.copy(last_response)
        print("--------------------\nCopied!")
    # save conversation record
    if keep_chat_record:
        config_file = os.path.join(PACKAGE_PATH, "config.py")
        config_content = "messages = " + pformat(config.messages)
        writeTextFile(config_file, config_content)
        if args.save_conversation:
            try:
                writeTextFile(args.save_conversation, pformat(config.messages))
            except:
                raise ValueError(f"Error! Failed to save conversation to '{args.save_conversation}'!")
        if args.export_conversation:
            export_content = []
            for i in config.messages:
                role = i.get("role", "")
                content = i.get("content", "")
                if role in ("user", "assistant") and content.strip():
                    content = f"```{role}\n{content}\n```"
                    export_content.append(content)
            try:
                writeTextFile(args.export_conversation, "\n".join(export_content))
                os.system(f'''{getOpenCommand()} "{args.export_conversation}"''')
            except:
                raise ValueError(f"Error! Failed to export conversation to '{args.export_conversation}'!")

def listComponent(folder, ext="md", info=False):
    folder1 = os.path.join(AGENTMAKE_USER_DIR, folder)
    folder2 = os.path.join(PACKAGE_PATH, folder)
    for i in (folder1, folder2):
        if os.path.isdir(i):
            for ii in os.listdir(i):
                fullPath = os.path.join(i, ii)
                if os.path.isfile(fullPath) and not ii.lower() == "readme.md" and ii.endswith(f".{ext}"):
                    component = os.path.join(folder, ii)
                    if info:
                        try:
                            #print(getToolInfo(fullPath))
                            info = getToolInfo(fullPath)
                            highlightMarkdownSyntax(info)
                        except:
                            # skipped unsupported tools
                            pass
                    else:
                        print(re.sub(r"^.*?[/\\]", "", component)[:-(len(ext)+1)])
                elif os.path.isdir(fullPath) and not os.path.basename(fullPath) == "lib":
                    listComponent(os.path.join(folder, ii), ext=ext, info=info)

def selectInstruction():
    from prompt_toolkit.shortcuts import radiolist_dialog
    import subprocess, shutil
    input_text = subprocess.run("""echo "$(xsel -o)" | sed 's/"/\"/g'""", shell=True, capture_output=True, text=True).stdout if shutil.which("xsel") else ""
    if not input_text:
        input_text = subprocess.run("termux-clipboard-get", shell=True, capture_output=True, text=True).stdout if shutil.which("termux-clipboard-get") else pyperclip.paste()
    if input_text is None:
        input_text = ""

    values=[
        ("explain", "Explain"),
        ("improve", "Improve writing"),
        ("summarize", "Summarize"),
        ("elaborate", "Elaborate"),
        ("analyze", "Analyze"),
        ("professional", "Rewrite in professional tone"),
        ("markdown", "Rewrite in markdown format"),
        ("translate", "Translate to ..."),
    ]
    for i in range(1, 11):
        custom = os.getenv(f"CUSTOM_INSTRUCTION_{i}")
        if custom:
            values.append((f"custom{i}", custom[30:] + " ..." if len(custom) > 30 else custom))
        else:
            break

    result = radiolist_dialog(
        title="Instructions",
        text="Select an instruction",
        values=values,
    ).run()
    if result:
        DEFAULT_WRITING_STYLE = os.getenv('DEFAULT_WRITING_STYLE') if os.getenv('DEFAULT_WRITING_STYLE') else 'standard English'
        instructions = {
            "explain": "Explain the following content:",
            "improve": f"Improve the following writing, according to {DEFAULT_WRITING_STYLE}:",
            "summarize": "Summarize the following content:",
            "elaborate": "Elaborate the following content:",
            "analyze": "Analyze the following content:",
            "professional": "Rewrite the following content in professional tone:",
            "markdown": "Rewrite the following content in markdown format:",
            "translate": "Translate the following content to ",
        }
        for i in range(1, 11):
            custom = os.getenv(f"CUSTOM_INSTRUCTION_{i}")
            if custom:
                instructions[f"custom{i}"] = custom
            else:
                break
        instruction = instructions.get(result)
        if instruction.startswith("Translate the following content to "):
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory
            history_dir = os.path.join(AGENTMAKE_USER_DIR, "history")
            if not os.path.isdir(history_dir):
                from pathlib import Path
                Path(history_dir).mkdir(parents=True, exist_ok=True)
            session = PromptSession(history=FileHistory(os.path.join(history_dir, "translate_history")))
            language = session.prompt("Translate to: ", bottom_toolbar="Press <Enter> to submit")
            if not language:
                language = "English"
            instruction = instruction + language + ". Provide me with the traslation ONLY, without extra comments and explanations."
        instruction += input_text
    return instruction.rstrip() + "\n\n" if instruction else ""

def highlightMarkdownSyntax(content, theme=""):

    from pygments import highlight
    from pygments.lexers.markup import MarkdownLexer
    from pygments.formatters import Terminal256Formatter
    from pygments.styles import get_style_by_name

    """
    Highlight Markdown content using Pygments and print it to the terminal.
    ```
    from pygments.styles import get_all_styles
    styles = list(get_all_styles())
    print(styles)
    ['abap', 'algol', 'algol_nu', 'arduino', 'autumn', 'bw', 'borland', 'coffee', 'colorful', 'default', 'dracula', 'emacs', 'friendly_grayscale', 'friendly', 'fruity', 'github-dark', 'gruvbox-dark', 'gruvbox-light', 'igor', 'inkpot', 'lightbulb', 'lilypond', 'lovelace', 'manni', 'material', 'monokai', 'murphy', 'native', 'nord-darker', 'nord', 'one-dark', 'paraiso-dark', 'paraiso-light', 'pastie', 'perldoc', 'rainbow_dash', 'rrt', 'sas', 'solarized-dark', 'solarized-light', 'staroffice', 'stata-dark', 'stata-light', 'tango', 'trac', 'vim', 'vs', 'xcode', 'zenburn']    
    ```
    """
    try:
        # Get the Pygments style by name.
        style = get_style_by_name(theme if theme else DEFAULT_MARKDOWN_THEME)
        # Create a terminal formatter that uses the specified style.
        formatter = Terminal256Formatter(style=style)
        # Highlight the content.
        highlighted_content = highlight(content, MarkdownLexer(), formatter)
        print(highlighted_content)
    except Exception as e:
        # Fallback: simply print the content if something goes wrong.
        print(content)

if __name__ == "__main__":
    test = main()
