from agentmake import AGENTMAKE_USERNAME
import os, datetime, re

CURRENT_DATETIME = re.sub(r"\..*?$", "", str(datetime.datetime.now()))
CURRENT_DAY = datetime.date.today().strftime("%A")
MEMORY_CATEGORY = [i.strip() for i in os.getenv("MEMORY_TYPES").split(",")] if os.getenv("MEMORY_TYPE") else ["general", "instruction", "fact", "event", "concept"]

TOOL_SCHEMA = {
    "name": "save_memory",
    "description": """Use this tool if I mention something which you think would be useful in the future and should be saved as a memory. Saved memories will allow you to retrieve snippets of past conversations when needed.""",
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": f"Detailed description of the memory content. I would like you to help me with converting relative dates and times, if any, into exact dates and times, based on the reference that the current datetime is {CURRENT_DATETIME} ({CURRENT_DAY}).",
            },
            "title": {
                "type": "string",
                "description": "Generate a title for this memory",
            },
            "category": {
                "type": "string",
                "description": f"Select a category that is the most relevant to this memory: {str(MEMORY_CATEGORY)}",
                "enum": MEMORY_CATEGORY,
            },
        },
        "required": ["content", "title", "category"]
    }
}

def save_memory(content: str, title: str, category: str, **kwargs):
    from agentmake import AGENTMAKE_USER_DIR
    from agentmake.utils.rag import MemoryVectorDatabase, get_embeddings
    from pathlib import Path
    from agentmake import OllamaAI
    import os
    from agentmake import OLLAMA_FOUND, OLLAMA_NOT_FOUND_MESSAGE
    if not OLLAMA_FOUND:
        print(OLLAMA_NOT_FOUND_MESSAGE)
        return ""
    
    embedding_model = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
    OllamaAI.downloadModel(embedding_model)
    vector = get_embeddings([content], embedding_model)

    db_dir = os.path.join(AGENTMAKE_USER_DIR, "memory_store")
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    memory_store = os.path.join(db_dir, "memory_store.sqlite")
    db = MemoryVectorDatabase(memory_store)
    db.add(title=title, text=content, vector=vector, category=category)
    print("Memory saved!")
    return ""

TOOL_FUNCTION = save_memory