import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk

class MainApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Image Coords App (ttkbootstrap版)")
        self.geometry("900x600")
        self._setup_ui()

    def _setup_ui(self):
        frame = tb.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        label = tb.Label(frame, text="座標管理システム", font=("Arial", 20, "bold"))
        label.pack(pady=10)

        btn_lot = tb.Button(frame, text="ロット一覧", bootstyle=PRIMARY)
        btn_lot.pack(pady=5)
        btn_worker = tb.Button(frame, text="作業者一覧", bootstyle=INFO)
        btn_worker.pack(pady=5)
        btn_coord = tb.Button(frame, text="座標一覧", bootstyle=SUCCESS)
        btn_coord.pack(pady=5)

        # ここにDB連携や詳細画面への遷移処理を追加可能

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
