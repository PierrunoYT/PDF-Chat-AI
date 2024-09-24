import os
from pdf_processor import process_multiple_pdfs
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
import numpy as np
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
        self.query_processor = QueryProcessor(self.embedding_model)

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
        similar_chunks = self.faiss_manager.search(query_vector, k)
        
        # Calculate relevance scores and rank results
        ranked_results = []
        for chunk, distance in similar_chunks:
            relevance_score = self.query_processor.calculate_relevance_score(query_text, chunk, distance)
            ranked_results.append((chunk, distance, relevance_score))
        
        # Sort results by relevance score in descending order
        ranked_results.sort(key=lambda x: x[2], reverse=True)
        
        return ranked_results

    def load_index(self):
        self.faiss_manager.load_index(self.faiss_index_file)

if __name__ == "__main__":
    pdf_directory = "path/to/your/pdf/directory"
    pipeline = IndexingPipeline(pdf_directory)

    # Run the indexing process
    results = pipeline.run(save_to_file=True, keyword_filter="report", max_pages=10, clean_text=True)
    print(f"\nProcessed {len(results)} PDF files successfully.")

    # Load the saved index (if you're running the search separately from indexing)
    pipeline.load_index()

    # Example searches
    queries = [
        "What are the main benefits of renewable energy?",
        "Discuss the challenges in implementing artificial intelligence in healthcare.",
        "Explain the impact of climate change on biodiversity."
    ]

    for query in queries:
        print(f"\nSearch results for query: '{query}'")
        ranked_results = pipeline.search_similar_chunks(query, k=5)
        for i, (chunk, distance, relevance_score) in enumerate(ranked_results, 1):
            print(f"Result {i}:")
            print(f"Relevance Score: {relevance_score:.4f}")
            print(f"Distance: {distance:.4f}")
            print(f"Chunk: {chunk[:200]}...")  # Print first 200 characters of the chunk
            print()
