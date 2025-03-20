import requests
import tarfile
import os
import csv
from BagOfWords import BagOfWords

class MovieReview:
    def __init__(self):
        self._get_imdb_data()
        self._create_imdb_csv()
        self.bag_of_words = BagOfWords(extra_stopwords=["movie", "film", "br", "one"])

    def create_bag_of_words(self, percentage: float = 0.5) -> None:
        """Creates a bag of words from the training data
        Args:
            percentage (float): Percentage of the training data to use for creating the bag of words
        """
        if os.path.exists("train_pos.csv"):
            self._bag_csv("train_pos.csv", percentage)                

        if os.path.exists("train_neg.csv"):
            self._bag_csv("train_neg.csv", percentage)

    def _bag_csv(self, file_path: str, percentage: float) -> None:
        """Reads a CSV file and returns its content
        Args:
            file_path (str): Path to the CSV file
        """
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            total_lines = sum(1 for row in reader)

            amount = int(total_lines * percentage)
            count = 0
            f.seek(0)

            for row in reader:
                count += 1
                target = row[0]
                content = row[1]

                if count > amount:
                    break

                self.bag_of_words.bag(content)


    def _get_imdb_data(self, dir_dest_path: str = "aclImdb") -> None:
        """Downloads and extracts Imdb data
        Args:
            dir_dest_path (str): Destination path for the extracted data
        """
        if not os.path.exists("aclImdb_v1.tar.gz"):
            response = requests.get(
                "https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz"
            )
            if response.status_code == 200:
                with open("aclImdb_v1.tar.gz", "wb") as f:
                    f.write(response.content)
            else:
                print("Failed to download data.")
                return

        if not os.path.exists(dir_dest_path):
            with tarfile.open("aclImdb_v1.tar.gz", "r:gz") as tar:
                members = [
                    member
                    for member in tar.getmembers()
                    if member.name.startswith(f"{dir_dest_path}/train/")
                    or member.name.startswith(f"{dir_dest_path}/test/")
                    or member.name.startswith(f"{dir_dest_path}/README")
                ]
                tar.extractall(members=members)

    def _create_imdb_csv(self, dir_source_path: str = "aclImdb") -> None:
        """Processes the Imdb data into train and test CSV files
        Args:
            dir_source_path (str): Source path for the extracted data
        """
        if not os.path.exists("train_pos.csv"):
            train_pos_files = os.listdir(
                os.path.join(f"{dir_source_path}", "train", "pos")
            )
            
            for file in train_pos_files:
                source_train_pos_file = os.path.join(
                    f"{dir_source_path}", "train", "pos", file
                )
                with open(source_train_pos_file, "r", encoding="utf-8") as in_f:
                    with open("train_pos.csv", "a", encoding="utf-8") as out_f:
                        target = file[:-4].split("_")[1]
                        content = in_f.read()
                        out_f.write(f"{target},{content}\n")

        if not os.path.exists("train_neg.csv"):
            train_neg_files = os.listdir(
                    os.path.join(f"{dir_source_path}", "train", "neg")
                )

            for file in train_neg_files:
                source_train_neg_file = os.path.join(
                    f"{dir_source_path}", "train", "neg", file
                )
                with open(source_train_neg_file, "r", encoding="utf-8") as in_f:
                    with open("train_neg.csv", "a", encoding="utf-8") as out_f:
                        target = file[:-4].split("_")[1]
                        content = in_f.read()
                        out_f.write(f"{target},{content}\n")

        if not os.path.exists("test_pos.csv"):
            test_pos_files = os.listdir(
                os.path.join(f"{dir_source_path}", "test", "pos")
            )
            

            for file in test_pos_files:
                source_test_pos_file = os.path.join(
                    f"{dir_source_path}", "test", "pos", file
                )
                with open(source_test_pos_file, "r", encoding="utf-8") as in_f:
                    with open("test_pos.csv", "a", encoding="utf-8") as out_f:
                        target = file[:-4].split("_")[1]
                        content = in_f.read()
                        out_f.write(f"{target},{content}\n")

        if not os.path.exists("test_neg.csv"):
            test_neg_files = os.listdir(
                os.path.join(f"{dir_source_path}", "test", "neg")
            )

            for file in test_neg_files:
                source_test_neg_file = os.path.join(
                    f"{dir_source_path}", "test", "neg", file
                )
                with open(source_test_neg_file, "r", encoding="utf-8") as in_f:
                    with open("test_neg.csv", "a", encoding="utf-8") as out_f:
                        target = file[:-4].split("_")[1]
                        content = in_f.read()
                        out_f.write(f"{target},{content}\n")

if __name__ == "__main__":
    movie_review = MovieReview()
    movie_review.create_bag_of_words()
    print(movie_review.bag_of_words.get(frequencies=True))
    # print(movie_review.bag_of_words.empty())  # Should return an empty dictionary