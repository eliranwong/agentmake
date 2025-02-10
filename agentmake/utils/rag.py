import numpy as np
import sqlite3, apsw
import json, re, ollama, os
from typing import Union

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

def embed_texts_with_ollama(texts, model=RAG_EMBEDDING_MODEL):
    try:
        response = ollama.embed(model=model, input=texts)
        embeddings = response.embeddings
        if not embeddings or len(embeddings) != len(texts):
            raise ValueError("Mismatch between texts and embeddings.")
        return np.array(embeddings)
    except Exception as e:
        print(f"Error embedding with Ollama: {e}")
        return None

def build_rag_pipeline(db, documents, embedding_model=RAG_EMBEDDING_MODEL, chunk_size=RAG_CHUNK_SIZE, chunk_overlap=RAG_CHUNK_OVERLAP_SIZE, separators=None):
    for doc in documents:
        chunks = recursive_character_text_splitter(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators)
        embeddings = embed_texts_with_ollama(chunks, embedding_model)
        
        if embeddings is None:
            print(f"Skipping document {doc[30:]} dueto embedding failure.")
            continue
        
        for chunk, embedding in zip(chunks, embeddings):
            db.add(chunk, embedding)

def rag_query(db, query, top_k=RAG_QUERY_TOP_K, embedding_model=RAG_EMBEDDING_MODEL):
    query_embedding = embed_texts_with_ollama([query], embedding_model)
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
