import nltk
from nltk.corpus import stopwords
import requests
import tarfile
import multiprocessing
import os

class BagOfWords:
    def __init__(self):
        self.stopwords = set(stopwords.words('english'))

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
                        

if __name__ == "__main__":
    bag_of_words = BagOfWords()
    bag_of_words._get_imdb_data()
    bag_of_words._create_imdb_csv()