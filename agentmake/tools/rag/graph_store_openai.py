# modified from lightrag example: https://github.com/HKUDS/LightRAG/blob/main/examples/lightrag_openai_demo.py

def search_graph_store_openai(question: str, list_of_files_or_folders: str, **kwargs):
    # reference: https://github.com/HKUDS/LightRAG

    from agentmake import AGENTMAKE_USER_DIR, extractText
    from agentmake.utils.rag import getValidFileList
    from pathlib import Path
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.openai import gpt_4o_mini_complete, gpt_4o_complete, openai_embed
    import os, warnings

    working_dir = os.path.join(AGENTMAKE_USER_DIR, "graph_store", "openai")
    Path(working_dir).mkdir(parents=True, exist_ok=True)

    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=openai_embed,
        llm_model_func=gpt_4o_mini_complete if "mini" in os.getenv("OPENAI_MODEL") else gpt_4o_complete
    )

    list_of_files_or_folders = getValidFileList(list_of_files_or_folders)
    if list_of_files_or_folders:
        for i in list_of_files_or_folders:
            rag.insert(extractText(i))

    print(rag.query(question, param=QueryParam(mode="mix")))

    warnings.filterwarnings("ignore", category=ResourceWarning, message=r"unclosed <socket.socket.*, 58650\)")
    warnings.filterwarnings("ignore", category=ResourceWarning, message=r"unclosed <socket.socket.*, 51148\)")
    warnings.filterwarnings("ignore", category=ResourceWarning, message=r"unclosed <socket.socket.*, 54768\)")
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport <_SelectorSocketTransport")

    return ""

TOOL_SYSTEM = """You carefully examine the user's request to look for files and the question about the files.
Your expertise lies in identifying the following parameters from user's request and returning them in a structured output.

# question

The original question, in detail, about the files

# list_of_files_or_folders

Identify all filenames or file paths or file folder paths specified in the user's request.
Return all of them in a formatted list like ['file1.ext', 'folder2', 'path/file.ext', 'another_path/another_folder']
Return an empty string '' or and empty list '[]' only when there is no file or folder specified"""

TOOL_SCHEMA = {
    "name": "search_graph_store_openai",
    "description": "Retrieve information from files",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The original question about the files",
            },
            "list_of_files_or_folders": {
                "type": "string",
                "description": """Return a list of file or folder paths. Return an empty string '' if there is no file or folder specified.""",
            },
        },
        "required": ["question", "list_of_files_or_folders"],
    },
}

TOOL_FUNCTION = search_graph_store_openai