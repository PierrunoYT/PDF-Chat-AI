import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
import string
import numpy as np
from prompt_engineer import PromptEngineer

class QueryProcessor:
    def __init__(self, embedding_model):
        # Download required NLTK resources
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.embedding_model = embedding_model
        self.prompt_engineer = PromptEngineer()

    def preprocess_query(self, query):
        """
        Preprocess the query by tokenizing, removing stopwords, and lemmatizing.
        
        :param query: Input query string
        :return: Preprocessed query tokens
        """
        # Tokenize the query
        tokens = word_tokenize(query.lower())
        
        # Remove punctuation and stopwords
        tokens = [token for token in tokens if token not in string.punctuation and token not in self.stop_words]
        
        # Lemmatize the tokens
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return lemmatized_tokens

    def expand_query(self, tokens):
        """
        Expand the query with synonyms or related terms using WordNet.
        
        :param tokens: List of preprocessed query tokens
        :return: Expanded list of tokens
        """
        expanded_tokens = []
        for token in tokens:
            expanded_tokens.append(token)
            for syn in wordnet.synsets(token):
                for lemma in syn.lemmas():
                    if lemma.name() != token and lemma.name() not in expanded_tokens:
                        expanded_tokens.append(lemma.name())
        return expanded_tokens

    def combine_with_context(self, query, conversation_history, max_context_length=5):
        """
        Combine the current query with previous context from the conversation history.
        
        :param query: Current query string
        :param conversation_history: List of previous messages in the conversation
        :param max_context_length: Maximum number of previous messages to include
        :return: Combined query string
        """
        context = []
        for message in reversed(conversation_history[-max_context_length:]):
            if message['role'] == 'user':
                context.append(message['content'])
        
        context.append(query)
        return ' '.join(context)

    def process_query(self, query, conversation_history=None):
        """
        Process the query by preprocessing, expanding, and combining with previous context.
        
        :param query: Input query string
        :param conversation_history: List of previous messages in the conversation
        :return: Processed query string
        """
        if conversation_history:
            combined_query = self.combine_with_context(query, conversation_history)
        else:
            combined_query = query
        
        preprocessed_tokens = self.preprocess_query(combined_query)
        expanded_tokens = self.expand_query(preprocessed_tokens)
        return ' '.join(expanded_tokens)

    def query_to_embedding(self, query):
        """
        Convert a query to its embedding representation.
        
        :param query: Input query string
        :return: Embedding vector for the processed query
        """
        processed_query = self.process_query(query)
        return self.embedding_model.get_embedding(processed_query)

    def calculate_relevance_score(self, query, chunk, distance):
        """
        Calculate the relevance score of a chunk based on the query.
        
        :param query: Original query string
        :param chunk: Retrieved text chunk
        :param distance: Distance score from FAISS
        :return: Relevance score
        """
        # Preprocess query and chunk
        query_tokens = set(self.preprocess_query(query))
        chunk_tokens = set(self.preprocess_query(chunk))
        
        # Calculate token overlap
        token_overlap = len(query_tokens.intersection(chunk_tokens)) / len(query_tokens)
        
        # Calculate semantic similarity (inverse of distance)
        semantic_similarity = 1 / (1 + distance)
        
        # Combine scores (you can adjust weights as needed)
        relevance_score = 0.5 * token_overlap + 0.5 * semantic_similarity
        
        return relevance_score

    def generate_context_aware_prompt(self, query, context_chunks, conversation_history):
        """
        Generate a context-aware prompt for the given query, context chunks, and conversation history.
        
        :param query: Original query string
        :param context_chunks: List of (chunk, relevance_score) tuples
        :param conversation_history: List of previous messages in the conversation
        :return: Context-aware prompt string
        """
        return self.prompt_engineer.generate_prompt(query, context_chunks, conversation_history)

    def generate_refinement_prompt(self, response, query, context_chunks):
        """
        Generate a refinement prompt for the given response, query, and context chunks.
        
        :param response: Initial response string
        :param query: Original query string
        :param context_chunks: List of (chunk, relevance_score) tuples
        :return: Refinement prompt string
        """
        context = "\n\n".join(chunk for chunk, _ in context_chunks)
        
        refinement_prompt = f"""
        Your previous response:
        {response}

        Original query: {query}

        Context:
        {context}

        Please review your response and consider the following:
        1. Does it directly address the user's query?
        2. Is it supported by the given context?
        3. Is it concise and clear?

        If necessary, provide a refined response that better addresses these points.

        Refined Response:
        """
        
        return refinement_prompt

    def refine_response(self, response, query, context_chunks):
        """
        Refine the generated response based on the query and context.
        
        :param response: Initial response string
        :param query: Original query string
        :param context_chunks: List of (chunk, relevance_score) tuples
        :return: Refined response string
        """
        return self.prompt_engineer.refine_response(response, query, context_chunks)
