"""
File Manager Module
ファイル操作機能を担当するモジュール
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime
import configparser
import os


class FileManager:
    """ファイル操作を担当するクラス"""
    
    def __init__(self):
        self.current_json_path = None
        self.current_comment = ""
        
    def _load_settings_from_ini(self):
        """iniファイルから設定を読み込み"""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), "image_coords_settings.ini")
            
            if os.path.exists(settings_file):
                config = configparser.ConfigParser()
                config.read(settings_file, encoding='utf-8')
                
                settings = {}
                if config.has_section('Settings'):
                    settings['image_directory'] = config.get('Settings', 'image_directory', fallback='未選択')
                    settings['data_directory'] = config.get('Settings', 'data_directory', fallback='未選択')
                    settings['default_mode'] = config.get('Settings', 'default_mode', fallback='編集')
                
                return settings
            else:
                return {
                    'image_directory': '未選択',
                    'data_directory': '未選択',
                    'default_mode': '編集'
                }
                
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return {
                'image_directory': '未選択',
                'data_directory': '未選択',
                'default_mode': '編集'
            }
    
    def _save_settings_to_ini(self, settings):
        """iniファイルに設定を保存"""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), "image_coords_settings.ini")
            
            config = configparser.ConfigParser()
            config.add_section('Settings')
            config.set('Settings', 'image_directory', settings.get('image_directory', ''))
            config.set('Settings', 'data_directory', settings.get('data_directory', ''))
            config.set('Settings', 'default_mode', settings.get('default_mode', '編集'))
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                config.write(f)
                
            return True
            
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
            return False
        
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
    
    def create_settings_dialog(self, parent, on_settings_changed_callback=None):
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
        
        # 既存の設定を読み込み
        current_settings = self._load_settings_from_ini()
        
        # 画像ディレクトリ設定
        image_dir_frame = tk.LabelFrame(main_frame, text="画像ディレクトリ", font=("Arial", 10))
        image_dir_frame.pack(fill=tk.X, pady=10)
        
        # 画像ディレクトリ表示
        self.image_dir_var = tk.StringVar(value=current_settings.get('image_directory', '未選択'))
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
        self.data_dir_var = tk.StringVar(value=current_settings.get('data_directory', '未選択'))
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
        
        self.default_mode_var = tk.StringVar(value=current_settings.get('default_mode', '編集'))
        
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
        
        # 保存状態表示ラベル
        self.save_status_label = tk.Label(button_frame, text="", font=("Arial", 9))
        self.save_status_label.pack(pady=(0, 10))
        
        def validate_settings():
            """設定を検証"""
            issues = []
            
            # 画像ディレクトリの検証
            image_dir = self.image_dir_var.get()
            if image_dir and image_dir != "未選択":
                if not os.path.exists(image_dir):
                    issues.append("画像ディレクトリが存在しません")
                elif not os.path.isdir(image_dir):
                    issues.append("画像ディレクトリが無効です")
            
            # データディレクトリの検証
            data_dir = self.data_dir_var.get()
            if data_dir and data_dir != "未選択":
                if not os.path.exists(data_dir):
                    # データディレクトリは存在しなくても作成できるので警告のみ
                    issues.append("データディレクトリが存在しません（保存時に作成されます）")
            
            return issues
        
        def update_save_status(message, color="black"):
            """保存状態を更新"""
            self.save_status_label.config(text=message, fg=color)
            dialog.after(3000, lambda: self.save_status_label.config(text=""))  # 3秒後にクリア
        
        def save_settings():
            """設定を保存"""
            # 設定を検証
            issues = validate_settings()
            if issues:
                warning_msg = "以下の問題があります：\n" + "\n".join(f"• {issue}" for issue in issues)
                warning_msg += "\n\n設定を保存しますか？"
                
                if not messagebox.askyesno("設定の検証", warning_msg):
                    return
            
            settings = {
                'image_directory': self.image_dir_var.get(),
                'data_directory': self.data_dir_var.get(),
                'default_mode': self.default_mode_var.get()
            }
            
            # 保存中の表示
            update_save_status("保存中...", "blue")
            dialog.update()
            
            # 設定をiniファイルに保存
            if self._save_settings_to_ini(settings):
                update_save_status("設定が保存されました", "green")
                
                # 設定変更コールバックを呼び出し
                if on_settings_changed_callback:
                    on_settings_changed_callback()
                
                # 少し待ってからダイアログを閉じる
                dialog.after(1500, dialog.destroy)
            else:
                update_save_status("設定の保存に失敗しました", "red")
        
        def reset_settings():
            """設定をデフォルト値にリセット"""
            if messagebox.askyesno("設定のリセット", "設定をデフォルト値にリセットしますか？"):
                self.image_dir_var.set("未選択")
                self.data_dir_var.set("未選択")
                self.default_mode_var.set("編集")
                update_save_status("設定がリセットされました", "orange")
        
        def auto_save():
            """変更があった場合に自動保存の提案"""
            current_settings = self._load_settings_from_ini()
            
            # 現在の設定と比較
            if (self.image_dir_var.get() != current_settings.get('image_directory', '未選択') or
                self.data_dir_var.get() != current_settings.get('data_directory', '未選択') or
                self.default_mode_var.get() != current_settings.get('default_mode', '編集')):
                
                update_save_status("設定が変更されています", "orange")
        
        # 設定変更時の自動チェック
        self.image_dir_var.trace('w', lambda *args: dialog.after(500, auto_save))
        self.data_dir_var.trace('w', lambda *args: dialog.after(500, auto_save))
        self.default_mode_var.trace('w', lambda *args: dialog.after(500, auto_save))
        
        def close_dialog():
            """ダイアログを閉じる"""
            # 変更があるかチェック
            current_settings = self._load_settings_from_ini()
            
            if (self.image_dir_var.get() != current_settings.get('image_directory', '未選択') or
                self.data_dir_var.get() != current_settings.get('data_directory', '未選択') or
                self.default_mode_var.get() != current_settings.get('default_mode', '編集')):
                
                result = messagebox.askyesnocancel(
                    "未保存の変更", 
                    "設定が変更されていますが保存しますか？\n\n「はい」: 保存して閉じる\n「いいえ」: 保存しないで閉じる\n「キャンセル」: ダイアログを開いたまま"
                )
                
                if result is True:  # はい - 保存して閉じる
                    save_settings()
                    return
                elif result is False:  # いいえ - 保存しないで閉じる
                    dialog.destroy()
                    return
                # キャンセル - 何もしない（ダイアログを開いたまま）
            else:
                dialog.destroy()
        
        # ボタンフレーム
        buttons_frame = tk.Frame(button_frame)
        buttons_frame.pack()
        
        # ボタンを配置
        save_btn = tk.Button(
            buttons_frame, 
            text="💾 保存", 
            command=save_settings, 
            width=12, 
            font=("Arial", 10),
            bg="#4CAF50",
            fg="white"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(
            buttons_frame, 
            text="🔄 リセット", 
            command=reset_settings, 
            width=12, 
            font=("Arial", 10),
            bg="#FF9800",
            fg="white"
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            buttons_frame, 
            text="❌ キャンセル", 
            command=close_dialog, 
            width=12, 
            font=("Arial", 10),
            bg="#f44336",
            fg="white"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # ダイアログのクローズボタン（X）を押した時も同じ処理
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
