from openai import OpenAI
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name='text-embedding-3-small'):
        self.client = OpenAI()
        self.model_name = model_name

    def get_embedding(self, text):
        """
        Generate an embedding for the given text.
        
        :param text: Input text string
        :return: Numpy array representing the embedding
        """
        text = text.replace("\n", " ")
        return np.array(self.client.embeddings.create(input=[text], model=self.model_name).data[0].embedding)

    def get_embeddings(self, texts):
        """
        Generate embeddings for a list of texts.
        
        :param texts: List of input text strings
        :return: List of numpy arrays representing the embeddings
        """
        texts = [text.replace("\n", " ") for text in texts]
        embeddings = self.client.embeddings.create(input=texts, model=self.model_name).data
        return [np.array(embedding.embedding) for embedding in embeddings]

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
        return 1536  # OpenAI's text-embedding-3-small model produces 1536-dimensional embeddings
