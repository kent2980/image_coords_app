# image_coords_app.py

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

class CoordinateApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Coordinate App")

        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.pack()

        self.btn_select = tk.Button(
            self.root, text="Select Image", command=self.select_image
        )
        self.btn_select.pack(side="left", padx=5, pady=5)

        self.btn_save = tk.Button(
            self.root, text="Save Coordinates", command=self.save_coordinates
        )
        self.btn_save.pack(side="left", padx=5, pady=5)

        self.btn_load_json = tk.Button(
            self.root, text="Load JSON", command=self.load_json
        )
        self.btn_load_json.pack(side="left", padx=5, pady=5)

        self.canvas.bind("<Button-1>", self.on_click)

        self.tk_img = None
        self.coordinates = []

    def on_click(self, event):
        x, y = event.x, event.y
        self.coordinates.append((x, y))
        size = 6  # 線の長さ（直径）
        # 左上から右下
        self.canvas.create_line(
            x - size, y - size, x + size, y + size, fill="white", width=3
        )
        # 右上から左下
        self.canvas.create_line(
            x + size, y - size, x - size, y + size, fill="white", width=3
        )

    def save_coordinates(self):
        if not self.coordinates:
            messagebox.showinfo("Info", "座標がありません。")
            return

        # すでにJSONファイルを開いている場合はそのパスを使う
        file_path = getattr(self, "current_json_path", None)
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not file_path:
                return

        # 画像ファイルパスを取得（なければ空文字列）
        image_path = getattr(self, "current_image_path", "")

        # コメント入力ダイアログ（既存コメントがあれば初期値にする）
        current_comment = getattr(self, "current_comment", "")
        comment = tk.simpledialog.askstring(
            "コメント",
            "コメントを入力してください（任意）:",
            initialvalue=current_comment,
        )

        data = {
            "image_path": image_path,
            "coordinates": [{"x": x, "y": y} for x, y in self.coordinates],
            "comment": comment if comment else "",
        }

        import json

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 保存したファイルパスとコメントを記憶
        self.current_json_path = file_path
        self.current_comment = comment if comment else ""

        messagebox.showinfo("保存完了", "座標をJSON形式で保存しました。")

    def load_json(self):
        import json

        file_path = filedialog.askopenfilename(
            title="JSONファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("エラー", f"JSONファイルの読み込みに失敗しました: {e}")
            return

        image_path = data.get("image_path", "")
        coordinates = data.get("coordinates", [])
        comment = data.get("comment", "")

        if not image_path:
            messagebox.showerror("エラー", "画像パスがJSONに含まれていません。")
            return

        try:
            img = Image.open(image_path)
            img = self._resize_image(img)  # リサイズ追加
        except Exception as e:
            messagebox.showerror("エラー", f"画像を開けませんでした: {e}")
            return

        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.coordinates = [
            (coord["x"], coord["y"])
            for coord in coordinates
            if "x" in coord and "y" in coord
        ]
        # 座標を再描画
        size = 6
        for x, y in self.coordinates:
            self.canvas.create_line(
                x - size, y - size, x + size, y + size, fill="white", width=3
            )
            self.canvas.create_line(
                x + size, y - size, x - size, y + size, fill="white", width=3
            )
        self.current_image_path = image_path
        self.current_json_path = file_path
        self.current_comment = comment
    def _resize_image(self, img):
        # アスペクト比を維持してリサイズ
        img_ratio = img.width / img.height
        canvas_ratio = CANVAS_WIDTH / CANVAS_HEIGHT

        if img_ratio > canvas_ratio:
            new_width = CANVAS_WIDTH
            new_height = int(CANVAS_WIDTH / img_ratio)
        else:
            new_height = CANVAS_HEIGHT
            new_width = int(CANVAS_HEIGHT * img_ratio)
        return img.resize((new_width, new_height), Image.LANCZOS)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        if not file_path:
            return
        try:
            img = Image.open(file_path)
            img = self._resize_image(img)  # リサイズ追加
        except Exception as e:
            messagebox.showerror("エラー", f"画像を開けませんでした: {e}")
            return
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.config(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        self.coordinates.clear()
        self.current_image_path = file_path
        self.current_json_path = None
        self.current_comment = ""

    def run_app(self):
        self.root.mainloop()
