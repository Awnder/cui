import os
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageOps
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score, classification_report
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
        if os.path.exists("mnist_784.csv"):
            mnist = np.loadtxt("mnist_784.csv", delimiter=",")
            X = mnist[:, 1:].astype(np.uint8)
            y = mnist[:, 0].astype(np.uint8)
        else:
            mnist = fetch_openml("mnist_784", parser="auto", version=1, as_frame=False)
            X = mnist.data.astype(np.uint8)
            y = mnist.target.astype(np.uint8)
            np.savetxt("mnist_784.csv", np.column_stack((y, X)), delimiter=",", fmt='%d')

        return X, y

    def train_model(self):
        """Finds best hyperparameters and trains RandomForest on the MNIST dataset."""
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y)

        rf = RandomForestClassifier(n_estimators=20)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)

        print(classification_report(y_test, y_pred))

        return rf

    def guess_digit(self, drawspace, prediction_lbl):
        x = drawspace.winfo_rootx()
        y = drawspace.winfo_rooty()
        width = drawspace.winfo_width()
        height = drawspace.winfo_height()

        # grab and grayscale image
        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        image = image.convert("L")
        image = ImageOps.invert(image) # invert tkinter black and white

        # Display the image in a new window
        # new_window = tk.Toplevel()
        # new_window.title("Captured Image")
        # new_window.geometry("200x200")

        # img = ImageTk.PhotoImage(image.resize((200, 200), Image.Resampling.LANCZOS))
        # panel = tk.Label(new_window, image=img)
        # panel.image = img  # keep a reference to avoid garbage collection
        # panel.pack()

        image = image.resize((28, 28), Image.Resampling.LANCZOS) # high quality resizing

        numpy_array = np.array(image)
        numpy_array = (numpy_array > 128).astype(np.uint8) * 255  # 0 black, 255 white
        numpy_array = numpy_array.reshape(-1, 784)

        print(numpy_array)

        prediction = self.model.predict(numpy_array)
        print(f"Prediction: {prediction}")

        prediction_lbl.config(text=f"Prediction: {prediction}")

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
        self.test_sample[event.y - 2 : event.y + 3, event.x - 2 : event.x + 3] = (
            self.white_pixel
        )
        self.last_x = event.x
        self.last_y = event.y

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
        prediction_lbl = tk.Label(window, text="", font=("Helvetica", 16))
        btn_clear = tk.Button(
            window, text="Clear", command=lambda: self.clear_drawing(drawspace)
        )
        btn_guess = tk.Button(
            window, text="Guess", command=lambda: self.guess_digit(drawspace, prediction_lbl)
        )

        drawspace.bind("<Button-1>", self.start_drawing)
        drawspace.bind("<B1-Motion>", lambda event: self.draw(event, drawspace))

        title_lbl.pack()
        drawspace.pack()
        btn_clear.pack()
        btn_guess.pack()
        prediction_lbl.pack()

        window.resizable(False, False)
        window.mainloop()


if __name__ == "__main__":
    hr = HandwritingRecognition()
    hr.train_model()
    hr.draw_window()
