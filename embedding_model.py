from sentence_transformers import SentenceTransformer
import numpy as np
from openrouter_client import OpenRouterClient

class EmbeddingModel:
    def __init__(self, model_name='all-MiniLM-L6-v2', use_openrouter=False, site_url=None, site_name=None):
        self.use_openrouter = use_openrouter
        if use_openrouter:
            self.openrouter_client = OpenRouterClient(site_url=site_url, site_name=site_name)
        else:
            self.model = SentenceTransformer(model_name)

    def get_embedding(self, text):
        """
        Generate an embedding for the given text.
        
        :param text: Input text string
        :return: Numpy array representing the embedding
        """
        if self.use_openrouter:
            return np.array(self.openrouter_client.generate_embedding(text))
        else:
            return self.model.encode(text)

    def get_embeddings(self, texts):
        """
        Generate embeddings for a list of texts.
        
        :param texts: List of input text strings
        :return: List of numpy arrays representing the embeddings
        """
        if self.use_openrouter:
            return [np.array(self.openrouter_client.generate_embedding(text)) for text in texts]
        else:
            return self.model.encode(texts)

    def cosine_similarity(self, embedding1, embedding2):
        """
        Calculate the cosine similarity between two embeddings.
        
        :param embedding1: First embedding (numpy array)
        :param embedding2: Second embedding (numpy array)
        :return: Cosine similarity score
        """
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def get_embedding_dimension(self):
        """
        Get the dimension of the embeddings produced by this model.
        
        :return: Integer representing the embedding dimension
        """
        if self.use_openrouter:
            # OpenAI's text-embedding-ada-002 model produces 1536-dimensional embeddings
            return 1536
        else:
            return self.model.get_sentence_embedding_dimension()
