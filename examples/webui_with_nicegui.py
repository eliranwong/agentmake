from agentmake import agentmake
from agentmake import STOP_FILE
from nicegui import ui
#from pathlib import Path
import asyncio, datetime, threading

RUNNING = False
SEND_BUTTON = None
CANCEL_BUTTON = None
REQUEST_INPUT = None
MESSAGES = None
MESSAGE_CONTAINER = None 
SCROLL_AREA = None
AUTO_SCROLL_CHECKBOX = None
STREAMING_EVENT = None


async def handle_send_click():
    """Handles the logic when the Send button is pressed."""
    global RUNNING, REQUEST_INPUT, SCROLL_AREA, MESSAGE_CONTAINER, SEND_BUTTON, AUTO_SCROLL_CHECKBOX, MESSAGES, agentmake, STOP_FILE, STREAMING_EVENT
    if RUNNING:
        #Path(STOP_FILE).touch()
        STREAMING_EVENT.set()
        RUNNING = False
        return None

    if not MESSAGES:
        MESSAGES = [{"role": "system", "content": "You are an AI assistant."}]
    RUNNING = True
    output_markdown = None
    if user_request := REQUEST_INPUT.value:
        SEND_BUTTON.set_text('Cancel')
        SEND_BUTTON.props('color=negative')

        with MESSAGE_CONTAINER:
            ui.chat_message(user_request,
                #name='Eliran Wong',
                stamp=datetime.datetime.now().strftime("%H:%M"),
                avatar='https://avatars.githubusercontent.com/u/25262722?s=96&v=4',
            )
            output_markdown = ui.markdown()

        n = ui.notification(timeout=None)

        STREAMING_EVENT = threading.Event()
        awaitable = asyncio.to_thread(agentmake, MESSAGES, follow_up_prompt=user_request, stream=True, print_on_terminal=False, streaming_event=STREAMING_EVENT)
        task = asyncio.create_task(awaitable)
        while RUNNING and not task.done():
            n.message = f'Loading ...'
            n.spinner = True
            await asyncio.sleep(0.2)
        if not RUNNING:
            task.cancel()
            n.message = 'Cancelled!'
        else:
            n.message = 'Done!'
            MESSAGES = task.result()
            output_markdown.content = MESSAGES[-1]['content']
            output_markdown.update()
            # clean input
            REQUEST_INPUT.set_value('')
            
            if AUTO_SCROLL_CHECKBOX.value:
                # Give the client a moment to render the new content
                await asyncio.sleep(0.1)
                # scroll to the bottom
                await ui.run_javascript(f'getElement({SCROLL_AREA.id}).setScrollPosition("vertical", 99999, 300)')

            RUNNING = False
            
        # restore send button
        SEND_BUTTON.set_text('Send')
        SEND_BUTTON.props('color=primary')
        # stop spinner
        n.spinner = False
        await asyncio.sleep(1)
        n.dismiss()


@ui.page('/')
def main_page():
    global REQUEST_INPUT, MESSAGE_CONTAINER, SEND_BUTTON, AUTO_SCROLL_CHECKBOX, SCROLL_AREA

    with ui.column().classes('w-full h-screen p-4 gap-0'):

        # Capture the ui.scroll_area instance in the global variable
        with ui.scroll_area().classes('w-full flex-grow p-4 border border-gray-300 rounded-lg mb-2') as SCROLL_AREA:
            MESSAGE_CONTAINER = ui.column().classes('w-full items-start gap-2')

        with ui.row().classes('w-full flex-nowrap items-end'):
            REQUEST_INPUT = ui.textarea(placeholder='Enter your message...').props('rows=4').classes('flex-grow h-full resize-none')
            with ui.column().classes('h-full justify-between gap-2'):
                AUTO_SCROLL_CHECKBOX = ui.checkbox('Auto-scroll', value=True).classes('w-full')
                SEND_BUTTON = ui.button('Send', on_click=handle_send_click).classes('w-full')
                

        ui.label('Powered by AgentMake AI | © 2025 | Eliran Wong')
        

# Run the NiceGUI app
ui.run(port=9999)