import re, datetime

CURRENT_DATETIME = re.sub(r"\..*?$", "", str(datetime.datetime.now()))
CURRENT_DAY = datetime.date.today().strftime("%A")

TOOL_SCHEMA = {
    "name": "search_memory",
    "description": """Recall memories of important conversation snippets that we had in the past.""",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": f"The query to be used for searching memories from a vector database. I would like you to help me with converting relative dates and times, if any, into exact dates and times, based on the reference that the current datetime is {CURRENT_DATETIME} ({CURRENT_DAY})."
            },
        },
        "required": ["query"]
    }
}

def search_memory(query: str, **kwargs):
    from agentmake import AGENTMAKE_USER_DIR
    from agentmake.utils.rag import MemoryVectorDatabase, rag_query
    from pathlib import Path
    from agentmake import OllamaAI
    import os, json
    from agentmake import OLLAMA_FOUND, OLLAMA_NOT_FOUND_MESSAGE
    if not OLLAMA_FOUND:
        print(OLLAMA_NOT_FOUND_MESSAGE)
        return ""

    embedding_model = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
    OllamaAI.downloadModel(embedding_model)

    db_dir = os.path.join(AGENTMAKE_USER_DIR, "memory_store")
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    memory_store = os.path.join(db_dir, "memory_store.sqlite")
    db = MemoryVectorDatabase(memory_store)

    retrieved_context = rag_query(db, query, embedding_model=embedding_model)
    retrieved_context = {f"retrieved_memory_{(index+1)}": item for index, item in enumerate(retrieved_context)}
    return json.dumps(retrieved_context)

TOOL_FUNCTION = search_memory
