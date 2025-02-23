import os
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageGrab, ImageOps
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


class HandwritingRecognition:
    def __init__(self):
        self.black_pixel = np.full((1, 3), 0, dtype=np.uint8)
        self.white_pixel = np.full((1, 3), 255, dtype=np.uint8)
        self.test_sample = np.full((140, 140, 3), self.black_pixel, dtype=np.uint8)
        self.X, self.y = self.fetch_mnist()
        self.model = self.train_model()
        self.last_x, self.last_y = None, None

    def fetch_mnist(self):
        """Fetches the MNIST dataset from OpenML."""
        mnist = None
        # if os.path.exists("mnist_784.csv"):
        #     mnist = np.loadtxt("mnist_784.csv", delimiter=",")
        #     X = mnist[:, 1:].astype(np.uint8)
        #     y = mnist[:, 0].astype(np.uint8)
        # else:
        mnist = fetch_openml("mnist_784", parser="auto", version=1, as_frame=False)
        X = mnist.data.astype(np.uint8)
        y = mnist.target.astype(np.uint8)
        # np.savetxt("mnist_784.csv", np.column_stack((y, X)), delimiter=",", fmt='%d')

        return X, y

    def train_model(self):
        """Finds best hyperparameters and trains RandomForest on the MNIST dataset."""
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y)

        rf = RandomForestClassifier(n_estimators=20)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)

        print(f"Accuracy: {accuracy_score(y_test, y_pred)}")

        return rf

    def guess_digit(self, drawspace):
        drawing_array = self.drawing_to_array(drawspace)
        print(drawing_array)
        print('shape', drawing_array.shape)

        prediction = self.model.predict(drawing_array)
        print(f"Prediction: {prediction}")

    def clear_drawing(self, drawspace):
        """Clears the drawing canvas and internal array."""
        drawspace.delete("all")  # clear canvas
        self.test_sample[:] = self.black_pixel  # internal representation of drawing

    def start_drawing(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event, drawspace):
        """Draws on the canvas and internal array based on mouse coordinates."""
        # xy-coordinates and radius of the circle being drawn
        drawspace.create_line(
            (self.last_x, self.last_y, event.x, event.y),
            width=5,
            fill="black",
            capstyle=tk.ROUND,
            smooth=tk.TRUE,
        )
        # drawspace.create_oval(x - r, y - r, x + r + 1, y + r + 1, fill="black")
        self.test_sample[event.y - 2 : event.y + 3, event.x - 2 : event.x + 3] = (
            self.white_pixel
        )
        self.last_x = event.x
        self.last_y = event.y

    def drawing_to_array(self, drawspace):
        x = drawspace.winfo_rootx() + drawspace.winfo_x()
        y = drawspace.winfo_rooty() + drawspace.winfo_y()
        width = drawspace.winfo_width()
        height = drawspace.winfo_height()

        # grab and grayscale image
        image = ImageGrab.grab((x, y, x + width, y + height))
        image = image.convert("L")
        image = ImageOps.invert(image) # invert tkinter black and white

        # bounding box to crop image directly to drawing canvas
        bbox = image.getbbox()
        if bbox:
            image = image.crop(bbox)

        # image = image.resize((28, 28), Image.Resampling.LANCZOS) # high quality resizing

        numpy_array = np.array(image)
        numpy_array = (numpy_array > 128).astype(np.uint8) * 255  # 0 black, 255 white
        numpy_array = numpy_array.reshape(-1, 784)

        return numpy_array

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
        btn_clear = tk.Button(
            window, text="Clear", command=lambda: self.clear_drawing(drawspace)
        )
        btn_guess = tk.Button(
            window, text="Guess", command=lambda: self.guess_digit(drawspace)
        )

        # drawspace.bind("<B1-Motion>", lambda event: self.draw_handwriting(event, drawspace))
        drawspace.bind("<Button-1>", self.start_drawing)
        drawspace.bind("<B1-Motion>", lambda event: self.draw(event, drawspace))

        title_lbl.pack()
        drawspace.pack()
        btn_clear.pack()
        btn_guess.pack()

        window.resizable(False, False)
        window.mainloop()


if __name__ == "__main__":
    hr = HandwritingRecognition()
    print(hr.X.shape)
    print(hr.y.shape)
    hr.train_model()
    hr.draw_window()
