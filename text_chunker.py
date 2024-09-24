import re

class TextChunker:
    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text):
        """
        Split the input text into overlapping chunks.
        
        :param text: Input text string
        :return: List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]

            # Adjust chunk to end at a sentence boundary if possible
            if end < text_length:
                sentence_end = self._find_sentence_end(chunk)
                if sentence_end != -1:
                    end = start + sentence_end
                    chunk = text[start:end]

            chunks.append(chunk)
            start = end - self.overlap

        return chunks

    def _find_sentence_end(self, text):
        """
        Find the last sentence boundary in the text.
        
        :param text: Input text string
        :return: Index of the last sentence end, or -1 if not found
        """
        sentence_ends = list(re.finditer(r'[.!?]\s+', text))
        if sentence_ends:
            return sentence_ends[-1].end()
        return -1
