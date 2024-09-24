import sqlite3
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self, db_name='pdf_extracts.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

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
