import numpy as np
import random
from sklearn.utils import Bunch

class KNeighborsClassifier:
	def __init__(self, n_neighbors: int=5, metric: str="euclidean"):
		''' 
		bare initialization of KNeighborsClassifier class 
		Parameters:
			n_neighbors: int, number of neighbors to use by default for kneighbors queries
			metric: str, the distance metric to use for the tree, can be euclidean, manhattan, or cosine
		'''
		self.metric = metric
		self.data = None
		self.classes_ = None
		self.n_features_in_ = None
		self.feature_names_in_ = None
		self.n_samples_fit_ = None

	def fit(self, X: np.ndarray, y: np.ndarray) -> object:
		'''
		Fit the model using X as training data and y as target values
		Parameters:
			X_train: np.ndarray, of shape (n_samples, n_features) or sklearn.utils.Bunch for feature names
				If Bunch, expects the following attributes:
					data_bunch = Bunch(
						data=np.array([[1, 2], [3, 4], [5, 6]]),
						target=np.array([0, 1, 0]),
						feature_names=['feature1', 'feature2'],
						target_names=['class1', 'class2']
					)
			y_train: np.ndarray, of shape (n_samples)
		Returns:
			self: object
		'''
		if isinstance(X, Bunch) and hasattr(X, 'feature_names'):
			self.n_features_in_ = len(X.data[0])
			self.n_samples_fit_ = len(X.data)
			self.feature_names_in_ = X.feature_names
		else:
			self.n_features_in_ = X.shape[1]
			self.n_samples_fit_ = X.shape[0]

		X = X.data if isinstance(X, Bunch) else X

		# self.data = zip(X, y, distances)
		# for x,z,d in self.data:
		# 	print(x,z,d)

		self.data = zip(X, y)
		
		return self

	def predict(self, X: np.ndarray) -> np.ndarray:
		pass
		
	def kneighbors(self, X: np.ndarray=None, n_neighbors: int=None, return_distance: bool=True) -> np.ndarray:
		"""
		
		"""
		if self.metric == "euclidean":
			distances = self._euclidean_distance(X, X)
		elif self.metric == "manhattan":
			distances = self._manhattan_distance(X, X)
		elif self.metric == "cosine":
			distances = self._cosine_distance(X, X)
		else:
			raise ValueError("metric must be euclidean, manhattan, or chebyshev")

	def score(self):
		pass

	def _euclidean_distance(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
		''' 
		p1: np.ndarray of numpy points, p2: np.ndarray of numpy points
		returns: np.ndarray of scalar distances between each point using euclidean
		'''
		return np.linalg.norm(p1[:, np.newaxis, :] - p2[np.newaxis, :, :], axis=2)

	def _manhattan_distance(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
		''' 
		p1: np.ndarray of numpy points, p2: np.ndarray of numpy points
		returns: np.ndarray of scalar distances between each point using manhattan
		'''
		return np.sum(np.abs(p1[:, np.newaxis, :] - p2[np.newaxis, :, :]), axis=2)

	def _cosine_distance(self, p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
		''' 
		p1: np.ndarray of numpy points, p2: np.ndarray of numpy points
		returns: np.ndarray of scalar distances between each point using 1 - cosine similarity
		'''
		return 1 - (np.dot(p1, p2.T) / (np.linalg.norm(p1, axis=1) * np.linalg.norm(p2, axis=1)))
	

if __name__ == "__main__":
	knn = KNeighborsClassifier(n_neighbors=3, metric="euclidean")
	data_bunch = Bunch(
		data=np.array([[1, 2], [3, 4], [5, 6]]),
		target=np.array([0, 1, 0]),
		feature_names=['feature1', 'feature2'],
		target_names=['class1', 'class2']
	)

	d = knn.fit(data_bunch, data_bunch.target)
	# d = knn.fit(np.array([[1, 2], [3, 4], [5, 6]]), np.array([0, 1, 0]))
	print(d.n_features_in_)
	print(d.feature_names_in_)
	print(d.n_samples_fit_)