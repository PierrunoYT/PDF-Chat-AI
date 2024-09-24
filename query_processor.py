from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
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

    def process_query(self, query):
        """
        Process the query by preprocessing and expanding it.
        
        :param query: Input query string
        :return: Processed query string
        """
        preprocessed_tokens = self.preprocess_query(query)
        expanded_tokens = self.expand_query(preprocessed_tokens)
        return ' '.join(expanded_tokens)
