import os
import pandas as pd
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageOps
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier


class HandwritingRecognition:
    def __init__(self):
        self.black_pixel = np.full((1, 3), 0, dtype=np.uint8)
        self.white_pixel = np.full((1, 3), 255, dtype=np.uint8)
        self.test_sample = np.full((140, 140, 3), self.black_pixel, dtype=np.uint8)
        self.X, self.y = self.fetch_mnist()
        self.rf, self.knn = self.train_models()
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

    def train_models(self):
        """Finds best hyperparameters and trains RandomForest on the MNIST dataset."""
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y)

        rf = RandomForestClassifier(n_estimators=20)
        rf.fit(X_train, y_train)
        knn = KNeighborsClassifier(n_neighbors=5)
        knn.fit(X_train, y_train)

        y_pred = rf.predict(X_test)

        print(classification_report(y_test, y_pred))

        return rf, knn

    def guess_digit(self, drawspace, main_pred_lbl, pred_lbls):
        """Guesses the digit drawn on the canvas and displays the prediction."""
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

        pred_rf = self.rf.predict(numpy_array)
        neighbors = self.knn.kneighbors(numpy_array, n_neighbors=3, return_distance=False)

        main_pred_lbl.config(text=f"Prediction: {pred_rf[0]}")
        
        # Display the top 3 neighbors
        neighbor_images = [self.X[neighbors[0][i]].reshape(28, 28) for i in range(3)]
        neighbor_imgs = [ImageTk.PhotoImage(image=Image.fromarray(img).resize((50, 50), Image.Resampling.LANCZOS)) for img in neighbor_images]

        pred_lbls[0].config(image=neighbor_imgs[0])
        pred_lbls[0].image = neighbor_imgs[0]  # keep a reference to avoid garbage collection
        pred_lbls[1].config(image=neighbor_imgs[1])
        pred_lbls[1].image = neighbor_imgs[1]  # keep a reference to avoid garbage collection
        pred_lbls[2].config(image=neighbor_imgs[2])
        pred_lbls[2].image = neighbor_imgs[2]  # keep a reference to avoid garbage collection

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
        main_pred_lbl = tk.Label(window, text="", font=("Helvetica", 16))
        pred1_lbl = tk.Label(window, image=None)
        pred2_lbl = tk.Label(window, image=None)
        pred3_lbl = tk.Label(window, image=None)
        pred_lbls = [pred1_lbl, pred2_lbl, pred3_lbl]
        btn_clear = tk.Button(
            window, text="Clear", command=lambda: self.clear_drawing(drawspace)
        )
        btn_guess = tk.Button(
            window, text="Guess", command=lambda: self.guess_digit(drawspace, main_pred_lbl, pred_lbls)
        )

        drawspace.bind("<Button-1>", self.start_drawing)
        drawspace.bind("<B1-Motion>", lambda event: self.draw(event, drawspace))

        title_lbl.pack()
        drawspace.pack()
        btn_clear.pack()
        btn_guess.pack()
        main_pred_lbl.pack()
        pred1_lbl.pack(side=tk.LEFT, padx=5)
        pred2_lbl.pack(side=tk.LEFT, padx=5)
        pred3_lbl.pack(side=tk.LEFT, padx=5)

        window.resizable(False, False)
        window.mainloop()


if __name__ == "__main__":
    hr = HandwritingRecognition()
    hr.train_models()
    hr.draw_window()
