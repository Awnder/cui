import os
import asyncio
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab, ImageOps, ImageDraw
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

class HandwritingRecognition:
    def __init__(self, custom_data=False):
        self.black_pixel = np.full((1, 3), 0, dtype=np.uint8)
        self.white_pixel = np.full((1, 3), 255, dtype=np.uint8)
        self.test_sample = np.full((140, 140, 3), self.black_pixel, dtype=np.uint8)
        self.X, self.y = self.fetch_custom_data() if custom_data else self.fetch_mnist() 
        self.rf, self.knn = self.train_models()
        self.last_x, self.last_y = None, None

    def fetch_mnist(self) -> tuple[np.ndarray, np.ndarray]:
        """Fetches the MNIST dataset from OpenML."""
        mnist = None
        if os.path.exists("mnist_784.csv"):
            mnist = np.loadtxt("mnist_784.csv", delimiter=",")
            X = mnist[:, 1:].astype(np.uint8)[:5000] # limit to speed up training
            y = mnist[:, 0].astype(np.uint8)[:5000]
        else:
            mnist = fetch_openml("mnist_784", parser="auto", version=1, as_frame=False)
            X = mnist.data.astype(np.uint8)
            y = mnist.target.astype(np.uint8)
            np.savetxt("mnist_784.csv", np.column_stack((y, X)), delimiter=",", fmt='%d')

        return X, y

    def fetch_custom_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Fetches custom data from a CSV file."""
        X, y = None, None
        if os.path.exists("custom_data.csv"):
            data = np.loadtxt("custom_data.csv", delimiter=",")
            X = data[:, 1:].astype(np.uint8)
            y = data[:, 0].astype(np.uint8)

        return X, y

    async def train_models(self) -> tuple[RandomForestClassifier, KNeighborsClassifier, LogisticRegression]:
        """Finds best hyperparameters and trains RandomForest on the MNIST dataset."""
        # X_train, X_test, y_train, y_test = train_test_split(self.X, self.y)

        rf = await self._train_random_forest()
        knn = await self._train_knn()
        lr = await self._train_logistic_regression()

        # rf.fit(X_train, y_train)
        # knn.fit(X_train, y_train)

        # y_pred = rf.predict(X_test)
        # print(classification_report(y_test, y_pred))

        return rf, knn, lr
    
    async def _train_random_forest(self) -> RandomForestClassifier:
        rf = RandomForestClassifier(n_estimators=20)
        rf.fit(self.X, self.y)
        return rf

    async def _train_knn(self) -> KNeighborsClassifier:
        knn = KNeighborsClassifier(n_neighbors=3)
        knn.fit(self.X, self.y)
        return knn
    
    async def _train_logistic_regression(self) -> LogisticRegression:
        lr = LogisticRegression()
        lr.fit(self.X, self.y)
        return lr

    def canvas_to_array(self, drawspace: tk.Canvas) -> tk.Image:
        """Captures, grayscales, and resizes the image drawn on the canvas."""
        x = drawspace.winfo_rootx()
        y = drawspace.winfo_rooty()
        width = drawspace.winfo_width()
        height = drawspace.winfo_height()

        # grab and grayscale image
        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        image = image.convert("L")
        image = ImageOps.invert(image) # invert tkinter black and white
        image = image.resize((28, 28), Image.Resampling.LANCZOS) # high quality resizing

        # display the captured image
        new_window = tk.Toplevel()
        new_window.title("Captured Image")
        new_window.geometry("200x200")
        img = ImageTk.PhotoImage(image.resize((200, 200), Image.Resampling.LANCZOS))
        panel = tk.Label(new_window, image=img)
        panel.image = img  # keep a reference to avoid garbage collection
        panel.pack()

        numpy_array = np.array(image)
        numpy_array = (numpy_array > 128).astype(np.uint8) * 255  # 0 black, 255 white
        numpy_array = numpy_array.reshape(-1, 784)
        return numpy_array

    def guess_digit(self, drawspace: tk.Canvas, main_pred_lbl: tk.Label, pred_lbls: tuple[tk.Label]) -> None:
        """Guesses the digit drawn on the canvas and displays the prediction."""
        numpy_array = self.canvas_to_array(drawspace)

        pred_rf = self.rf.predict(numpy_array)
        neighbors = self.knn.kneighbors(numpy_array, n_neighbors=3, return_distance=False)

        print('rf', pred_rf)
        print('neighbors:', self.knn.predict(numpy_array))

        main_pred_lbl.config(text=f"Prediction: {pred_rf[0]}")
        
        # Display the top 3 neighbors
        neighbor_image_arrays = [self.X[neighbors[0][i]].reshape(28, 28) for i in range(3)]
        neighbor_images = [ImageTk.PhotoImage(image=Image.fromarray(img).resize((50, 50), Image.Resampling.LANCZOS)) for img in neighbor_image_arrays]

        pred_lbls[0].config(image=neighbor_images[0])
        pred_lbls[0].image = neighbor_images[0]  # keep a reference to avoid garbage collection
        pred_lbls[1].config(image=neighbor_images[1])
        pred_lbls[1].image = neighbor_images[1]
        pred_lbls[2].config(image=neighbor_images[2])
        pred_lbls[2].image = neighbor_images[2]

    def add_custom_data(self, drawspace: tk.Canvas, custom_data_combobox: ttk.Combobox) -> None:
        """Adds custom data to the CSV file."""
        numpy_array = self.canvas_to_array(drawspace)

        with open("custom_data.csv", "a") as f:
            f.write(f"{custom_data_combobox.get()},{','.join(map(str, numpy_array[0]))}\n")

    def clear_drawing(self, drawspace: tk.Canvas) -> None:
        """Clears the drawing canvas and internal array."""
        drawspace.delete("all")  # clear canvas
        self.test_sample[:] = self.black_pixel  # internal representation of drawing

    def start_drawing(self, event: tk.Event) -> None:
        """Sets the initial coordinates of the mouse when drawing."""
        self.last_x = event.x
        self.last_y = event.y

    def draw(self, event: tk.Event, drawspace: tk.Canvas) -> None:
        """Draws on the canvas and internal array based on mouse coordinates."""
        # xy-coordinates and radius of the circle being drawn
        drawspace.create_line(
            (self.last_x, self.last_y, event.x, event.y),
            width=10,
            fill="black",
            capstyle=tk.ROUND,
            smooth=tk.TRUE,
        )
        self.test_sample[event.y - 2 : event.y + 3, event.x - 2 : event.x + 3] = (
            self.white_pixel
        )
        self.last_x = event.x
        self.last_y = event.y

    def draw_window(self) -> None:
        """Creates the drawing window and all its components."""
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
        # imagespace = Image.new("L", size=(200, 200), color="white")
        # imagespace_draw = ImageDraw.Draw(imagespace)

        title_lbl = tk.Label(window, text="Draw a digit", font=("Helvetica", 16))
        main_pred_lbl = tk.Label(window, text="", font=("Helvetica", 16))
        pred1_lbl = tk.Label(window, image=None)
        pred2_lbl = tk.Label(window, image=None)
        pred3_lbl = tk.Label(window, image=None)
        pred_lbls = [pred1_lbl, pred2_lbl, pred3_lbl]
        custom_data_combobox = ttk.Combobox(window, values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], state="readonly")
        custom_data_combobox.set("0")
        clear_btn = tk.Button(
            window, text="Clear", command=lambda: self.clear_drawing(drawspace)
        )
        guess_btn = tk.Button(
            window, text="Guess", command=lambda: self.guess_digit(drawspace, main_pred_lbl, pred_lbls)
        )
        add_custom_data_btn = tk.Button(
            window, text="Add Custom Data", command=lambda: self.add_custom_data(drawspace, custom_data_combobox)
        )

        drawspace.bind("<Button-1>", self.start_drawing)
        drawspace.bind("<B1-Motion>", lambda event: self.draw(event, drawspace))

        title_lbl.pack()
        drawspace.pack()
        clear_btn.pack()
        guess_btn.pack()
        main_pred_lbl.pack()
        pred1_lbl.pack(side=tk.LEFT, padx=5)
        pred2_lbl.pack(side=tk.LEFT, padx=5)
        pred3_lbl.pack(side=tk.LEFT, padx=5)
        custom_data_combobox.pack()
        add_custom_data_btn.pack()
        
        window.resizable(False, False)
        window.mainloop()


if __name__ == "__main__":
    hr = HandwritingRecognition(custom_data=False)
    hr.train_models()
    hr.draw_window()
