import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from utils.coords_loader import load_coordinates


def display_coordinates(coordinates):
    for x, y in coordinates:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")


def load_and_display(coords_path):
    try:
        coordinates = load_coordinates(coords_path)
        display_coordinates(coordinates)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load coordinates: {e}")


def select_and_show_image():
    global img, tk_img, canvas
    file_path = filedialog.askopenfilename(
        title="画像ファイルを選択",
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")],
    )
    if not file_path:
        return
    img = Image.open(file_path)
    tk_img = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)

    coords_path = filedialog.askopenfilename(
        title="座標ファイルを選択",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if not coords_path:
        return
    load_and_display(coords_path)


root = tk.Tk()
root.title("Coordinate Viewer")

canvas = tk.Canvas(root)
canvas.pack()

btn = tk.Button(root, text="画像を選択", command=select_and_show_image)
btn.pack()

root.mainloop()
