import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import tkinter.simpledialog
from datetime import datetime

from PIL import Image, ImageTk

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
SIDEBAR_WIDTH = 250

class CoordinateApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Coordinate App")

        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # コンテンツフレーム
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # サイドバーフレーム
        self.sidebar_frame = tk.Frame(self.content_frame, width=SIDEBAR_WIDTH, bg='lightgray')
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)  # サイズ固定

        # コンテンツヘッダーフレーム
        self.content_header_frame = tk.Frame(self.content_frame, height=40)
        self.content_header_frame.pack(fill=tk.X, padx=5, pady=5)
        self.content_header_frame.pack_propagate(False)  # サイズ固定

        # 日付関連の変数
        self.selected_date = datetime.now().date()
        
        # モード関連の変数
        self.mode_var = tk.StringVar(value="編集")
        
        # 日付表示を設定
        self._setup_date_display()

                
        # モード選択フレーム
        mode_frame = tk.Frame(self.content_header_frame)
        mode_frame.pack(side=tk.RIGHT, padx=20, pady=5)
        
        tk.Label(mode_frame, text="モード:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 編集モードラジオボタン
        self.edit_radio = tk.Radiobutton(
            mode_frame,
            text="編集",
            variable=self.mode_var,
            value="編集",
            font=("Arial", 10),
            command=self.on_mode_change
        )
        self.edit_radio.pack(side=tk.LEFT, padx=5)
        
        # 閲覧モードラジオボタン
        self.view_radio = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            font=("Arial", 10),
            command=self.on_mode_change
        )
        self.view_radio.pack(side=tk.LEFT, padx=5)


        # キャンバス上段フレーム（モデル選択と保存名）
        self.canvas_top_frame = tk.Frame(self.content_frame,  height=35)
        self.canvas_top_frame.pack(fill=tk.X, pady=(0, 5))
        self.canvas_top_frame.pack_propagate(False)  # サイズ固定

        # キャンバスフレーム
        self.canvas_frame = tk.Frame(self.content_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # キャンバス上段の内容を設定
        self._setup_canvas_top()

        # キャンバス
        self.canvas = tk.Canvas(self.canvas_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
        self.canvas.pack()

        # サイドバーの内容を設定
        self._setup_sidebar()

        self.canvas.bind("<Button-1>", self.on_click)

        self.tk_img = None
        self.coordinates = []

    def _setup_date_display(self):
        """日付表示エリアの設定"""
        # 日付フレーム（キャンバス内）
        self.date_frame = tk.Frame(self.content_header_frame)
        self.date_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 日付ラベル
        self.date_label = tk.Label(
            self.date_frame, 
            text=f"日付: {self.selected_date.strftime('%Y年%m月%d日')}", 
            font=("Arial", 12), 
        )
        self.date_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 日付選択ボタン
        self.date_button = tk.Button(
            self.date_frame, 
            text="日付を選択", 
            command=self.select_date,
            font=("Arial", 10)
        )
        self.date_button.pack(side=tk.LEFT, padx=10, pady=5)

    def on_mode_change(self):
        """モード変更時の処理"""
        if self.mode_var.get() == "編集":
            # 編集モード: キャンバスクリックイベントを有効化
            self.canvas.bind("<Button-1>", self.on_click)
        else:
            # 閲覧モード: キャンバスクリックイベントを無効化
            self.canvas.unbind("<Button-1>")

    def select_date(self):
        """日付選択ダイアログを表示"""
        # 簡易的な日付選択ダイアログ
        from tkinter import Toplevel
        
        dialog = Toplevel(self.root)
        dialog.title("日付選択")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 中央に配置
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # 日付入力フレーム
        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="日付を入力 (YYYY-MM-DD):").pack()
        
        date_entry = tk.Entry(input_frame, width=20)
        date_entry.pack(pady=10)
        date_entry.insert(0, self.selected_date.strftime('%Y-%m-%d'))
        date_entry.focus()
        
        # ボタンフレーム
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def apply_date():
            try:
                date_str = date_entry.get()
                new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.selected_date = new_date
                self.date_label.config(text=f"日付: {self.selected_date.strftime('%Y年%m月%d日')}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("エラー", "正しい日付形式で入力してください (YYYY-MM-DD)")
        
        def cancel():
            dialog.destroy()
        
        tk.Button(button_frame, text="適用", command=apply_date, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="キャンセル", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Enterキーで適用
        date_entry.bind('<Return>', lambda e: apply_date())

    def _setup_canvas_top(self):
        """キャンバス上段エリアの設定"""
        # モデル選択フレーム
        model_frame = tk.Frame(self.canvas_top_frame)
        model_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(model_frame, text="モデル:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # モデル選択リストボックス
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            model_frame, 
            textvariable=self.model_var, 
            values=["YOLOv8", "YOLOv5", "Faster R-CNN", "SSD", "Custom Model"],
            state="readonly",
            width=15
        )
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        self.model_combobox.current(0)  # デフォルトで最初の項目を選択
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 保存名テキストボックス
        self.save_name_var = tk.StringVar()
        self.save_name_entry = tk.Entry(
            save_frame,
            textvariable=self.save_name_var,
            width=20
        )
        self.save_name_entry.pack(side=tk.LEFT, padx=5)

    def _setup_sidebar(self):
        # サイドバータイトル
        title_label = tk.Label(self.sidebar_frame, text="詳細情報", font=("Arial", 14, "bold"), bg='lightgray')
        title_label.pack(pady=10)

        # アイテム番号フレーム
        item_number_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        item_number_frame.pack(fill=tk.X, padx=10, pady=5)

        # アイテム番号ラベルと入力フィールド（中央寄せ）
        item_content_frame = tk.Frame(item_number_frame, bg='lightgray')
        item_content_frame.pack(expand=True)
        
        item_number_label = tk.Label(item_content_frame, text="番号", font=("Arial", 10), bg='lightgray')
        item_number_label.pack(side=tk.LEFT)
        self.item_number_var = tk.StringVar()
        self.item_number_entry = tk.Entry(item_content_frame, textvariable=self.item_number_var, width=10)
        self.item_number_entry.pack(side=tk.LEFT, padx=5)

        # リファレンスフレーム
        reference_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        reference_frame.pack(fill=tk.X, padx=10, pady=5)

        # リファレンスラベルと入力フィールド（中央寄せ）
        reference_content_frame = tk.Frame(reference_frame, bg='lightgray')
        reference_content_frame.pack(expand=True)
        
        reference_label = tk.Label(reference_content_frame, text="Rf", font=("Arial", 10), bg='lightgray')
        reference_label.pack(side=tk.LEFT)
        self.reference_var = tk.StringVar()
        self.reference_entry = tk.Entry(reference_content_frame, textvariable=self.reference_var, width=15)
        self.reference_entry.pack(side=tk.LEFT, padx=5)

        # 不良名ラベルと選択コンボボックス
        defect_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        defect_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(defect_frame, text="不良名:", font=("Arial", 10), bg='lightgray').pack(side=tk.LEFT)
        self.defect_var = tk.StringVar()
        self.defect_combobox = ttk.Combobox(
            defect_frame, 
            textvariable=self.defect_var, 
            values=["ズレ", "裏", "飛び"],  # 例として3つの不良名を設定
            state="readonly",
            width=15
        )
        self.defect_combobox.pack(side=tk.LEFT, padx=5)
        self.defect_combobox.current(0)  # デフォルトで最初の項目を選択

        # コメントフレーム
        comment_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        comment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # コメントラベル（上部）
        tk.Label(comment_frame, text="コメント:", font=("Arial", 10), bg='lightgray').pack(anchor='w')
        
        # コメント入力フィールド（下部）- Textウィジェットで高さ設定
        self.comment_text = tk.Text(comment_frame, height=12, width=30, font=("Arial", 9))
        self.comment_text.pack(fill=tk.X, pady=(2, 0))

        # 修理済みラベルと（はい・いいえ）ラジオボタン
        repaired_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        repaired_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(repaired_frame, text="修理済み:", font=("Arial", 10), bg='lightgray').pack(side=tk.LEFT)
        self.repaired_var = tk.StringVar(value="いいえ")
        self.repaired_yes = tk.Radiobutton(
            repaired_frame,
            text="はい",
            variable=self.repaired_var,
            value="はい",
            font=("Arial", 10),
            bg='lightgray'
        )   
        self.repaired_yes.pack(side=tk.LEFT, padx=5)
        self.repaired_no = tk.Radiobutton(
            repaired_frame,
            text="いいえ",
            variable=self.repaired_var,
            value="いいえ",
            font=("Arial", 10),
            bg='lightgray'
        )
        self.repaired_no.pack(side=tk.LEFT, padx=5)

    def clear_coordinates(self):
        """座標をクリア"""
        self.coordinates.clear()
        self.canvas.delete("all")
        if self.tk_img:
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)

    def delete_selected_coordinate(self):
        """選択された座標を削除"""
        # サイドバーが削除されたため、この機能は無効
        pass

    def update_sidebar_info(self):
        """サイドバーの情報を更新"""
        # サイドバーが削除されたため、この機能は無効
        pass

    def redraw_canvas(self):
        """キャンバスを再描画"""
        self.canvas.delete("all")
        if self.tk_img:
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        
        # 座標を再描画
        size = 6
        for x, y in self.coordinates:
            self.canvas.create_line(
                x - size, y - size, x + size, y + size, fill="white", width=3
            )
            self.canvas.create_line(
                x + size, y - size, x - size, y + size, fill="white", width=3
            )

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
        self.redraw_canvas()
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

if __name__ == "__main__":
    app = CoordinateApp()
    app.run_app()