import os
from pdf_processor import process_multiple_pdfs
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
from faiss_manager import FAISSManager
from query_processor import QueryProcessor

class IndexingPipeline:
    def __init__(self, pdf_directory, db_name='pdf_extracts.db', faiss_index_file='pdf_embeddings.faiss'):
        self.pdf_directory = pdf_directory
        self.db_manager = DatabaseManager(db_name)
        self.embedding_model = EmbeddingModel()
        self.faiss_manager = FAISSManager(self.embedding_model.get_embedding_dimension())
        self.db_manager.set_faiss_manager(self.faiss_manager)
        self.faiss_index_file = faiss_index_file
        self.query_processor = QueryProcessor()

    def run(self, save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False, chunk_size=1000, chunk_overlap=200):
        results = process_multiple_pdfs(
            self.pdf_directory,
            save_to_file=save_to_file,
            keyword_filter=keyword_filter,
            max_pages=max_pages,
            clean_text=clean_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            use_faiss=True,
            db_manager=self.db_manager,
            embedding_model=self.embedding_model,
            faiss_manager=self.faiss_manager
        )
        
        self.faiss_manager.save_index(self.faiss_index_file)
        self.db_manager.close()
        
        return results

    def search_similar_chunks(self, query_text, k=5):
        query_vector = self.query_processor.query_to_embedding(query_text)
        return self.db_manager.search_similar_chunks(query_vector, k)

if __name__ == "__main__":
    pdf_directory = "path/to/your/pdf/directory"
    pipeline = IndexingPipeline(pdf_directory)
    results = pipeline.run(save_to_file=True, keyword_filter="report", max_pages=10, clean_text=True)
    print(f"\nProcessed {len(results)} PDF files successfully.")

    # Example search
    query = "Example search query"
    similar_chunks = pipeline.search_similar_chunks(query)
    print(f"\nSimilar chunks for query '{query}':")
    for chunk, distance in similar_chunks:
        print(f"Distance: {distance:.4f}")
        print(f"Chunk: {chunk[:100]}...")  # Print first 100 characters of the chunk
        print()
