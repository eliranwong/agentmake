"""
Documents RAG
* add given files, if any, to file store
* search for information in file store
* using local sqlite for vector database
"""

TOOL_SYSTEM = """You carefully examine the user's request to look for files and the question about the files.
Your expertise lies in identifying the following parameters from user's request and returning them in a structured output.

# question

The original question, in detail, about the files

# list_of_files_or_folders

Identify all filenames or file paths or file folder paths specified in the user's request.
Return all of them in a formatted list like ['file1.ext', 'folder2', 'path/file.ext', 'another_path/another_folder']
Return an empty string '' or and empty list '[]' only when there is no file or folder specified"""

def search_file_store(question: str, list_of_files_or_folders: str, **kwargs):

    from agentmake import AGENTMAKE_USER_DIR, extractText
    from agentmake.utils.rag import ApswVectorDatabase, build_rag_pipeline, rag_query, getValidFileList
    from agentmake import OllamaAI
    from pathlib import Path
    import os, json

    list_of_files_or_folders = getValidFileList(list_of_files_or_folders)
    # comment the following two lines to allow searching current file store
    #if not list_of_files_or_folders:
    #    return None

    embedding_model = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
    OllamaAI.downloadModel(embedding_model)

    db_dir = os.path.join(AGENTMAKE_USER_DIR, "file_store")
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    db_path = os.path.join(db_dir, "file_store.sqlite")
    db = ApswVectorDatabase(db_path=db_path)

    if list_of_files_or_folders:
        documents = [extractText(i) for i in list_of_files_or_folders]
        build_rag_pipeline(db, documents, embedding_model=embedding_model)
    retrieved_context = rag_query(db, question, embedding_model=embedding_model)
    retrieved_context = {f"retrieved_information_{(index+1)}": item for index, item in enumerate(retrieved_context)}
    return json.dumps(retrieved_context)

TOOL_SCHEMA = {
    "name": "search_file_store",
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

TOOL_FUNCTION = search_file_store
