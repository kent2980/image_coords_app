# image_coords_app.py

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

coordinates = []


def on_click(event):
    x, y = event.x, event.y
    coordinates.append((x, y))
    canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")


def save_coordinates():
    if not coordinates:
        messagebox.showinfo("Info", "座標がありません。")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    if not file_path:
        return
    with open(file_path, "w") as f:
        for x, y in coordinates:
            f.write(f"{x},{y}\n")
    messagebox.showinfo("保存完了", "座標を保存しました。")


def select_image():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
    )
    if not file_path:
        return
    try:
        img = Image.open(file_path)
    except Exception as e:
        messagebox.showerror("エラー", f"画像を開けませんでした: {e}")
        return
    global tk_img
    tk_img = ImageTk.PhotoImage(img)
    canvas.config(width=img.width, height=img.height)
    canvas.create_image(0, 0, anchor="nw", image=tk_img)
    coordinates.clear()
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=tk_img)


root = tk.Tk()
root.title("画像座標取得アプリ")

canvas = tk.Canvas(root)
canvas.pack()

canvas.bind("<Button-1>", on_click)

btn_select = tk.Button(root, text="画像を選択", command=select_image)
btn_select.pack(side="left", padx=5, pady=5)

btn_save = tk.Button(root, text="座標を保存", command=save_coordinates)
btn_save.pack(side="left", padx=5, pady=5)

root.mainloop()
