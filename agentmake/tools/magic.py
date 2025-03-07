# a dummy tool to force fallback to regular chat completion

def magic(messages, **kwargs):
    from agentmake import USER_OS, agentmake
    from copy import deepcopy
    import os
    from agentmake.utils.system import get_linux_distro

    TOOL_PLATFORM = "Linux (" + get_linux_distro().get("name", "") + ")" if USER_OS == "Linux" else USER_OS
    TOOL_PLATFORM = TOOL_PLATFORM.replace("()", "")

    TOOL_SYSTEM = f"""You are a senior python engineer. Your expertise lies in generating python code that works on {TOOL_PLATFORM}, to resolve my request.
Remember, you should format the answer or requested information, if any, into a string that is easily readable by humans.
Use the 'print' function in the last line of your generated code to display the requested information."""

    MAXIMUM_AUTO_HEALING = int(os.getenv("MAXIMUM_AUTO_HEALING")) if os.getenv("MAXIMUM_AUTO_HEALING") else 3
    
    messages_copy = deepcopy(messages)
    messages_copy = agentmake(messages_copy, system=TOOL_SYSTEM, tool="execute_python", **kwargs)
    trial = 0
    while "```buggy_python_code\n" in messages_copy[-1].get("content", "") and trial < MAXIMUM_AUTO_HEALING:
        messages_copy = agentmake(messages_copy, tool="correct_python", **kwargs)
        trial += 1
    return ""

TOOL_SCHEMA = {}
TOOL_DESCRIPTION = """Generate and execute Python code to perform a computing task, access user device information, or search for real-time information. The user's instruction should specify the task and request the information to be printed on the terminal output via the print function. Any buggy python codes are fixed automatically."""

TOOL_FUNCTION = magic