"""
File Manager Module
ファイル操作機能を担当するモジュール
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime


class FileManager:
    """ファイル操作を担当するクラス"""
    
    def __init__(self):
        self.current_json_path = None
        self.current_comment = ""
        
    def select_image_file(self):
        """画像ファイルを選択"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")]
        )
        return file_path
        
    def select_json_file(self):
        """JSONファイルを選択"""
        file_path = filedialog.askopenfilename(
            title="JSONファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        return file_path
        
    def save_json_file(self, default_filename=None):
        """JSONファイルの保存先を選択"""
        if self.current_json_path:
            return self.current_json_path
            
        file_path = filedialog.asksaveasfilename(
            initialvalue=default_filename or "coordinates.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        return file_path
        
    def load_json_data(self, file_path):
        """JSONデータを読み込み"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise Exception(f"JSONファイルの読み込みに失敗しました: {e}")
            
    def save_json_data(self, file_path, data):
        """JSONデータを保存"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.current_json_path = file_path
            return True
        except Exception as e:
            raise Exception(f"JSONファイルの保存に失敗しました: {e}")
            
    def create_save_data(self, coordinates, image_path="", form_data=None):
        """保存用データを作成"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "coordinates": [{"x": x, "y": y} for x, y in coordinates]
        }
        
        if form_data:
            data.update({
                "date": form_data.get('date', datetime.now().date()).isoformat() if form_data.get('date') else None,
                "model": form_data.get('model', ''),
                "save_name": form_data.get('save_name', ''),
                "item_number": form_data.get('item_number', ''),
                "reference": form_data.get('reference', ''),
                "defect": form_data.get('defect', ''),
                "comment": form_data.get('comment', ''),
                "repaired": form_data.get('repaired', 'いいえ')
            })
            
        return data
        
    def parse_loaded_data(self, data):
        """読み込んだデータを解析"""
        result = {
            'image_path': data.get('image_path', ''),
            'coordinates': [],
            'form_data': {}
        }
        
        # 座標データを変換
        coordinates = data.get('coordinates', [])
        for coord in coordinates:
            if isinstance(coord, dict) and 'x' in coord and 'y' in coord:
                result['coordinates'].append((coord['x'], coord['y']))
                
        # フォームデータを変換
        if 'date' in data and data['date']:
            try:
                result['form_data']['date'] = datetime.fromisoformat(data['date']).date()
            except:
                pass
                
        form_fields = ['model', 'save_name', 'item_number', 'reference', 'defect', 'comment', 'repaired']
        for field in form_fields:
            if field in data:
                result['form_data'][field] = data[field]
                
        return result
        
    def show_success_message(self, message):
        """成功メッセージを表示"""
        messagebox.showinfo("成功", message)
        
    def show_error_message(self, message):
        """エラーメッセージを表示"""
        messagebox.showerror("エラー", message)
        
    def show_info_message(self, message):
        """情報メッセージを表示"""
        messagebox.showinfo("情報", message)
        
    def ask_comment(self, initial_value=""):
        """コメント入力ダイアログを表示"""
        return simpledialog.askstring(
            "コメント",
            "コメントを入力してください（任意）:",
            initialvalue=initial_value
        )
        
    def create_date_dialog(self, parent, current_date):
        """日付選択ダイアログを作成"""
        dialog = tk.Toplevel(parent)
        dialog.title("日付選択")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # 中央に配置
        dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # 日付入力フレーム
        input_frame = tk.Frame(dialog)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="日付を入力 (YYYY-MM-DD):").pack()
        
        date_entry = tk.Entry(input_frame, width=20)
        date_entry.pack(pady=10)
        date_entry.insert(0, current_date.strftime('%Y-%m-%d'))
        date_entry.focus()
        
        # 結果を保存する変数
        result = {'date': None, 'cancelled': True}
        
        def apply_date():
            try:
                date_str = date_entry.get()
                new_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                result['date'] = new_date
                result['cancelled'] = False
                dialog.destroy()
            except ValueError:
                messagebox.showerror("エラー", "正しい日付形式で入力してください (YYYY-MM-DD)")
        
        def cancel():
            dialog.destroy()
        
        # ボタンフレーム
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="適用", command=apply_date, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="キャンセル", command=cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        # Enterキーで適用
        date_entry.bind('<Return>', lambda e: apply_date())
        
        # ダイアログが閉じるまで待機
        parent.wait_window(dialog)
        
        return result
    
    def create_settings_dialog(self, parent):
        """設定ダイアログを作成"""
        dialog = tk.Toplevel(parent)
        dialog.title("設定")
        dialog.geometry("500x350")
        dialog.resizable(False, False)
        dialog.transient(parent)
        dialog.grab_set()
        
        # 中央に配置
        dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 100,
            parent.winfo_rooty() + 100
        ))
        
        # メインフレーム
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(main_frame, text="アプリケーション設定", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 画像ディレクトリ設定
        image_dir_frame = tk.LabelFrame(main_frame, text="画像ディレクトリ", font=("Arial", 10))
        image_dir_frame.pack(fill=tk.X, pady=10)
        
        # 画像ディレクトリ表示
        self.image_dir_var = tk.StringVar(value="未選択")
        image_display_frame = tk.Frame(image_dir_frame)
        image_display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(image_display_frame, text="現在のディレクトリ:", font=("Arial", 9)).pack(anchor='w')
        image_path_label = tk.Label(
            image_display_frame, 
            textvariable=self.image_dir_var, 
            font=("Arial", 9), 
            bg='white', 
            relief='sunken',
            anchor='w'
        )
        image_path_label.pack(fill=tk.X, pady=(2, 5))
        
        # 画像ディレクトリ選択ボタン
        image_button_frame = tk.Frame(image_dir_frame)
        image_button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def select_image_directory():
            directory = filedialog.askdirectory(title="画像ディレクトリを選択")
            if directory:
                self.image_dir_var.set(directory)
        
        tk.Button(
            image_button_frame, 
            text="ディレクトリを選択", 
            command=select_image_directory,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        # データディレクトリ設定
        data_dir_frame = tk.LabelFrame(main_frame, text="データディレクトリ", font=("Arial", 10))
        data_dir_frame.pack(fill=tk.X, pady=10)
        
        # データディレクトリ表示
        self.data_dir_var = tk.StringVar(value="未選択")
        data_display_frame = tk.Frame(data_dir_frame)
        data_display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(data_display_frame, text="現在のディレクトリ:", font=("Arial", 9)).pack(anchor='w')
        data_path_label = tk.Label(
            data_display_frame, 
            textvariable=self.data_dir_var, 
            font=("Arial", 9), 
            bg='white', 
            relief='sunken',
            anchor='w'
        )
        data_path_label.pack(fill=tk.X, pady=(2, 5))
        
        # データディレクトリ選択ボタン
        data_button_frame = tk.Frame(data_dir_frame)
        data_button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def select_data_directory():
            directory = filedialog.askdirectory(title="データディレクトリを選択")
            if directory:
                self.data_dir_var.set(directory)
        
        tk.Button(
            data_button_frame, 
            text="ディレクトリを選択", 
            command=select_data_directory,
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        # デフォルトモード設定
        mode_frame = tk.LabelFrame(main_frame, text="デフォルトモード", font=("Arial", 10))
        mode_frame.pack(fill=tk.X, pady=10)
        
        self.default_mode_var = tk.StringVar(value="編集")
        
        mode_radio_frame = tk.Frame(mode_frame)
        mode_radio_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(mode_radio_frame, text="起動時のデフォルトモード:", font=("Arial", 10)).pack(anchor='w', pady=(0, 5))
        
        # ラジオボタンフレーム
        radio_frame = tk.Frame(mode_radio_frame)
        radio_frame.pack(anchor='w')
        
        edit_radio = tk.Radiobutton(
            radio_frame,
            text="編集モード",
            variable=self.default_mode_var,
            value="編集",
            font=("Arial", 10)
        )
        edit_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        view_radio = tk.Radiobutton(
            radio_frame,
            text="閲覧モード",
            variable=self.default_mode_var,
            value="閲覧",
            font=("Arial", 10)
        )
        view_radio.pack(side=tk.LEFT)
        
        # 保存ボタン
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        def save_settings():
            """設定を保存"""
            settings = {
                'image_directory': self.image_dir_var.get(),
                'data_directory': self.data_dir_var.get(),
                'default_mode': self.default_mode_var.get()
            }
            
            # 設定をJSONファイルに保存（実装例）
            try:
                import os
                settings_file = os.path.join(os.path.expanduser("~"), "image_coords_settings.json")
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("設定保存", "設定が保存されました")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("エラー", f"設定の保存に失敗しました: {e}")
        
        def close_dialog():
            """ダイアログを閉じる"""
            dialog.destroy()
        
        tk.Button(button_frame, text="保存", command=save_settings, width=12, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="キャンセル", command=close_dialog, width=12, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
