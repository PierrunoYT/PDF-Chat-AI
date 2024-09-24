from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

class QueryProcessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_query(self, query):
        """
        Preprocess the query by tokenizing, removing stopwords, and lemmatizing.
        
        :param query: Input query string
        :return: Preprocessed query string
        """
        # Tokenize the query
        tokens = word_tokenize(query.lower())
        
        # Remove punctuation and stopwords
        tokens = [token for token in tokens if token not in string.punctuation and token not in self.stop_words]
        
        # Lemmatize the tokens
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        # Join the tokens back into a string
        preprocessed_query = ' '.join(lemmatized_tokens)
        
        return preprocessed_query

    def expand_query(self, query):
        """
        Expand the query with synonyms or related terms.
        This is a placeholder function and can be implemented with more advanced NLP techniques.
        
        :param query: Input query string
        :return: Expanded query string
        """
        # For now, we'll just return the original query
        # In a more advanced implementation, you could use techniques like word embeddings
        # or knowledge graphs to expand the query with related terms
        return query

    def process_query(self, query):
        """
        Process the query by preprocessing and expanding it.
        
        :param query: Input query string
        :return: Processed query string
        """
        preprocessed_query = self.preprocess_query(query)
        expanded_query = self.expand_query(preprocessed_query)
        return expanded_query
