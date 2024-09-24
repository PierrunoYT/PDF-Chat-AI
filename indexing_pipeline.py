import os
from pdf_processor import process_multiple_pdfs
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
import numpy as np
from faiss_manager import FAISSManager
from query_processor import QueryProcessor
from openrouter_client import OpenRouterClient

class IndexingPipeline:
    def __init__(self, pdf_directory, db_name='pdf_extracts.db', faiss_index_file='pdf_embeddings.faiss', use_openrouter=True, site_url=None, site_name=None):
        self.pdf_directory = pdf_directory
        self.db_manager = DatabaseManager(db_name)
        self.embedding_model = EmbeddingModel(use_openrouter=use_openrouter, site_url=site_url, site_name=site_name)
        self.faiss_manager = FAISSManager(self.embedding_model.get_embedding_dimension())
        self.db_manager.set_faiss_manager(self.faiss_manager)
        self.faiss_index_file = faiss_index_file
        self.query_processor = QueryProcessor(self.embedding_model)
        self.openrouter_client = OpenRouterClient(site_url=site_url, site_name=site_name)

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

    def get_top_k_relevant_chunks(self, query_text, k=5):
        """
        Return the top-k most relevant chunks for a given query.
        
        :param query_text: Input query string
        :param k: Number of top chunks to return (default: 5)
        :return: List of tuples containing (chunk, relevance_score)
        """
        ranked_results = self.search_similar_chunks(query_text, k)
        return [(chunk, relevance_score) for chunk, _, relevance_score in ranked_results[:k]]

    def generate_context_aware_response(self, query_text, k=5):
        """
        Generate a context-aware response for the given query using OpenRouter.
        
        :param query_text: Input query string
        :param k: Number of top chunks to use for context (default: 5)
        :return: Generated response string
        """
        top_chunks = self.get_top_k_relevant_chunks(query_text, k)
        prompt = self.query_processor.generate_context_aware_prompt(query_text, top_chunks)
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that provides accurate and relevant information based on the given context."},
            {"role": "user", "content": prompt}
        ]
        
        initial_response = self.openrouter_client.chat_completion(messages)
        
        refinement_prompt = self.query_processor.generate_refinement_prompt(initial_response, query_text, top_chunks)
        refinement_messages = [
            {"role": "system", "content": "You are a helpful AI assistant that refines responses to ensure accuracy and relevance."},
            {"role": "user", "content": refinement_prompt}
        ]
        
        refined_response = self.openrouter_client.chat_completion(refinement_messages)
        return refined_response

    def load_index(self):
        self.faiss_manager.load_index(self.faiss_index_file)

if __name__ == "__main__":
    pdf_directory = "path/to/your/pdf/directory"
    use_openrouter = True  # Set this to True to use OpenRouter
    site_url = "https://your-site-url.com"  # Replace with your actual site URL
    site_name = "Your Site Name"  # Replace with your actual site name
    pipeline = IndexingPipeline(pdf_directory, use_openrouter=use_openrouter, site_url=site_url, site_name=site_name)

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
        print(f"\nQuery: '{query}'")
        response = pipeline.generate_context_aware_response(query, k=5)
        print("Context-aware response:")
        print(response)
        print("\nTop 5 most relevant chunks:")
        top_chunks = pipeline.get_top_k_relevant_chunks(query, k=5)
        for i, (chunk, relevance_score) in enumerate(top_chunks, 1):
            print(f"Result {i}:")
            print(f"Relevance Score: {relevance_score:.4f}")
            print(f"Chunk: {chunk[:200]}...")  # Print first 200 characters of the chunk
            print()
