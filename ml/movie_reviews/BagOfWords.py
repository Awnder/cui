from nltk.corpus import stopwords
from collections import defaultdict
import requests
import tarfile
import string
import re
import os

class BagOfWords:
    def __init__(self):
        self._get_imdb_data()
        self._create_imdb_csv()

        self.bag_of_words = defaultdict(int)

    def _get_imdb_data(self, dir_dest_path: str = 'aclImdb'):
        '''Downloads and extracts Imdb data'''
        if not os.path.exists('aclImdb_v1.tar.gz'):
            response = requests.get('https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz')
            if response.status_code == 200:
                with open('aclImdb_v1.tar.gz', 'wb') as f:
                    f.write(response.content)
            else:
                print('Failed to download data.')
                return

        if not os.path.exists(dir_dest_path):
            with tarfile.open('aclImdb_v1.tar.gz', 'r:gz') as tar:
                members = [
                    member for member in tar.getmembers() 
                    if member.name.startswith(f'{dir_dest_path}/train/') 
                    or member.name.startswith(f'{dir_dest_path}/test/') 
                    or member.name.startswith(f'{dir_dest_path}/README')
                ]
                tar.extractall(members=members)

    def _create_imdb_csv(self, dir_source_path: str = 'aclImdb'):
        '''Processes the Imdb data'''
        if not os.path.exists('train.csv'):
            train_pos_files = os.listdir(os.path.join(f'{dir_source_path}', 'train', 'pos'))
            train_neg_files = os.listdir(os.path.join(f'{dir_source_path}', 'train', 'neg'))

            for file in train_pos_files:
                source_train_pos_file = os.path.join(f'{dir_source_path}', 'train', 'pos', file)
                with open(source_train_pos_file, 'r', encoding='utf-8') as in_f:
                    with open('train.csv', 'a', encoding='utf-8') as out_f:
                        target = file[:-4].split('_')[1]
                        content = in_f.read()
                        out_f.write(f'{target},{content}\n')

            for file in train_neg_files:
                source_train_neg_file = os.path.join(f'{dir_source_path}', 'train', 'neg', file)
                with open(source_train_neg_file, 'r', encoding='utf-8') as in_f:
                    with open('train.csv', 'a', encoding='utf-8') as out_f:
                        target = file[:-4].split('_')[1]
                        content = in_f.read()
                        out_f.write(f'{target},{content}\n')

        if not os.path.exists('test.csv'):
            test_pos_files = os.listdir(os.path.join(f'{dir_source_path}', 'test', 'pos'))
            test_neg_files = os.listdir(os.path.join(f'{dir_source_path}', 'test', 'neg'))

            for file in test_pos_files:
                source_test_pos_file = os.path.join(f'{dir_source_path}', 'test', 'pos', file)
                with open(source_test_pos_file, 'r', encoding='utf-8') as in_f:
                    with open('test.csv', 'a', encoding='utf-8') as out_f:
                        target = file[:-4].split('_')[1]
                        content = in_f.read()
                        out_f.write(f'{target},{content}\n')

            for file in test_neg_files:
                source_test_neg_file = os.path.join(f'{dir_source_path}', 'test', 'neg', file)
                with open(source_test_neg_file, 'r', encoding='utf-8') as in_f:
                    with open('test.csv', 'a', encoding='utf-8') as out_f:
                        target = file[:-4].split('_')[1]
                        content = in_f.read()
                        out_f.write(f'{target},{content}\n')

    def get_imdb_data(self):
        if os.path.exists('train.csv'):
            with open('train.csv', 'r', encoding='utf-8') as f:
                train_data = f.read()
                self.word_tokenize(train_data)

                

    def word_tokenize(self, text: str):
        '''Tokenizes the input text and removes stopwords'''
        text = text.replace('\n', ' ').replace('\r', ' ') # remove newlines
        text = text.translate(str.maketrans('', '', string.punctuation)) # remove punctuation
        text = re.compile(r'<[^>]+>').sub('', text) # remove HTML tags
        text = text.lower() # convert to lowercase
        tokens = text.split()

        for i, word in enumerate(tokens):
            # remove stopwords like "the", "is", "and", etc.
            if word in set(stopwords.words('english')):
                continue
            
            # handle negation words by creating trigrams
            # e.g., "not good" becomes "not good" instead of just "good"
            if word.lower() == 'not':
                trigram = [word]
                if i + 1 < len(tokens):
                    trigram.append(tokens[i + 1])
                if i + 2 < len(tokens):
                    trigram.append(tokens[i + 2])
                self.bag_of_words[' '.join(trigram)] += 1
            else:
                self.bag_of_words[word] += 1

        return self.bag_of_words


if __name__ == "__main__":
    BOW = BagOfWords()