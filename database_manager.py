import sqlite3
from datetime import datetime
import json
import numpy as np

class DatabaseManager:
    def __init__(self, db_name='pdf_extracts.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.faiss_manager = None

    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_extracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            extracted_text TEXT,
            page_count INTEGER,
            extraction_date DATETIME,
            cleaned BOOLEAN,
            embedding TEXT
        )
        ''')
        self.conn.commit()

    def insert_pdf_extract(self, filename, extracted_text, page_count, cleaned, chunk_embeddings):
        self.cursor.execute('''
        INSERT INTO pdf_extracts (filename, extracted_text, page_count, extraction_date, cleaned, embedding)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, extracted_text, page_count, datetime.now(), cleaned, json.dumps(chunk_embeddings)))
        self.conn.commit()

        if self.faiss_manager:
            vectors = [np.array(emb) for emb in chunk_embeddings]
            chunks = [chunk for chunk, _ in json.loads(extracted_text)]
            self.faiss_manager.add_vectors(vectors, chunks)

    def get_pdf_extract(self, filename):
        self.cursor.execute('SELECT * FROM pdf_extracts WHERE filename = ?', (filename,))
        result = self.cursor.fetchone()
        if result:
            # Convert the chunk embeddings back to a list of lists
            result = list(result)
            result[6] = json.loads(result[6])
        return result

    def close(self):
        self.conn.close()

    def set_faiss_manager(self, faiss_manager):
        self.faiss_manager = faiss_manager

    def search_similar_chunks(self, query_vector, k=5):
        if not self.faiss_manager:
            raise ValueError("FAISS manager not set")
        return self.faiss_manager.search(query_vector, k)
