import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

class HPTuningValidation:
    def __init__(self):
        self.X = None
        self.y = None

    def _load_data(self):
        data = pd.read_csv('covtype.data.gz', compression='gzip', header=None)
        # 52nd column is target cover_type
        print(len(data.columns))
if __name__ == '__main__':
    hp = HPTuningValidation()
    hp._load_data()