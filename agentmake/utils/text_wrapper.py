from prompt_toolkit.keys import Keys
from prompt_toolkit.input import create_input
import asyncio, shutil, os, wcwidth


class TextWrapper:

    def __init__(self, wrap_words: bool=True):
        self.streaming_finished = False
        self.word_wrap = wrap_words
        self.text_chunk = ""
        self.text_output = ""

    def getStringWidth(self, text):
        width = 0
        for character in text:
            width += wcwidth.wcwidth(character)
        return width

    def wrapStreamWords(self, answer, terminal_width):
        if " " in answer:
            if answer == " ":
                if self.line_width < terminal_width:
                    print(" ", end='', flush=True)
                    self.line_width += 1
            else:
                answers = answer.split(" ")
                for index, item in enumerate(answers):
                    isLastItem = (len(answers) - index == 1)
                    itemWidth = self.getStringWidth(item)
                    newLineWidth = (self.line_width + itemWidth) if isLastItem else (self.line_width + itemWidth + 1)
                    if isLastItem:
                        if newLineWidth > terminal_width:
                            print(f"\n{item}", end='', flush=True)
                            self.line_width = itemWidth
                        else:
                            print(item, end='', flush=True)
                            self.line_width += itemWidth
                    else:
                        if (newLineWidth - terminal_width) == 1:
                            print(f"{item}\n", end='', flush=True)
                            self.line_width = 0
                        elif newLineWidth > terminal_width:
                            print(f"\n{item} ", end='', flush=True)
                            self.line_width = itemWidth + 1
                        else:
                            print(f"{item} ", end='', flush=True)
                            self.line_width += (itemWidth + 1)
        else:
            answerWidth = self.getStringWidth(answer)
            newLineWidth = self.line_width + answerWidth
            if newLineWidth > terminal_width:
                print(f"\n{answer}", end='', flush=True)
                self.line_width = answerWidth
            else:
                print(answer, end='', flush=True)
                self.line_width += answerWidth

    def keyToStopStreaming(self, streaming_event):
        async def readKeys() -> None:
            done = False
            input = create_input()

            def keys_ready():
                nonlocal done
                for key_press in input.read_keys():
                    #print(key_press)
                    if key_press.key in (Keys.ControlQ, Keys.ControlZ):
                        print("\n")
                        done = True
                        streaming_event.set()

            with input.raw_mode():
                with input.attach(keys_ready):
                    while not done:
                        if self.streaming_finished:
                            break
                        await asyncio.sleep(0.1)

        try:
            asyncio.run(readKeys())
        except:
            pass

    def streamOutputs(self, streaming_event, completion, openai_style=False, print_on_terminal=True):
        terminal_width = shutil.get_terminal_size().columns

        def finishOutputs(word_wrap, chat_response):
            self.word_wrap = word_wrap
            self.text_chunk = ""
            self.streaming_finished = True
            self.text_output = chat_response
            if print_on_terminal:
                print("\n\n")

        chat_response = ""
        self.line_width = 0
        block_start = False
        word_wrap = self.word_wrap
        first_event = True
        stop_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "temp", "stop_running")
        for event in completion:
            if os.path.isfile(stop_file):
                os.remove(stop_file)
                finishOutputs(word_wrap, chat_response)
            if streaming_event is None or (not streaming_event.is_set() and not self.streaming_finished):
                # RETRIEVE THE TEXT FROM THE RESPONSE
                if openai_style:
                    # openai
                    # when open api key is invalid for some reasons, event response in string
                    if isinstance(event, str):
                        answer = event
                    elif hasattr(event, "data"): # mistralai
                        answer = event.data.choices[0].delta.content
                    elif not event.choices: # in case of the 1st event of azure's completion
                        continue
                    else:
                        answer = event.choices[0].delta.content
                elif hasattr(event, "delta") and hasattr(event.delta, "text"): # anthropic
                    answer = event.delta.text
                elif hasattr(event, "content_block") and hasattr(event.content_block, "text"):
                    answer = event.content_block.text
                elif str(type(event)).startswith("<class 'anthropic.types"): # anthropic
                    continue
                elif hasattr(event, "message"): # newer ollama python package
                    answer = event.message.content
                elif isinstance(event, dict):
                    if "message" in event:
                        # ollama chat
                        answer = event["message"].get("content", "")
                    else:
                        # llama.cpp chat
                        answer = event["choices"][0]["delta"].get("content", "")
                else:
                    # vertex ai, genai
                    answer = event.text
                # STREAM THE ANSWER
                if answer is not None:
                    if first_event:
                        first_event = False
                        answer = answer.lstrip()
                    # update the chat response
                    chat_response += answer
                    # display the chunk on the terminal
                    if print_on_terminal:
                        # word wrap
                        if answer in ("```", "``"):
                            block_start = not block_start
                            if block_start:
                                self.word_wrap = False
                            else:
                                self.word_wrap = word_wrap
                        if self.word_wrap:
                            if "\n" in answer:
                                lines = answer.split("\n")
                                for index, line in enumerate(lines):
                                    is_last_line = (len(lines) - index == 1)
                                    self.wrapStreamWords(line, terminal_width)
                                    if not is_last_line:
                                        print("\n", end='', flush=True)
                                        self.line_width = 0
                            else:
                                self.wrapStreamWords(answer, terminal_width)
                        else:
                            print(answer, end='', flush=True) # Print the response
            else:
                finishOutputs(word_wrap, chat_response)
                return None

        finishOutputs(word_wrap, chat_response)
