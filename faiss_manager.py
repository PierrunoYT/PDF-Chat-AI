import faiss
import numpy as np

class FAISSManager:
    def __init__(self, dimension):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)  # Create a CPU index
        self.id_to_text = {}

    def add_vectors(self, vectors, texts):
        if len(vectors) != len(texts):
            raise ValueError("Number of vectors and texts must be the same")
        
        start_id = len(self.id_to_text)
        vectors = np.array(vectors).astype('float32')
        self.index.add(vectors)
        
        for i, text in enumerate(texts):
            self.id_to_text[start_id + i] = text

    def search(self, query_vector, k=5):
        query_vector = np.array([query_vector]).astype('float32')
        distances, indices = self.index.search(query_vector, k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # -1 indicates no match found
                results.append((self.id_to_text[idx], distances[0][i]))
        return results

    def save_index(self, filename):
        faiss.write_index(self.index, filename)

    def load_index(self, filename):
        self.index = faiss.read_index(filename)
