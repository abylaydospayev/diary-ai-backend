"""
embed_store.py
AI memory system for diary entries using semantic embeddings.
Handles vector embeddings, similarity search, and Supabase database operations for contextual diary reflections.
"""

import sqlite3
import time
import json
import numpy as np
from sentence_transformers import SentenceTransformer

DB_PATH = "journal.db"
MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text):
    return MODEL.encode(text).tolist()

def save_entry(entry, reflection, embedding):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO journal_entries (entry, reflection, embedding, timestamp)
        VALUES (?, ?, ?, ?)
    """, (entry, reflection, json.dumps(embedding), int(time.time() * 1000)))
    conn.commit()
    conn.close()

def load_entries(limit=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = "SELECT entry, reflection, embedding, timestamp FROM journal_entries ORDER BY timestamp DESC"
    if limit:
        query += f" LIMIT {limit}"
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "entry": row[0],
            "reflection": row[1],
            "embedding": row[2],
            "timestamp": row[3]
        } for row in rows
    ]


def find_similar_entries(query_embedding, top_k=3):
    entries = load_entries()
    if not entries:
        return []

    vectors = np.array([json.loads(e["embedding"]) for e in entries]).astype("float32")
    query = np.array([query_embedding]).astype("float32")

    import faiss
    index = faiss.IndexFlatL2(len(query_embedding))
    index.add(vectors)
    D, I = index.search(query, top_k)
    return [entries[i] for i in I[0] if i < len(entries)]

def search_memory(query):
    query_embedding = embed(query)
    return find_similar_entries(query_embedding)

def add_entry(text, reflection=""):
    new_embedding = embed(text)
    save_entry(text, reflection, new_embedding)
    return find_similar_entries(new_embedding)
