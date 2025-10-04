from agentmake import config
from prompt_toolkit.input import create_input
from prompt_toolkit.layout import Layout, HSplit
from prompt_toolkit.widgets import Frame, Label
from prompt_toolkit.styles import Style, merge_styles
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.widgets import Frame, TextArea
from prompt_toolkit.layout.menus import CompletionsMenu
from prompt_toolkit.layout import WindowAlign
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.styles import style_from_pygments_cls
from pygments.styles import get_style_by_name
from agentmake import DEFAULT_TEXT_EDITOR, edit_file, readTextFile, writeTextFile
from agentmake.etextedit import launch
from typing import Any, Optional
import os


def getTextArea(input_suggestions:list=None, default_entry="", title="", multiline:bool=True, completion:Optional[Any]=None, scrollbar:bool=True, read_only:bool=False):
    """Get text area input with a border frame"""

    if hasattr(config, "current_prompt") and config.current_prompt and not default_entry:
        default_entry = config.current_prompt
    
    config.current_prompt = ""
    config.cursor_position = 0

    completer = FuzzyCompleter(WordCompleter(input_suggestions, ignore_case=True)) if input_suggestions else None
    
    # Markdown
    pygments_style = get_style_by_name('github-dark')
    markdown_style = style_from_pygments_cls(pygments_style)
    # Define custom style
    custom_style = Style.from_dict({
        #'frame.border': '#00ff00',  # Green border
        #'frame.label': '#ffaa00 bold',  # Orange label
        #'completion-menu': 'bg:#008888 #ffffff',
        #'completion-menu.completion': 'bg:#008888 #ffffff',
        #'completion-menu.completion.current': 'bg:#00aaaa #000000',
        #"status": "reverse",
        "textarea": "bg:#1E1E1E",
    })

    style = merge_styles([markdown_style, custom_style])

    # TextArea with a completer
    text_area = TextArea(
        text=default_entry,
        style="class:textarea",
        lexer=PygmentsLexer(MarkdownLexer),
        multiline=multiline,
        scrollbar=scrollbar,
        read_only=read_only,
        completer=completer,
        complete_while_typing=True,
        focus_on_click=True,
        wrap_lines=True,
    )
    text_area.buffer.cursor_position = len(text_area.text)

    def edit_temp_file(initial_content: str) -> str:
        config.current_prompt = ""
        temp_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "temp", "edit.md")
        writeTextFile(temp_file, initial_content)
        edit_file(temp_file)
        return readTextFile(temp_file).strip()

    # Layout: include a CompletionsMenu
    root_container = HSplit(
        [
            Frame(
                text_area,
                title=title,
            ),
            Label(
                "[Ctrl+S] Send [Ctrl+Q] Exit",
                align=WindowAlign.RIGHT,
                style="fg:grey",
            ),
            CompletionsMenu(
                max_height=8,
                scroll_offset=1,
            ),
        ]
    )
    
    # Create key bindings
    bindings = KeyBindings()

    # launch editor
    @bindings.add("c-p")
    def _(event):
        config.cursor_position = text_area.buffer.cursor_position
        config.current_prompt = text_area.text
        event.app.exit(result=".editprompt")
    # exit
    @bindings.add("c-q")
    def _(event):
        event.app.exit(result="")
    # submit
    @bindings.add("escape", "enter")
    @bindings.add("c-s")
    def _(event):
        if text_area.text.strip():
            event.app.exit(result=text_area.text.strip())
    # submit or new line
    @bindings.add("enter")
    @bindings.add("c-m")
    def _(event):
        text_area.buffer.newline()
    # insert four spaces
    @bindings.add("s-tab")
    def _(event):
        buffer = event.app.current_buffer if event is not None else text_area.buffer
        buffer.insert_text("    ")
    # trigger completion
    @bindings.add("tab")
    @bindings.add("c-i")
    def _(event):
        buffer = event.app.current_buffer if event is not None else text_area.buffer
        buffer.start_completion()
    # close completion menu
    @bindings.add("escape")
    def _(event):
        buffer = event.app.current_buffer if event is not None else text_area.buffer
        buffer.cancel_completion()
    # undo
    @bindings.add("c-z")
    def _(event):
        buffer = event.app.current_buffer if event is not None else text_area.buffer
        buffer.undo()
    # reset buffer
    @bindings.add("c-r")
    def _(event):
        buffer = event.app.current_buffer if event is not None else text_area.buffer
        buffer.reset()
    # Create application
    app = Application(
        layout=Layout(root_container, focused_element=text_area),
        key_bindings=bindings,
        enable_page_navigation_bindings=True,
        style=style,
        #clipboard=PyperclipClipboard(), # not useful if mouse_support is not enabled
        #mouse_support=True, # If enabled; content outside the app becomes unscrollable
        input=create_input(always_prefer_tty=True),
        full_screen=False,
    )
    
    # Run the app
    result = app.run()
    print()
    # edit in full editor
    while result == ".editprompt":
        if DEFAULT_TEXT_EDITOR == "etextedit":
            text_area.text = launch(input_text=config.current_prompt, exitWithoutSaving=True, customTitle=f"BibleMate AI", startAt=config.cursor_position)
        else:
            text_area.text = edit_temp_file(config.current_prompt)
        text_area.buffer.cursor_position = len(text_area.text)
        config.current_prompt = ""
        # Run the non-full-screen text area again
        result = app.run()
        print()
    # return the text content
    return result