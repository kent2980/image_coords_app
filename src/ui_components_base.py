"""
UI Components Base Module
UIコンポーネントの基本クラス - 共通機能を提供
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import sys
import configparser
import re
import csv
from PIL import Image, ImageTk
from pathlib import Path

class UIComponentsBase:
    """UIコンポーネントの基本クラス"""
    
    def __init__(self, root, callbacks=None):
        self.root = root
        self.callbacks = callbacks or {}
        
        # 定数
        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 600
        self.SIDEBAR_WIDTH = 250
        
        # 変数
        self.selected_date = datetime.now().date()
        self.mode_var = tk.StringVar(value="編集")
        self.model_var = tk.StringVar()
        self.save_name_var = tk.StringVar()
        self.item_number_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.defect_var = tk.StringVar()
        self.repaired_var = tk.StringVar(value="いいえ")
        self.current_lot_number = ""  # 現在保存されているロット番号
        self.current_worker_no = ""  # 現在設定されている作業者No
        self.current_worker_name = ""  # 現在設定されている作業者名
        
        # UI要素の参照を保持
        self.date_label = None
        self.canvas = None
        self.comment_text = None
        self.lot_number_label = None  # ロット番号ラベルの参照
        self.worker_label = None  # 作業者ラベルの参照
        
    def _get_executable_directory(self):
        """実行ファイルのディレクトリを取得"""
        if getattr(sys, 'frozen', False):
            # PyInstallerでビルドされた実行ファイルの場合
            return os.path.dirname(sys.executable)
        else:
            # 開発環境の場合
            return os.path.dirname(os.path.abspath(__file__))
    
    def _load_settings(self):
        """設定ファイル（ini）から設定を読み込み"""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), "image_coords_settings.ini")
            
            if os.path.exists(settings_file):
                config = configparser.ConfigParser()
                config.read(settings_file, encoding='utf-8')
                
                # 設定を辞書形式で返す
                settings = {}
                if config.has_section('Settings'):
                    settings['image_directory'] = config.get('Settings', 'image_directory', fallback='')
                    settings['data_directory'] = config.get('Settings', 'data_directory', fallback='')
                    settings['default_mode'] = config.get('Settings', 'default_mode', fallback='編集')
                
                return settings
            else:
                # ファイルが存在しない場合はデフォルト設定を返す
                return {
                    'image_directory': '',
                    'data_directory': '',
                    'default_mode': '編集'
                }
                
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return {
                'image_directory': '',
                'data_directory': '',
                'default_mode': '編集'
            }
    
    def _load_defects_from_file(self):
        """外部ファイルから不良名リストを読み込み"""
        try:
            # 実行ファイルと同じディレクトリのdefects.txtを読み込み
            defects_file = os.path.join(self._get_executable_directory(), "defects.txt")
            
            if os.path.exists(defects_file):
                with open(defects_file, 'r', encoding='utf-8') as f:
                    defects = [line.strip() for line in f.readlines() if line.strip()]
                    return defects if defects else ["ズレ"]  # 空の場合はデフォルト値
            else:
                # ファイルが存在しない場合はデフォルト値を返す
                return ["ズレ", "裏", "飛び"]
                
        except Exception as e:
            # エラーが発生した場合はデフォルト値を返す
            print(f"不良名ファイル読み込みエラー: {e}")
            return ["ズレ", "裏", "飛び"]
        
    def setup_main_layout(self):
        """メインレイアウトをセットアップ"""
        self.root.title("Image Coordinate App")
        
        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # コンテンツフレーム
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # サイドバーフレーム
        self.sidebar_frame = tk.Frame(self.content_frame, width=self.SIDEBAR_WIDTH)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)
        
        # コンテンツヘッダーフレーム
        self.content_header_frame = tk.Frame(self.content_frame, height=40)
        self.content_header_frame.pack(fill=tk.X, padx=5, pady=5)
        self.content_header_frame.pack_propagate(False)
        
        # キャンバス上段フレーム
        self.canvas_top_frame = tk.Frame(self.content_frame, height=35)
        self.canvas_top_frame.pack(fill=tk.X, pady=(0, 5))
        self.canvas_top_frame.pack_propagate(False)
        
        # キャンバスフレーム
        self.canvas_frame = tk.Frame(self.content_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        return {
            'main_frame': self.main_frame,
            'content_frame': self.content_frame,
            'sidebar_frame': self.sidebar_frame,
            'content_header_frame': self.content_header_frame,
            'canvas_top_frame': self.canvas_top_frame,
            'canvas_frame': self.canvas_frame
        }
    
    def setup_date_display(self):
        """日付表示エリアをセットアップ"""
        self.date_frame = tk.Frame(self.content_header_frame)
        self.date_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.date_label = tk.Label(
            self.date_frame,
            text=f"日付: {self.selected_date.strftime('%Y年%m月%d日')}",
            font=("Arial", 12)
        )
        self.date_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.date_button = tk.Button(
            self.date_frame,
            text="日付を選択",
            command=self.callbacks.get('select_date'),
            font=("Arial", 10)
        )
        self.date_button.pack(side=tk.LEFT, padx=10, pady=5)
    
    def setup_undo_redo_buttons(self):
        """元に戻す・進むボタンをセットアップ"""
        undo_redo_frame = tk.Frame(self.content_header_frame)
        undo_redo_frame.pack(side=tk.LEFT, padx=15, pady=5)
        
        # 元に戻すボタン
        self.undo_button = tk.Button(
            undo_redo_frame,
            text="↶ 元に戻す",
            command=self.callbacks.get('undo_action'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        # 進むボタン
        self.redo_button = tk.Button(
            undo_redo_frame,
            text="↷ 進む",
            command=self.callbacks.get('redo_action'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.redo_button.pack(side=tk.LEFT, padx=2)
    
    def setup_mode_selection(self):
        """モード選択エリアをセットアップ"""
        mode_frame = tk.Frame(self.content_header_frame)
        mode_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        tk.Label(mode_frame, text="モード:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.edit_radio = tk.Radiobutton(
            mode_frame,
            text="編集",
            variable=self.mode_var,
            value="編集",
            font=("Arial", 10),
            command=self.callbacks.get('on_mode_change')
        )
        self.edit_radio.pack(side=tk.LEFT, padx=5)
        
        self.view_radio = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            font=("Arial", 10),
            command=self.callbacks.get('on_mode_change')
        )
        self.view_radio.pack(side=tk.LEFT, padx=5)
    
    def setup_settings_button(self):
        """設定ボタンをセットアップ"""
        settings_frame = tk.Frame(self.content_header_frame)
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.settings_button = tk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self.callbacks.get('open_settings'),
            font=("Arial", 10),
            relief='raised',
            padx=10
        )
        self.settings_button.pack()
    
    def setup_canvas(self):
        """キャンバスをセットアップ"""
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT
        )
        self.canvas.pack()
        return self.canvas
    
    def update_date_label(self, date):
        """日付ラベルを更新"""
        if self.date_label:
            self.date_label.config(text=f"日付: {date.strftime('%Y年%m月%d日')}")
    
    def get_form_data(self):
        """フォームデータを取得"""
        return {
            'date': self.selected_date,
            'mode': self.mode_var.get(),
            'model': self.model_var.get(),
            'save_name': self.save_name_var.get(),
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get(),
            'comment': self.comment_text.get("1.0", tk.END).strip() if self.comment_text else "",
            'repaired': self.repaired_var.get()
        }
    
    def get_current_lot_number(self):
        """現在保存されているロット番号を取得"""
        return self.current_lot_number
    
    def set_current_lot_number(self, lot_number):
        """ロット番号を設定してラベルを更新"""
        self.current_lot_number = lot_number
        self._update_lot_number_label()
    
    def _update_lot_number_label(self):
        """サイドバーのロット番号ラベルを更新"""
        if hasattr(self, 'lot_number_label') and self.lot_number_label:
            if self.current_lot_number:
                self.lot_number_label.config(text=f"指図番号: {self.current_lot_number}")
            else:
                self.lot_number_label.config(text="指図番号: 未設定")
    
    def get_current_worker(self):
        """現在設定されている作業者Noを取得（JSONファイル保存用）"""
        return self.current_worker_no
    
    def get_current_worker_name(self):
        """現在設定されている作業者名を取得"""
        return self.current_worker_name
    
    def set_current_worker(self, worker_no):
        """作業者Noを設定してラベルを更新"""
        workers = self._load_workers_from_csv()
        if worker_no in workers:
            self.current_worker_no = worker_no
            self.current_worker_name = workers[worker_no]
            self._update_worker_label()
        else:
            print(f"警告: 作業者No '{worker_no}' が見つかりません")
            self.current_worker_no = worker_no
            self.current_worker_name = f"不明({worker_no})"
            self._update_worker_label()
    
    def set_readonly_mode(self, readonly=True):
        """サイドバーの読み取り専用モードを設定 - 基底クラスでは空実装"""
        pass
    
    def reset_sidebar_title_for_viewing(self):
        """閲覧モード用のサイドバータイトルをリセット"""
        # サイドバーのタイトルラベルを検索してリセット
        for child in self.sidebar_frame.winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'config'):
                current_text = child.cget('text')
                if '座標' in current_text and '詳細情報' in current_text:
                    child.config(text="不良詳細情報")
                    break
    
    def _update_worker_label(self):
        """サイドバーの作業者ラベルを更新"""
        if hasattr(self, 'worker_label') and self.worker_label:
            if self.current_worker_name:
                self.worker_label.config(text=f"作業者: {self.current_worker_name}")
            else:
                self.worker_label.config(text="作業者: 未設定")
    
    def _load_workers_from_csv(self):
        """worker.csvから作業者リストを読み込み"""
        try:
            # プロジェクトディレクトリのworker.csvを読み込み
            worker_file = os.path.join(Path(self._get_executable_directory()).parent.as_posix(), "worker.csv")
            
            workers = {}
            if os.path.exists(worker_file):
                with open(worker_file, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        if len(row) >= 2:
                            worker_no = row[0].strip()
                            worker_name = row[1].strip()
                            if worker_no and worker_name:
                                workers[worker_no] = worker_name
                
                return workers
            else:
                print(f"worker.csvが見つかりません: {worker_file}")
                return {}
                
        except Exception as e:
            print(f"worker.csv読み込みエラー: {e}")
            return {}
    
    def show_worker_input_dialog(self):
        """作業者No入力ダイアログを表示"""
        from tkinter import simpledialog, messagebox
        
        # worker.csvを読み込み
        workers = self._load_workers_from_csv()
        
        if not workers:
            messagebox.showerror("エラー", "worker.csvが見つからないか、作業者データがありません。")
            self.root.quit()
            return None
        
        while True:
            worker_no = simpledialog.askstring(
                "作業者設定",
                "作業者Noを入力してください:"
            )
            
            if worker_no is None:
                # キャンセルされた場合はアプリを終了
                response = messagebox.askyesno(
                    "確認",
                    "作業者Noは必須です。\nアプリケーションを終了しますか？"
                )
                if response:
                    self.root.quit()
                    return None
                # いいえの場合は再度入力を求める
                continue
            
            worker_no = worker_no.strip()
            if not worker_no:
                messagebox.showerror("エラー", "作業者Noを入力してください。")
                continue
            
            # 作業者Noから作業者名を取得
            if worker_no in workers:
                worker_name = workers[worker_no]
                self.current_worker_no = worker_no
                self.current_worker_name = worker_name
                self._update_worker_label()
                print(f"作業者を設定しました: No.{self.current_worker_no} - {self.current_worker_name}")
                return worker_no
            else:
                # 存在しない作業者Noの場合
                available_workers = "\n".join([f"{no}: {name}" for no, name in workers.items()])
                messagebox.showerror(
                    "エラー", 
                    f"作業者No '{worker_no}' は存在しません。\n\n利用可能な作業者:\n{available_workers}"
                )
    
    def _load_and_display_image(self):
        """選択されたモデルの画像を読み込んでキャンバスに表示"""
        try:
            # 現在選択されているモデル名を取得
            selected_model = self.model_var.get()
            
            if not selected_model or selected_model.startswith("画像"):
                # モデルが選択されていない、または画像がない場合はキャンバスをクリア
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.delete("all")
                return
            
            # 保存されている辞書データから画像パスを取得
            image_path = None
            if hasattr(self, 'model_data'):
                for item in self.model_data:
                    if selected_model in item:
                        image_path = item[selected_model]
                        break
            
            # 辞書データがない場合は従来の方法で検索
            if not image_path:
                # 設定から画像ディレクトリを取得
                settings = self._load_settings()
                image_directory = settings.get('image_directory', '')
                
                if not image_directory or not os.path.exists(image_directory):
                    return
                
                # 画像ファイルのパスを構築
                # サポートする拡張子を順番に試す
                image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
                
                for ext in image_extensions:
                    potential_path = os.path.join(image_directory, selected_model + ext)
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        break
            
            if not image_path or not os.path.exists(image_path):
                # 画像ファイルが見つからない場合はキャンバスをクリア
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.delete("all")
                return
            
            # 画像を読み込み
            if self.callbacks.get('load_image_for_display'):
                image_data = self.callbacks['load_image_for_display'](image_path)
                
                if not image_data:
                    # 画像読み込みに失敗した場合はキャンバスをクリア
                    if hasattr(self, 'canvas') and self.canvas:
                        self.canvas.delete("all")
                    return
                
                # キャンバスに表示
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.delete("all")
                    
                    # 画像を中央に配置
                    canvas_width = self.CANVAS_WIDTH
                    canvas_height = self.CANVAS_HEIGHT
                    x = (canvas_width - image_data['display_width']) // 2
                    y = (canvas_height - image_data['display_height']) // 2
                    
                    # coordinate_managerで読み込まれたImageTkオブジェクトを使用
                    self.current_image = image_data['tk_image']
                    self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_image)
                    
                    # 画像の表示領域をcoordinate_managerに通知
                    if self.callbacks.get('on_image_loaded'):
                        self.callbacks['on_image_loaded']({
                            'image_path': image_data['image_path'],
                            'display_x': x,
                            'display_y': y,
                            'display_width': image_data['display_width'],
                            'display_height': image_data['display_height'],
                            'original_width': image_data['original_width'],
                            'original_height': image_data['original_height']
                        })
        
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            # エラーが発生した場合はキャンバスをクリア
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.delete("all")
