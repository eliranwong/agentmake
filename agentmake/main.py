from agentmake import AGENTMAKE_ASSISTANT_NAME, AGENTMAKE_USERNAME, AGENTMAKE_USER_DIR, PACKAGE_PATH, DEFAULT_AI_BACKEND, DEFAULT_TEXT_EDITOR, DEFAULT_MARKDOWN_THEME, config, agentmake, edit_configurations, getOpenCommand, listResources, getMultipleTools, override_DEFAULT_SYSTEM_MESSAGE, override_DEFAULT_FOLLOW_UP_PROMPT, exportPlainConversation
from agentmake.etextedit import launch
from agentmake.utils.handle_text import readTextFile, writeTextFile
from agentmake.utils.files import searchFolder
from agentmake.utils.text_wrapper import wrapText
from agentmake.utils.system import getCliOutput
from pprint import pformat
import argparse, os, sys, pyperclip, re, json, shutil


def chat():
    main(keep_chat_record=True)

def main(keep_chat_record=False):
    # Create the parser
    parser = argparse.ArgumentParser(description = """AgentMake AI cli options""")
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
    # override default system message and follow-up prompt
    parser.add_argument("-dsys", "--default_system_message", action="store", dest="default_system_message", help="override default system message without changing the configuration")
    parser.add_argument("-dfup", "--default_follow_up_prompt", action="store", dest="default_follow_up_prompt", help="override default follow-up prompt without changing the configuration")
    parser.add_argument("-dtc", "--default_tool_choices", action="store", dest="default_tool_choices", help="override the default tool choices for agents to select, e.g. '@chat @magic'")
    # prompts
    parser.add_argument("-i", "--interactive", action="store_true", dest="interactive", help="interactive mode to select an instruction to work on selected or copied text")
    parser.add_argument("-p", "--prompts", action="store_true", dest="prompts", help="enable mult-turn prompts for the user interface")
    # chat features
    parser.add_argument("-c", "--chat", action="store_true", dest="chat", help="enable chat feature")
    parser.add_argument("-o", "--open_conversation", action="store", dest="open_conversation", help="open a saved conversation file")
    parser.add_argument("-n", "--new_conversation", action="store_true", dest="new_conversation", help="new conversation; applicable when chat feature is enabled")
    parser.add_argument("-s", "--save_conversation", action="store", dest="save_conversation", help="save conversation in a chat file; specify the file path for saving the file; applicable when chat feature is enabled")
    parser.add_argument("-e", "--export_conversation", action="store", dest="export_conversation", help="export conversation in plain text format; specify the file path for the export; applicable when chat feature is enabled")
    # clipboard
    parser.add_argument("-pa", "--paste", action="store_true", dest="paste", help="paste the clipboard text as a suffix to the user prompt")
    parser.add_argument("-py", "--copy", action="store_true", dest="copy", help="copy assistant response to the clipboard")
    # export assistant response to a file
    parser.add_argument("-docx", "--document", action="store", dest="document", help="save assistant response to a specified docx file")
    parser.add_argument("-html", "--webpage", action="store", dest="webpage", help="save assistant response to a specified html file")
    parser.add_argument("-md", "--markdown", action="store", dest="markdown", help="save assistant response to a specified markdown file")
    parser.add_argument("-txt", "--text", action="store", dest="text", help="save assistant response to a specified text file")
    # list
    parser.add_argument("-la", "--list_agents", action="store_true", dest="list_agents", help="list agents")
    parser.add_argument("-li", "--list_instructions", action="store_true", dest="list_instructions", help="list instructions")
    parser.add_argument("-lpl", "--list_plugins", action="store_true", dest="list_plugins", help="list plugins")
    parser.add_argument("-lpr", "--list_prompts", action="store_true", dest="list_prompts", help="list prompts")
    parser.add_argument("-ls", "--list_systems", action="store_true", dest="list_systems", help="list systems")
    parser.add_argument("-lt", "--list_tools", action="store_true", dest="list_tools", help="list tools")
    parser.add_argument("-lti", "--list_tools_info", action="store_true", dest="list_tools_info", help="list tools information")
    parser.add_argument("-lm", "--list_models", action="store_true", dest="list_models", help="list downloaded gguf models")
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
    parser.add_argument("-u", "--upgrade", action="store_true", dest="upgrade", help="upgrade `agentmake` pip package")
    parser.add_argument("-gm", "--get_model", action="append", dest="get_model", help=f"download ollama models if they do not exist; export downloaded ollama models to `{os.path.join(AGENTMAKE_USER_DIR, 'models', 'gguf')}`")
    parser.add_argument("-ed", "--editor", action="store", dest="editor", help="specify the text editor used for editing features; use default text editor if not specified")
    parser.add_argument("-ec", "--edit_configurations", action="store_true", dest="edit_configurations", help="edit default configurations with text editor")
    parser.add_argument("-ei", "--edit_input", action="store_true", dest="edit_input", help="edit user input with text editor")
    parser.add_argument("-eo", "--edit_output", action="store_true", dest="edit_output", help="edit assistant response with text editor")
    parser.add_argument("-mh", "--markdown_highlights", action="store_true", dest="markdown_highlights", help="highlight markdown syntax")
    # Parse arguments
    args = parser.parse_args()

    # upgrade
    if args.upgrade:
        if pip := shutil.which("pip"):
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

    # set text editor
    text_editor = args.editor if args.editor else DEFAULT_TEXT_EDITOR

    # edit configurations
    if args.edit_configurations:
        edit_configurations()

    # override default system message and follow-up prompt
    if args.default_system_message:
        override_DEFAULT_SYSTEM_MESSAGE(args.default_system_message)
    if args.default_follow_up_prompt:
        override_DEFAULT_FOLLOW_UP_PROMPT(args.default_follow_up_prompt)
    if args.default_tool_choices:
        os.environ["DEFAULT_TOOL_CHOICES"] = args.default_tool_choices

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
        listResources("agents", ext="py", display_func=print)
    if args.list_instructions:
        listResources("instructions", display_func=print)
    if args.list_plugins:
        listResources("plugins", ext="py", display_func=print)
    if args.list_prompts:
        listResources("prompts", display_func=print)
    if args.list_systems:
        listResources("systems", display_func=print)
    if args.list_tools:
        listResources("tools", ext="py", display_func=print)
    if args.list_tools_info:
        listResources("tools", ext="py", info=True, display_func=highlightMarkdownSyntax)
    if args.list_models:
        listResources("models", ext="gguf", display_func=print)

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
        clipboardText = getCliOutput("termux-clipboard-get") if shutil.which("termux-clipboard-get") else pyperclip.paste()
    else:
        clipboardText = ""
    if clipboardText:
        clipboardText = f"\n\n{clipboardText.strip()}"
    user_prompt = user_prompt + stdin_text + clipboardText
    # edit with text editor
    if args.edit_input and text_editor:
        if text_editor == "etextedit":
            user_prompt = launch(input_text=user_prompt, filename=None, exitWithoutSaving=True, customTitle="Edit instruction below; exit when you finish", startAtEnd=True)
        else:
            tempTextFile = os.path.join(PACKAGE_PATH, "temp", "edit_instruction")
            writeTextFile(tempTextFile, user_prompt)
            os.system(f'''{text_editor} "{tempTextFile}"''')
            user_prompt = readTextFile(tempTextFile)
    # new
    if args.new_conversation:
        if config.messages:
            # save current conversation record
            from agentmake import getCurrentDateTime
            from pathlib import Path
            timestamp = getCurrentDateTime()
            folderPath = os.path.join(AGENTMAKE_USER_DIR, "chats", re.sub("^([0-9]+?-[0-9]+?)-.*?$", r"\1", timestamp))
            Path(folderPath).mkdir(parents=True, exist_ok=True)
            chatFile = os.path.join(folderPath, f"{timestamp}.chat")
            writeTextFile(chatFile, pformat(config.messages))
        config.messages = []
    # run
    last_response = ""
    if not user_prompt and args.prompts:
        user_prompt = getInput(prompt=f"{AGENTMAKE_USERNAME.capitalize()}: ")
    if user_prompt:
        tools = args.tool if args.tool else []
        follow_up_prompt = args.follow_up_prompt if args.follow_up_prompt else []
        instruction_prefix = args.instruction if args.instruction else []

        instruction_pattern = "|".join(listResources("instructions", ext="md"))
        instruction_pattern = rf"""\+({instruction_pattern}) """

        def checkComponents(user_prompt, tools, follow_up_prompt, instruction_prefix):
            # multiple tools in a single instruction
            if not args.agent and (user_prompt.startswith("@") or re.search("[\n ]@", user_prompt)):
                tool_pattern = "|".join(listResources("tools", ext="py"))
                tool_pattern = f"""@({tool_pattern})[\n ]"""
                tools_names = re.findall(tool_pattern, f"{user_prompt} ")
                if tools_names:
                    separator = "＊@＊@＊"
                    tools_prompts = re.sub(tool_pattern, separator, f"{user_prompt} ").split(separator)
                    if tools_prompts:
                        if tools_prompts[0].strip():
                            # in case content entered before the first action declared
                            tools_names.insert(0, "chat")
                        else:
                            del tools_prompts[0]
                        user_prompt = tools_prompts[0]
                        if found_instruction := re.search(instruction_pattern, user_prompt):
                            found_instruction = found_instruction.group(1)
                            instruction_prefix.insert(0, found_instruction)
                            user_prompt = re.sub(rf"\+({found_instruction}) ", "", user_prompt)
                        for i in tools_prompts[1:]:
                            if found_instruction := re.search(instruction_pattern, i):
                                found_instruction = found_instruction.group(1)
                                instruction_prefix.append(found_instruction)
                                i = re.sub(rf"\+({found_instruction}) ", "", i)
                            follow_up_prompt.append(i)
                        for i in tools_names:
                            tools.append(i)
            else:
                instruction_names = re.findall(instruction_pattern, f"{user_prompt} ")
                for i in instruction_names:
                    instruction_prefix.append(i)
                user_prompt = re.sub(instruction_pattern, "", user_prompt)
            return user_prompt

        if keep_chat_record:
            if args.open_conversation:
                if os.path.isfile(args.open_conversation):
                    glob = {}
                    loc = {}
                    try:
                        content = "chat_file_messages = " + readTextFile(args.open_conversation)
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
                    except Exception as e:
                        raise ValueError("An error occurred: {e}" if e else "Error! Chat file format is invalid!")
                else:
                    raise ValueError("Error! Given chat file path does not exist!")
        if keep_chat_record and config.messages:
            follow_up_prompt.insert(0, user_prompt)

        messages = config.messages if keep_chat_record and config.messages else user_prompt

        # run agentmake function
        is_first_go = True
        while user_prompt:
            user_prompt = checkComponents(user_prompt, tools, follow_up_prompt, instruction_prefix)
            if args.prompts:
                print(f"{AGENTMAKE_ASSISTANT_NAME}: ", end='', flush=True)
            config.messages = agentmake(
                messages=messages if is_first_go else config.messages,
                backend=args.backend if args.backend else DEFAULT_AI_BACKEND,
                model=args.model,
                model_keep_alive=args.model_keep_alive,
                system=args.system,
                instruction=instruction_prefix,
                follow_up_prompt=follow_up_prompt if is_first_go else [user_prompt],
                input_content_plugin=args.input_content_plugin,
                output_content_plugin=args.output_content_plugin,
                agent=args.agent,
                tool=tools,
                schema=json.loads(args.schema) if args.schema else None,
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
            if not args.prompts:
                break
            # reset tools and follow_up_prompt
            is_first_go = False
            tools = []
            follow_up_prompt = []
            # get user prompt
            user_prompt = getInput(prompt=f"{AGENTMAKE_USERNAME.capitalize()}: ")

        last_response = config.messages[-1].get("content", "")
        if args.copy or args.markdown_highlights:
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
    if last_response:
        # edit assistant response with text editor
        if args.edit_output and text_editor:
            original_response = last_response
            if text_editor == "etextedit":
                last_response = launch(input_text=last_response, filename=None, exitWithoutSaving=True, customTitle="Edit assistant response; exit when you finish")
            else:
                tempTextFile = os.path.join(PACKAGE_PATH, "temp", "edit_response")
                writeTextFile(tempTextFile, last_response)
                os.system(f'''{text_editor} "{tempTextFile}"''')
                last_response = readTextFile(tempTextFile)
            if keep_chat_record and last_response and not last_response == original_response:
                config.messages[-1]["content"] = last_response
        # copy response to the clipboard
        if args.copy:
            if shutil.which("termux-clipboard-set"):
                from pydoc import pipepager
                pipepager(last_response, cmd="termux-clipboard-set")
            else:
                pyperclip.copy(last_response)
            print("--------------------\nCopied!")
        # export assistant response to a file
        if args.document:
            from agentmake.utils.handle_text import markdownToDocx
            output_file = args.document if args.document.endswith(".docx") else args.document + ".docx"
            markdownToDocx(last_response, output_file)
            os.system(f'''{getOpenCommand()} "{output_file}"''')
        if args.webpage:
            from agentmake.utils.handle_text import markdownToHtml
            output_file = args.webpage if args.webpage.endswith(".html") else args.webpage + ".html"
            markdownToHtml(last_response, output_file)
            os.system(f'''{getOpenCommand()} "{output_file}"''')
        if args.markdown:
            output_file = args.markdown if args.markdown.endswith(".md") else args.markdown + ".md"
            writeTextFile(output_file, last_response)
            os.system(f'''{getOpenCommand()} "{output_file}"''')
        if args.text:
            output_file = args.text if args.text.endswith(".txt") else args.text + ".txt"
            writeTextFile(output_file, last_response)
            os.system(f'''{getOpenCommand()} "{output_file}"''')
            
    # save conversation record
    if keep_chat_record:
        config_file = os.path.join(PACKAGE_PATH, "config.py")
        config_content = "messages = " + pformat(config.messages)
        writeTextFile(config_file, config_content)
        if args.save_conversation:
            try:
                writeTextFile(args.save_conversation, pformat(config.messages))
            except Exception as e:
                raise ValueError("An error occurred: {e}" if e else f"Error! Failed to save conversation to '{args.save_conversation}'!")
        if args.export_conversation:
            exportPlainConversation(config.messages, args.export_conversation)

def getInput(prompt="Instruction: "):
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
    from prompt_toolkit.key_binding import KeyBindings
    bindings = KeyBindings()
    @bindings.add("c-q")
    def _(event):
        " Exit when `c-x` is pressed. "
        event.app.exit()
    @bindings.add("c-i")
    def _(event):
        event.app.current_buffer.newline()

    history_dir = os.path.join(AGENTMAKE_USER_DIR, "history")
    if not os.path.isdir(history_dir):
        from pathlib import Path
        Path(history_dir).mkdir(parents=True, exist_ok=True)
    session = PromptSession(history=FileHistory(os.path.join(history_dir, "instruction_history")))
    completer = FuzzyCompleter(WordCompleter([f"+{i}" for i in listResources("instructions", ext="md")]+[f"@{i}" for i in listResources("tools", ext="py")], ignore_case=True))
    instruction = session.prompt(
        prompt,
        bottom_toolbar="Press <Enter> to submit <Tab> to start a new line <Ctrl+Q> to exit",
        completer=completer,
        key_bindings=bindings,
    )
    print()
    return instruction.strip() if instruction else ""

def selectInstruction():
    import subprocess
    from prompt_toolkit.shortcuts import radiolist_dialog
    
    input_text = subprocess.run("""echo "$(xsel -o)" | sed 's/"/\"/g'""", shell=True, capture_output=True, text=True).stdout if shutil.which("xsel") else ""

    # support custom menu
    custom_instructions = os.path.join(AGENTMAKE_USER_DIR, "menu.py")
    if os.path.isfile(custom_instructions):
        instructions = eval(readTextFile(custom_instructions))
    else:
        DEFAULT_REFINE_INSTRUCTION = os.getenv("DEFAULT_REFINE_INSTRUCTION") if os.getenv("DEFAULT_REFINE_INSTRUCTION") else f"@{os.path.join('styles', 'english')} "
        instructions = {
            "explain": ("Explain", "Explain the following content or words:"),
            "refine": ("Refine", DEFAULT_REFINE_INSTRUCTION),
            "summarize": ("Summarize", "Summarize the following content:"),
            "elaborate": ("Elaborate", "Elaborate the following content:"),
            "analyze": ("Analyze", "Analyze the following content:"),
            "professional": ("Rewrite in professional tone", "Rewrite the following content in professional tone:"),
            "markdown": ("Rewrite in markdown format", "Rewrite the following content in markdown format:"),
            "translate": ("Translate to ...", "Translate the following content to "),
        }
    for i in range(1, 11):
        if custom := os.getenv(f"CUSTOM_INSTRUCTION_{i}"):
            instructions[f"custom{i}"] = (custom[:30]+" ..." if len(custom) > 30 else custom, custom)
        else:
            break
    DEFAULT_CUSTOM_LABEL = os.getenv("DEFAULT_CUSTOM_LABEL") if os.getenv("DEFAULT_CUSTOM_LABEL") else "Custom"
    instructions["custom"] = (DEFAULT_CUSTOM_LABEL, "")

    values=[(key, value[0]) for key, value in instructions.items()]
    result = radiolist_dialog(
        title="Instructions",
        text="Select an instruction",
        values=values,
    ).run()
    if result:
        if result == "custom":
            instruction = getInput(prompt="Custom instruction: ")
            if not instruction:
                return ""
        else:
            instruction = instructions.get(result)[-1]
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
        return instruction + "\n\n" if instruction else ""
    return ""

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
