"""
Documents RAG
search for information in given files
using in-memory vector database
"""

TOOL_SYSTEM = """You carefully examine the user's request to look for files and the question about the files.
Your expertise lies in identifying the following parameters from user's request and returning them in a structured output.

# question

The original question, in detail, about the files

# list_of_files_or_folders

Identify all filenames or file paths or file folder paths specified in the user's request.
Return all of them in a formatted list like ['file1.ext', 'folder2', 'path/file.ext', 'another_path/another_folder']
Return an empty string '' or and empty list '[]' only when there is no file or folder specified"""

def search_files(question: str, list_of_files_or_folders: str, **kwargs):

    from agentmake import extractText
    from agentmake.utils.rag import InMemoryVectorDatabase, build_rag_pipeline, rag_query, getValidFileList
    from agentmake import OllamaAI
    import json, os

    list_of_files_or_folders = getValidFileList(list_of_files_or_folders)
    if not list_of_files_or_folders:
        return None

    embedding_model = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
    OllamaAI.downloadModel(embedding_model)

    db = InMemoryVectorDatabase()

    documents = [extractText(i) for i in list_of_files_or_folders]
    build_rag_pipeline(db, documents, embedding_model=embedding_model)
    retrieved_context = rag_query(db, question, embedding_model=embedding_model)
    retrieved_context = {f"retrieved_information_{(index+1)}": item for index, item in enumerate(retrieved_context)}
    return json.dumps(retrieved_context)

TOOL_SCHEMA = {
    "name": "search_files",
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

TOOL_FUNCTION = search_files
