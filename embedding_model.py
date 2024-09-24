import numpy as np

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI module not found. Using fallback embedding method.")

class EmbeddingModel:
    def __init__(self, model_name='text-embedding-3-small'):
        self.model_name = model_name
        if OPENAI_AVAILABLE:
            self.client = OpenAI()
        else:
            # Fallback to a simple embedding method
            self.dimension = 100

    def get_embedding(self, text):
        """
        Generate an embedding for the given text.
        
        :param text: Input text string
        :return: Numpy array representing the embedding
        """
        text = text.replace("\n", " ")
        if OPENAI_AVAILABLE:
            return np.array(self.client.embeddings.create(input=[text], model=self.model_name).data[0].embedding)
        else:
            return self._fallback_embedding(text)

    def get_embeddings(self, texts):
        """
        Generate embeddings for a list of texts.
        
        :param texts: List of input text strings
        :return: List of numpy arrays representing the embeddings
        """
        texts = [text.replace("\n", " ") for text in texts]
        if OPENAI_AVAILABLE:
            embeddings = self.client.embeddings.create(input=texts, model=self.model_name).data
            return [np.array(embedding.embedding) for embedding in embeddings]
        else:
            return [self._fallback_embedding(text) for text in texts]

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
        if OPENAI_AVAILABLE:
            return 1536  # OpenAI's text-embedding-3-small model produces 1536-dimensional embeddings
        else:
            return self.dimension

    def _fallback_embedding(self, text):
        """
        A simple fallback method to generate embeddings when OpenAI is not available.
        
        :param text: Input text string
        :return: Numpy array representing the embedding
        """
        # This is a very simplistic embedding method and should be replaced with a more sophisticated one
        words = text.lower().split()
        embedding = np.zeros(self.dimension)
        for i, word in enumerate(words[:self.dimension]):
            embedding[i] = hash(word) % 100  # Using hash for simplicity
        return embedding / np.linalg.norm(embedding)
