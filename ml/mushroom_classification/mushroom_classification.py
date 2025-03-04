import numpy as np
import pandas as pd
from sklearn.preprocessing import TargetEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report


class MushroomClassifier:
    def __init__(self):
        self.X, self.y = self._load_data()
        self.rf = None
        self.knn = None

    def _load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Loads the mushroom dataset."""
        data = pd.read_csv("mushrooms.csv")
        data.index = np.arange(1, len(data) + 1)

        X = data.drop("labels", axis=1)
        # 10 common ways to identify poisonous mushrooms, synthesis from searching
        X = X[["stalk_root", "stalk_color_above_ring", "stalk_color_below_ring", "gill_color", "cap_color", "odor", "ring_number", "ring_type", "population", "habitat"]]
        y = data["labels"]

        return X, y

    def fit_predict(self):
        """Trains RandomForest, KNeighbors, and LogisticRegression models."""
        # not using train_test_split because we want to encode the test data with the training data
        # don't want data leakage!
        X_train = self.X[:6000]
        X_test = self.X[6000:]
        y_train = self.y[:6000]
        y_test = self.y[6000:]

        enc = TargetEncoder()
        X_train = pd.DataFrame(enc.fit_transform(X_train, y_train), columns=X_train.columns)
        X_test = pd.DataFrame(enc.transform(X_test), columns=X_test.columns)

        print(X_train)

        rf = RandomForestClassifier(n_estimators=20)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)

        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(X_train, y_train)
        knn_pred = knn.predict(X_test)

        lr = LogisticRegression(max_iter=1000)
        lr.fit(X_train, y_train)
        lr_pred = lr.predict(X_test)

        print("Random Forest Classifier:")
        print(classification_report(y_test, rf_pred))
        print("KNeighbors Classifier:")
        print(classification_report(y_test, knn_pred))
        print("Logistic Regression:")
        print(classification_report(y_test, lr_pred))

        self.rf = rf
        self.knn = knn

    
if __name__ == "__main__":
    mc = MushroomClassifier()
    mc.fit_predict()