from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import KNNImputer
import pandas as pd
import argparse
import csv
import os

def main():
	### COMMAND LINE INPUT ###
	parser = argparse.ArgumentParser(description="Titanic survival prediction using csv data")
	parser.add_argument("--train", type=str, help="Path to train data")
	parser.add_argument("--test", type=str, help="Path to test data")
	args = parser.parse_args()
	
	if not args.train or not args.test:
		parser.print_help()
		return
	
	### IMPORT DATA ###
	X_train = pd.read_csv(args.train)
	X_test = pd.read_csv(args.test)
	
	### CLEANING DATA ###
	# setting desired columns
	y_train = X_train["Survived"]
	X_train = X_train[["PassengerId", "Pclass", "Sex", "Age", "Fare"]]
	X_test = X_test[["PassengerId", "Pclass", "Sex", "Age", "Fare"]]

	# setting index
	X_train.set_index("PassengerId", inplace=True)
	X_test.set_index("PassengerId", inplace=True)

	# mapping sex to binary
	X_train["Sex"] = X_train["Sex"].map({"male": 0, "female": 1})
	X_test["Sex"] = X_test["Sex"].map({"male": 0, "female": 1})
	

	X_train.drop(columns=["Pclass", "Age", "Fare"], inplace=True)
	X_test.drop(columns=["Pclass", "Age", "Fare"], inplace=True)
	# fill missing ages using KNN - replaces missing values with mean from nearest neighbors
	# knn_imputer = KNNImputer(n_neighbors=3)
	# X_train["Age"] = knn_imputer.fit_transform(X_train[["Age"]])
	# X_test["Age"] = knn_imputer.transform(X_test[["Age"]])
	
	# fill single missing class 3 fare value using mean from only class 3 - this code groups by class and fills missing values with the mean of that class
	# X_test["Fare"] = X_test.groupby("Pclass")["Fare"].transform(lambda x: x.fillna(x.mean()))

	# normalize age and fare data
	# scaler = MinMaxScaler()
	# X_train.loc[:, ["Age", "Fare"]] = pd.DataFrame(scaler.fit_transform(X_train[["Age", "Fare"]].to_numpy()), columns=["Age", "Fare"], index=X_train.index)
	# X_test.loc[:, ["Age", "Fare"]] = pd.DataFrame(scaler.transform(X_test[["Age", "Fare"]].to_numpy()), columns=["Age", "Fare"], index=X_test.index)

	### PREDICTION ###
	knn = KNeighborsClassifier(n_neighbors=3)
	knn.fit(X_train, y_train)

	y_pred = knn.predict(X_test)

	### OUTPUT ###
	y_pred = pd.DataFrame(y_pred, columns=["Survived"], index=X_test.index)
	print(y_pred)
	print("Saved to csv:", "titanic_predictions_with_knn.csv")
	y_pred.to_csv("titanic_predictions_with_knn.csv")

if __name__ == "__main__":
	main()