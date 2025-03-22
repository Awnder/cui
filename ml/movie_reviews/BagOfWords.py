from nltk.corpus import stopwords
from collections import defaultdict
import string
import re

class BagOfWords:
    def __init__(self, extra_stopwords: list = []):
        self.bag_of_words = defaultdict(int)
        self.stopwords = set(stopwords.words('english')).union(set(extra_stopwords))

    def bag(self, text: str) -> dict:
        '''Tokenizes the input text and removes stopwords
        Args:
            text (str): Input text to be tokenized
        Returns:
            dict: A dictionary with words as keys and their frequencies as values
        '''
        text = text.replace('\n', ' ').replace('\r', ' ') # remove newlines
        text = text.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
        text = re.compile(r'<[^>]+>').sub('', text) # remove HTML tags
        text = text.lower() # convert to lowercase
        tokens = text.split()

        for i, word in enumerate(tokens):
            # remove stopwords like "the", "is", "and", etc.
            if word in self.stopwords:
                continue
            
            # handle negation words by creating trigrams
            # e.g., "not good" becomes "not good" instead of just "good"
            # if word.lower() == 'not':
            #     trigram = [word]
            #     if i + 1 < len(tokens):
            #         trigram.append(tokens[i + 1])
            #     if i + 2 < len(tokens):
            #         trigram.append(tokens[i + 2])
            #     self.bag_of_words[' '.join(trigram)] += 1
            # else:
            self.bag_of_words[word] += 1
        return self.bag_of_words
    
    def get(self, top: int = 1000, frequencies: bool = False) -> dict:
        '''Returns the most frequent words in the bag of words
        Args:
            top (int): Number of top words to return. Default is 1000
            frequencies (bool): If True, return words and frequencies, else just the words
        Returns:
            dict/list: A dictionary of the most frequent words or a list of words
        '''
        if frequencies:
            return dict(sorted(self.bag_of_words.items(), key=lambda item: item[1], reverse=True)[:top])
        else:
            return sorted(self.bag_of_words.items(), key=lambda item: item[1], reverse=True).keys()[:top]

    def get_size(self) -> int:
        '''Returns the size of the bag of words
        Returns:
            int: Size of the bag of words
        '''
        return len(self.bag_of_words)

    def empty(self) -> dict:
        '''Resets the bag of words to an empty state
        Returns:
            dict: An empty dictionary
        '''
        self.bag_of_words.clear()
        return self.bag_of_words
    

if __name__ == "__main__":
    BOW = BagOfWords()
    print(BOW.bag_of_words)  # Display the bag of words