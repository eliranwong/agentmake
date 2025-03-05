import numpy as np
import sqlite3, apsw
import json, re, ollama, os, datetime
from typing import Union
from openai import OpenAI
from openai import AzureOpenAI
from mistralai import Mistral
import cohere
try:
    from google import genai
except:
    pass

RAG_EMBEDDING_MODEL = os.getenv("RAG_EMBEDDING_MODEL") if os.getenv("RAG_EMBEDDING_MODEL") else "paraphrase-multilingual"
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE")) if os.getenv("RAG_CHUNK_SIZE") else 1200
RAG_CHUNK_OVERLAP_SIZE = int(os.getenv("RAG_CHUNK_OVERLAP_SIZE")) if os.getenv("RAG_CHUNK_OVERLAP_SIZE") else 200
RAG_QUERY_TOP_K = int(os.getenv("RAG_QUERY_TOP_K")) if os.getenv("RAG_QUERY_TOP_K") else 5

def refinePath(docs_path):
    docs_path = docs_path.strip()
    docs_path = re.sub("^'(.*?)'$", r"\1", docs_path)
    if "\\ " in docs_path or r"\(" in docs_path:
        docs_path = docs_path.replace("\\ ", " ")
        docs_path = docs_path.replace(r"\(", "(")
    return os.path.expanduser(docs_path)

def getValidFileList(list_of_files_or_folders: Union[str, list]):
    if isinstance(list_of_files_or_folders, str):
        try:
            obj = eval(list_of_files_or_folders)
            if isinstance(obj, list):
                list_of_files_or_folders = obj
            else:
                list_of_files_or_folders = [list_of_files_or_folders]
        except:
            list_of_files_or_folders = [list_of_files_or_folders]
    if not list_of_files_or_folders:
        return []
    validFileList = []
    for i in list_of_files_or_folders:
        i = refinePath(i)
        if os.path.isdir(i):
            for ii in os.listdir(i):
                filePath = os.path.join(i, ii)
                if os.path.isfile(filePath):
                    validFileList.append(filePath)
        elif os.path.isfile(i):
            validFileList.append(i)
    return validFileList
            

def getRagPrompt(query: str, context: str) -> str:
    return context if not query else f"""# Provided Context

{context}

# My question:

{query}

# Instruction

Carefully select all the relevant information from the provided context to answer my question in as much detail as possible."""

def recursive_character_text_splitter(text, chunk_size=RAG_CHUNK_SIZE, chunk_overlap=RAG_CHUNK_OVERLAP_SIZE, separators=None):
    if separators is None:
        separators = ["\n\n", "\n", " "]
    
    def _split_text(text_to_split):
        if len(text_to_split) <= chunk_size:
            return [text_to_split]
        
        for separator in separators:
            split_texts = re.split(f'({re.escape(separator)})', text_to_split)
            if len(split_texts) > 1:
                return sum((_split_text(t) for t in split_texts if t.strip()), [])
        
        return [text_to_split[i: i + chunk_size] for i in range(0, len(text_to_split), chunk_size - chunk_overlap)]
    
    return _split_text(text)

def cosine_similarity_matrix(query_vector, document_matrix):
    query_norm = np.linalg.norm(query_vector)
    document_norms = np.linalg.norm(document_matrix, axis=1, keepdims=True)
    document_norms[document_norms == 0] = 1  # Avoid division by zero
    
    similarities = np.dot(document_matrix, query_vector) / (query_norm * document_norms.flatten())
    return similarities

def get_embeddings(texts: list, model: str=RAG_EMBEDDING_MODEL, backend: str=""):
    if backend == "openai" or model in ("text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"):
        return embed_texts_with_openai(texts=texts, model=model)
    if backend == "azure" or model in ("azure-text-embedding-3-small", "azure-text-embedding-3-large", "azure-text-embedding-ada-002"):
        return embed_texts_with_azure(texts=texts, model=model)
    elif backend == "cohere" or model in ("embed-english-v3.0", "embed-english-light-v3.0", "embed-multilingual-v3.0", "embed-multilingual-light-v3.0"):
        return embed_texts_with_cohere(texts=texts, model=model)
    elif backend == "mistral" or model in ("mistral-embed",):
        return embed_texts_with_mistral(texts=texts, model=model)
    elif backend in ("genai", "googleai", "vertexai") or model in ("text-embedding-004",):
        return embed_texts_with_genai(texts=texts, model=model)
    return embed_texts_with_ollama(texts=texts, model=model)

def embed_texts_with_ollama(texts: list, model: str=RAG_EMBEDDING_MODEL):
    try:
        response = ollama.embed(model=model, input=texts)
        embeddings = response.embeddings
        if not embeddings or len(embeddings) != len(texts):
            raise ValueError("Mismatch between texts and embeddings.")
        return np.array(embeddings)
    except Exception as e:
        print(f"Error embedding with Ollama: {e}")
        return None

def embed_texts_with_openai(texts: list, model: str=RAG_EMBEDDING_MODEL):
    if not os.getenv("OPENAI_API_KEY"):
        return None
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    if not model in ("text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"):
        model = "text-embedding-3-large"
    #embeddings = []
    #for i in texts:
    #    embeddings.append(client.embeddings.create(input=i, model=model).data[0].embedding)
    embeddings = [i.embedding for i in client.embeddings.create(input=texts, model=model).data]
    return np.array(embeddings)

def embed_texts_with_azure(texts: list, model: str=RAG_EMBEDDING_MODEL):
    api_key = os.getenv("AZURE_OPENAI_API_KEY") if os.getenv("AZURE_OPENAI_API_KEY") else ""
    azure_endpoint = os.getenv("AZURE_OPENAI_API_ENDPOINT") if os.getenv("AZURE_OPENAI_API_ENDPOINT") else ""
    if not (api_key and azure_endpoint):
        return None
    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=azure_endpoint,
        api_version="2024-10-21",
    )
    if not model in ("azure-text-embedding-3-small", "azure-text-embedding-3-large", "azure-text-embedding-ada-002"):
        model = "azure-text-embedding-3-large"
    #embeddings = []
    #for i in texts:
    #    embeddings.append(client.embeddings.create(input=i, model=model).data[0].embedding)
    embeddings = [i.embedding for i in client.embeddings.create(input=texts, model=model).data]
    return np.array(embeddings)

def embed_texts_with_genai(texts: list, model: str=RAG_EMBEDDING_MODEL):
    if not ((os.getenv("GOOGLE_APPLICATION_CREDENTIALS") and os.getenv("VERTEXAI_PROJECT_ID") and os.getenv("VERTEXAI_SERVICE_LOCATION"))) and not os.getenv("GOOGLEAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        return None
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        client = genai.Client(vertexai=True, project=os.getenv("VERTEXAI_PROJECT_ID"), location=os.getenv("VERTEXAI_SERVICE_LOCATION"))
    elif os.getenv("GOOGLEAI_API_KEY"):
        client = genai.Client(api_key=os.getenv("GOOGLEAI_API_KEY"))
    elif os.getenv("GEMINI_API_KEY"):
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    #if not model in ("text-embedding-004", "text-embedding-005", "text-multilingual-embedding-002"):
    # "text-embedding-005", "text-multilingual-embedding-002" are current not supported in genai sdk
        # reference: https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings#supported-models
    if not model in ("text-embedding-004",):
        model = "text-embedding-004"
    #embeddings = []
    #for i in texts:
    #    embeddings.append(client.models.embed_content(model=model, contents=i).embeddings[0].values)
    embeddings = [i.values for i in client.models.embed_content(model=model, contents=texts).embeddings] # batch
    return np.array(embeddings)

def embed_texts_with_mistral(texts: list, model: str=RAG_EMBEDDING_MODEL):
    if not os.getenv("MISTRAL_API_KEY"):
        return None
    mistral_api_key = os.getenv("MISTRAL_API_KEY").split(",") if os.getenv("MISTRAL_API_KEY") and "," in os.getenv("MISTRAL_API_KEY") else [os.getenv("MISTRAL_API_KEY")]
    client = Mistral(api_key=mistral_api_key[0])
    if not model in ("mistral-embed",):
        model = "mistral-embed"
    embeddings_batch_response = client.embeddings.create(
        model=model,
        inputs=texts,
    )
    embeddings = [i.embedding for i in embeddings_batch_response.data]
    return np.array(embeddings)

def embed_texts_with_cohere(texts: list, model: str=RAG_EMBEDDING_MODEL):
    if not os.getenv("COHERE_API_KEY"):
        return None
    cohere_api_key = os.getenv("COHERE_API_KEY").split(",") if os.getenv("COHERE_API_KEY") and "," in os.getenv("COHERE_API_KEY") else [os.getenv("COHERE_API_KEY")]
    client = cohere.Client(api_key=cohere_api_key[0])
    if not model in ("embed-english-v3.0", "embed-english-light-v3.0", "embed-multilingual-v3.0", "embed-multilingual-light-v3.0"):
        model = "embed-multilingual-v3.0"
    response = client.embed(
        model="embed-multilingual-v3.0",
        texts=texts,
        input_type="classification",
        embedding_types=["float"],
    )
    embeddings = response.embeddings.float
    return np.array(embeddings)

def build_rag_pipeline(db, documents, embedding_model=RAG_EMBEDDING_MODEL, chunk_size=RAG_CHUNK_SIZE, chunk_overlap=RAG_CHUNK_OVERLAP_SIZE, separators=None, backend: str=""):
    for doc in documents:
        chunks = recursive_character_text_splitter(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators)
        embeddings = get_embeddings(chunks, model=embedding_model, backend=backend)
        
        if embeddings is None:
            print(f"Skipping document {doc[30:]} dueto embedding failure.")
            continue
        
        for chunk, embedding in zip(chunks, embeddings):
            db.add(chunk, embedding)

def rag_query(db, query, top_k=RAG_QUERY_TOP_K, embedding_model=RAG_EMBEDDING_MODEL, backend: str=""):
    query_embedding = get_embeddings([query], model=embedding_model, backend=backend)
    if query_embedding is None:
        print("Query embedding failed.")
        return []
    
    return db.search(query_embedding[0], top_k)

class InMemoryVectorDatabase:
    """
    In-Memory Vector Database
    """

    def __init__(self):
        self.vectors = np.array([])
        self.texts = []
    
    def add(self, text, vector):
        if self.vectors.size == 0:
            self.vectors = np.array([vector])
        else:
            self.vectors = np.vstack([self.vectors, vector])
        self.texts.append(text)
    
    def search(self, query_vector, top_k=3):
        if self.vectors.size == 0:
            return []
        similarities = cosine_similarity_matrix(query_vector, self.vectors)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.texts[i] for i in top_indices]

class SqliteVectorDatabase:
    """
    Sqlite Vector Database
    """

    def __init__(self, db_path="vectors.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                vector TEXT
            )
        """
        )
        self.conn.commit()

    def add(self, text, vector):
        vector_str = json.dumps(vector.tolist())
        self.cursor.execute("SELECT COUNT(*) FROM vectors WHERE text = ?", (text,))
        if self.cursor.fetchone()[0] == 0:  # Ensure the text does not already exist
            try:
                self.cursor.execute("INSERT INTO vectors (text, vector) VALUES (?, ?)", (text, vector_str))
                self.conn.commit()
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

    def search(self, query_vector, top_k=3):
        self.cursor.execute("SELECT text, vector FROM vectors")
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]

class ApswVectorDatabase:
    """
    Sqlite Vector Database via `apsw`
    https://rogerbinns.github.io/apsw/pysqlite.html
    """

    def __init__(self, db_path="vectors.db"):
        self.conn = apsw.Connection(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                vector TEXT
            )
        """
        )
        #self.conn.commit()

    def add(self, text, vector):
        vector_str = json.dumps(vector.tolist())
        self.cursor.execute("SELECT COUNT(*) FROM vectors WHERE text = ?", (text,))
        if self.cursor.fetchone()[0] == 0:  # Ensure the text does not already exist
            try:
                self.cursor.execute("INSERT INTO vectors (text, vector) VALUES (?, ?)", (text, vector_str))
                #self.conn.commit()
            except sqlite3.IntegrityError:
                pass  # Ignore duplicate entries

    def search(self, query_vector, top_k=3):
        self.cursor.execute("SELECT text, vector FROM vectors")
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]

class MemoryVectorDatabase:
    """
    Sqlite Vector Database via `apsw`; designed for memory store
    """

    def __init__(self, db_path="vectors.db"):
        self.conn = apsw.Connection(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()

    def __del__(self):
        if not self.conn is None:
            self.conn.close()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id TEXT,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                microsecond INTEGER,
                today TEXT,
                title TEXT,
                category TEXT,
                text TEXT,
                vector TEXT
            )
        """
        )
        #self.conn.commit()

    def add(self, title, text, vector, category=""):
        now = datetime.datetime.now()
        id = now.strftime("%Y%m%d%H%M%S%f")
        year, month, day, hour, minute, microsecond = now.year, now.month, now.day, now.hour, now.minute, now.microsecond
        today = datetime.date.today().strftime("%A")

        vector_str = json.dumps(vector.tolist())
        try:
            self.cursor.execute("INSERT INTO vectors (id, year, month, day, hour, minute, microsecond, today, title, category, text, vector) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, year, month, day, hour, minute, microsecond, today, title, category, text, vector_str))
            #self.conn.commit()
        except sqlite3.IntegrityError:
            pass  # Ignore duplicate entries

    def search(self, query_vector, top_k=3):
        self.cursor.execute("SELECT text, vector FROM vectors")
        rows = self.cursor.fetchall()
        
        if not rows:
            return []
        
        texts, vectors = zip(*[(row[0], np.array(json.loads(row[1]))) for row in rows])
        document_matrix = np.vstack(vectors)
        
        similarities = cosine_similarity_matrix(query_vector, document_matrix)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [texts[i] for i in top_indices]