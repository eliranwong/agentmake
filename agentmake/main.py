from agentmake import PACKAGE_PATH, DEFAULT_AI_BACKEND, DEFAULT_TEXT_EDITOR, DEFAULT_MARKDOWN_THEME, config, agentmake, edit_configurations, getOpenCommand
from agentmake.etextedit import launch
from agentmake.utils.handle_text import readTextFile, writeTextFile
from agentmake.utils.retrieve_text_output import wrapText
from agentmake.utils.system import getCliOutput
import argparse, os, pprint, sys, pyperclip, shutil, pydoc
import pygments
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.formatted_text import PygmentsTokens
from prompt_toolkit import print_formatted_text
from pygments.styles import get_style_by_name
from prompt_toolkit.styles.pygments import style_from_pygments_cls


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
    parser.add_argument("-sys", "--system", action='append', dest="system", help="system message")
    parser.add_argument("-con", "--context", action='append', dest="context", help="predefined context that is added as the user prompt prefix")
    parser.add_argument("-fup", "--follow_up_prompt", action='append', dest="follow_up_prompt", help="follow-up prompts after an assistant message is generated")
    parser.add_argument("-icp", "--input_content_plugin", action='append', dest="input_content_plugin", help="plugin(s) that works on user input")
    parser.add_argument("-ocp", "--output_content_plugin", action='append', dest="output_content_plugin", help="plugin(s) that works on assistant response")
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
    # others
    parser.add_argument("-ec", "--edit_configurations", action="store_true", dest="edit_configurations", help="edit default configurations with text editor")
    parser.add_argument("-ei", "--edit_input", action="store_true", dest="edit_input", help="edit user input with text editor")
    parser.add_argument("-mh", "--markdown_highlights", action="store_true", dest="markdown_highlights", help="highlight markdown syntax")
    # Parse arguments
    args = parser.parse_args()

    # edit configurations
    if args.edit_configurations:
        edit_configurations()

    # enable chat feature
    if args.chat:
        keep_chat_record = True

    user_prompt = " ".join(args.default) if args.default is not None else ""
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if args.paste:
        clipboardText = getCliOutput("termux-clipboard-get") if shutil.which("termux-clipboard-get") else pyperclip.paste()
    else:
        clipboardText = ""
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
    # run inference
    if user_prompt:
        follow_up_prompt = args.follow_up_prompt if args.follow_up_prompt else []
        if keep_chat_record:
            if args.new_conversation:
                config.messages = []
            elif args.chat_file:
                if os.path.isfile(args.chat_file):
                    try:
                        content = "config.messages = " + readTextFile(args.chat_file)
                        exec(content, globals())
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
            context=args.context,
            follow_up_prompt=follow_up_prompt,
            input_content_plugin=args.input_content_plugin,
            output_content_plugin=args.output_content_plugin,
            agent=args.agent,
            tool=args.tool,
            schema=args.schema,
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
        # display the last assistant response when there is no new user prompt
        last_response = config.messages[-1].get("content", "")
        if last_response:
            if args.markdown_highlights:
                highlightMarkdownSyntax(last_response)
            else:
                print(wrapText(last_response) if args.word_wrap else last_response)
    # copy response to the clipboard
    if args.copy and last_response:
        pydoc.pipepager(last_response, cmd="termux-clipboard-set") if shutil.which("termux-clipboard-set") else pyperclip.copy(last_response)
        print("--------------------\nCopied!")
    # save conversation record
    if keep_chat_record:
        config_file = os.path.join(PACKAGE_PATH, "config.py")
        config_content = "messages = " + pprint.pformat(config.messages)
        writeTextFile(config_file, config_content)
        if args.save_conversation:
            try:
                writeTextFile(args.save_conversation, pprint.pformat(config.messages))
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

def getPygmentsStyle():
    """
    from pygments.styles import get_all_styles
    styles = list(get_all_styles())
    print(styles)
    ['abap', 'algol', 'algol_nu', 'arduino', 'autumn', 'bw', 'borland', 'coffee', 'colorful', 'default', 'dracula', 'emacs', 'friendly_grayscale', 'friendly', 'fruity', 'github-dark', 'gruvbox-dark', 'gruvbox-light', 'igor', 'inkpot', 'lightbulb', 'lilypond', 'lovelace', 'manni', 'material', 'monokai', 'murphy', 'native', 'nord-darker', 'nord', 'one-dark', 'paraiso-dark', 'paraiso-light', 'pastie', 'perldoc', 'rainbow_dash', 'rrt', 'sas', 'solarized-dark', 'solarized-light', 'staroffice', 'stata-dark', 'stata-light', 'tango', 'trac', 'vim', 'vs', 'xcode', 'zenburn']
    """
    return style_from_pygments_cls(get_style_by_name(DEFAULT_MARKDOWN_THEME))

def highlightMarkdownSyntax(content):
    try:
        tokens = list(pygments.lex(content, lexer=MarkdownLexer()))
        print_formatted_text(PygmentsTokens(tokens), style=getPygmentsStyle())
    except:
        print(content)

if __name__ == "__main__":
    test = main()
