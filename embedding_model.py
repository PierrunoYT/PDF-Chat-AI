from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text):
        """
        Generate an embedding for the given text.
        
        :param text: Input text string
        :return: Numpy array representing the embedding
        """
        return self.model.encode(text)

    def get_embeddings(self, texts):
        """
        Generate embeddings for a list of texts.
        
        :param texts: List of input text strings
        :return: List of numpy arrays representing the embeddings
        """
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
        return self.model.get_sentence_embedding_dimension()
