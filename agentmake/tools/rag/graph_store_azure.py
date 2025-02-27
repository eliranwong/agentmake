# modified from lightrag example: https://github.com/HKUDS/LightRAG/blob/main/examples/lightrag_azure_openai_demo.py

def search_graph_store_azure(question: str, list_of_files_or_folders: str, **kwargs):

    from agentmake import AGENTMAKE_USER_DIR, extractText
    from agentmake.utils.rag import getValidFileList
    from pathlib import Path
    from lightrag import LightRAG, QueryParam
    from lightrag.utils import EmbeddingFunc
    import os, warnings
    import numpy as np
    from openai import AzureOpenAI

    AZURE_OPENAI_API_VERSION = AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION") if os.getenv("AZURE_OPENAI_API_VERSION") else "2024-10-21"
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_MODEL") if os.getenv("AZURE_OPENAI_MODEL") else "gpt-4o"
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY") if os.getenv("AZURE_OPENAI_API_KEY") else ""
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT") if os.getenv("AZURE_OPENAI_API_ENDPOINT") else ""

    AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_MODEL") if os.getenv("AZURE_EMBEDDING_MODEL") else "azure-text-embedding-3-large"

    # reference: https://github.com/HKUDS/LightRAG

    async def llm_model_func(
        prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
    ) -> str:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})

        chat_completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,  # model = "deployment_name".
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            top_p=kwargs.get("top_p", 1),
            n=kwargs.get("n", 1),
        )
        return chat_completion.choices[0].message.content


    async def embedding_func(texts: list[str]) -> np.ndarray:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_EMBEDDING_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )
        embedding = client.embeddings.create(model=AZURE_EMBEDDING_DEPLOYMENT, input=texts)

        embeddings = [item.embedding for item in embedding.data]
        return np.array(embeddings)

    working_dir = os.path.join(AGENTMAKE_USER_DIR, "graph_store", "azure")
    Path(working_dir).mkdir(parents=True, exist_ok=True)

    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=3072, # as used by the example
            max_token_size=8192,
            func=embedding_func,
        ),
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
    "name": "search_graph_store_azure",
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

TOOL_FUNCTION = search_graph_store_azure