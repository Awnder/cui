import os
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

class HandwritingRecognition:
    def __init__(self):
        self.black_pixel = np.full((1, 3), 0, dtype=np.uint8)
        self.white_pixel = np.full((1, 3), 255, dtype=np.uint8)
        self.test_sample = np.full((140, 140, 3), self.black_pixel, dtype=np.uint8)
        self.X, self.y = self.fetch_mnist()

    def fetch_mnist(self):
        """Fetches the MNIST dataset from OpenML."""
        mnist = None
        # if os.path.exists("mnist_784.csv"):
        #     mnist = np.loadtxt("mnist_784.csv", delimiter=",")
        #     X = mnist[:, 1:].astype(np.uint8)
        #     y = mnist[:, 0].astype(np.uint8)
        # else:
        mnist = fetch_openml('mnist_784', parser="auto", version=1, as_frame=False)
        X = mnist.data.astype(np.uint8)
        y = mnist.target.astype(np.uint8)
        # np.savetxt("mnist_784.csv", np.column_stack((y, X)), delimiter=",", fmt='%d')
        
        return X, y
    
    def train_models(self):
        """Trains the models on the MNIST dataset."""
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2)
        models = {
            "Random Forest": RandomForestClassifier(n_estimators=25),
            "Decision Tree": DecisionTreeClassifier(),
            "Logistic Regression": LogisticRegression(max_iter=3),
        }

        for model_name, model in models.items():
            print('fitting model:', model_name)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            score = accuracy_score(y_test, y_pred)
            print(f"{model_name} accuracy: {score}")

    def guess_digit(self, drawspace):
        pass

    def clear_drawing(self, drawspace):
        """Clears the drawing canvas and internal array."""
        drawspace.delete("all")  # clear canvas
        self.test_sample[:] = self.black_pixel  # internal representation of drawing

    def draw_handwriting(self, event, drawspace):
        """Draws on the canvas and internal array based on mouse coordinates."""

        # xy-coordinates and radius of the circle being drawn
        x = event.x
        y = event.y
        r = 2
        drawspace.create_oval(x - r, y - r, x + r + 1, y + r + 1, fill="black")
        self.test_sample[y - 2 : y + 3, x - 2 : x + 3] = self.white_pixel

    def draw_window(self):
        window = tk.Tk()
        window.geometry("400x400")
        window.wm_title("Drawing Canvas")

        drawspace = tk.Canvas(
            window,
            width=200,
            height=200,
            bg="white",
            cursor="tcross",
            highlightthickness=1,
            highlightbackground="steelblue",
        )
        title_lbl = tk.Label(window, text="Draw a digit", font=("Helvetica", 16))
        btn_clear = tk.Button(window, text="Clear", command=lambda: self.clear_drawing(drawspace))
        btn_guess = tk.Button(window, text="Guess", command=lambda: self.guess_digit(drawspace))

        drawspace.bind("<B1-Motion>", lambda event: self.draw_handwriting(event, drawspace))
        drawspace.bind("<B1-Motion>", lambda event: self.draw_handwriting(event, drawspace))

        title_lbl.pack()
        drawspace.pack()
        btn_clear.pack()

        window.resizable(False, False)
        window.mainloop()

if __name__ == "__main__":
    hr = HandwritingRecognition()
    print(hr.X.shape)
    print(hr.y.shape)
    hr.train_models()
    hr.draw_window()