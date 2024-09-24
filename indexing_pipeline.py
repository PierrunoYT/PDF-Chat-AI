import os
from dotenv import load_dotenv
from pdf_processor import process_multiple_pdfs
from database_manager import DatabaseManager
from embedding_model import EmbeddingModel
import numpy as np
from faiss_manager import FAISSManager
from query_processor import QueryProcessor
from openrouter_client import OpenRouterClient

load_dotenv()

class IndexingPipeline:
    def __init__(self):
        self.db_manager = DatabaseManager(os.getenv('DB_NAME'))
        self.embedding_model = EmbeddingModel(
            use_openrouter=os.getenv('USE_OPENROUTER', 'True').lower() == 'true',
            model_name=os.getenv('OPENAI_EMBEDDING_MODEL', 'openai/text-embedding-3-small')
        )
        self.faiss_manager = FAISSManager(self.embedding_model.get_embedding_dimension())
        self.db_manager.set_faiss_manager(self.faiss_manager)
        self.faiss_index_file = os.getenv('FAISS_INDEX_FILE')
        self.query_processor = QueryProcessor(self.embedding_model)
        self.openrouter_client = OpenRouterClient()

    def run(self, pdf_files, save_to_file=False, keyword_filter=None, max_pages=None, clean_text=False, chunk_size=1000, chunk_overlap=200):
        results = process_multiple_pdfs(
            pdf_files,
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

    def generate_context_aware_response(self, query_text, conversation_history, k=5):
        """
        Generate a context-aware response for the given query using OpenRouter.
        
        :param query_text: Input query string
        :param conversation_history: List of previous messages in the conversation
        :param k: Number of top chunks to use for context (default: 5)
        :return: Generated response string
        """
        processed_query = self.query_processor.process_query(query_text, conversation_history)
        top_chunks = self.get_top_k_relevant_chunks(processed_query, k)
        prompt = self.query_processor.generate_context_aware_prompt(query_text, top_chunks, conversation_history)
        
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that provides accurate and relevant information based on the given context."},
        ] + conversation_history + [
            {"role": "user", "content": prompt}
        ]
        
        response = self.openrouter_client.chat_completion(messages)
        return response

    def load_index(self):
        self.faiss_manager.load_index(self.faiss_index_file)

if __name__ == "__main__":
    pipeline = IndexingPipeline()

    # Run the indexing process
    results = pipeline.run(
        save_to_file=True,
        keyword_filter="report",
        max_pages=10,
        clean_text=True,
        chunk_size=int(os.getenv('CHUNK_SIZE', 1000)),
        chunk_overlap=int(os.getenv('CHUNK_OVERLAP', 200))
    )
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
        response = pipeline.generate_context_aware_response(query, k=int(os.getenv('TOP_K_RESULTS', 5)))
        print("Context-aware response:")
        print(response)
        print("\nTop most relevant chunks:")
        top_chunks = pipeline.get_top_k_relevant_chunks(query, k=int(os.getenv('TOP_K_RESULTS', 5)))
        for i, (chunk, relevance_score) in enumerate(top_chunks, 1):
            print(f"Result {i}:")
            print(f"Relevance Score: {relevance_score:.4f}")
            print(f"Chunk: {chunk[:200]}...")  # Print first 200 characters of the chunk
            print()
