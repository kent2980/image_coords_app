"""
UI Components Module
UIデザインとレイアウトを担当するモジュール
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import sys
import configparser
from PIL import Image, ImageTk


class UIComponents:
    """UIコンポーネントを管理するクラス"""
    
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
        
        # UI要素の参照を保持
        self.date_label = None
        self.canvas = None
        self.comment_text = None
        
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
    
    def _get_image_files_from_directory(self, directory):
        """指定されたディレクトリから画像ファイル名を取得"""
        if not directory or not os.path.exists(directory):
            return []
        
        # サポートする画像拡張子
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        
        try:
            image_files = []
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    # 拡張子を取得して小文字に変換
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in image_extensions:
                        # 拡張子を除いたファイル名を追加
                        name_without_ext = os.path.splitext(filename)[0]
                        image_files.append(name_without_ext)
            
            # ファイル名をソート
            return sorted(image_files)
            
        except Exception as e:
            print(f"画像ファイル読み込みエラー: {e}")
            return []
    
    def _load_models_from_file(self):
        """設定で指定された画像ディレクトリから画像ファイル名を読み込み"""
        try:
            # 設定ファイルから画像ディレクトリを取得
            settings = self._load_settings()
            image_directory = settings.get('image_directory', '')
            
            if image_directory and image_directory != "未選択":
                # 画像ディレクトリから画像ファイル名を取得
                image_files = self._get_image_files_from_directory(image_directory)
                
                if image_files:
                    return image_files
                else:
                    # 画像ファイルが見つからない場合はディレクトリ名を表示
                    return [f"画像なし（{os.path.basename(image_directory)}）"]
            else:
                # 画像ディレクトリが設定されていない場合
                return ["画像ディレクトリが未設定"]
                
        except Exception as e:
            # エラーが発生した場合はデフォルト値を返す
            print(f"画像ファイル読み込みエラー: {e}")
            return ["設定エラー"]
    
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
        mode_frame.pack(side=tk.RIGHT, padx=5, pady=5)  # paddingを調整
        
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
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=5)  # paddingを調整
        
        self.settings_button = tk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self.callbacks.get('open_settings'),
            font=("Arial", 10),
            relief='raised',
            padx=10
        )
        self.settings_button.pack()
    
    def setup_canvas_top(self):
        """キャンバス上段エリアをセットアップ"""
        # モデル選択フレーム
        model_frame = tk.Frame(self.canvas_top_frame)
        model_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(model_frame, text="モデル:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 設定で指定された画像ディレクトリから画像ファイル名を読み込み
        model_values = self._load_models_from_file()
        
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=model_values,
            state="readonly",
            width=50  # 画像ファイル名が長い場合があるので幅を広げる
        )
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        # モデル選択時のイベントをバインド
        self.model_combobox.bind('<<ComboboxSelected>>', self._on_model_selected)
        if model_values:
            self.model_combobox.current(0)
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.save_name_entry = tk.Entry(
            save_frame,
            textvariable=self.save_name_var,
            width=50  # 幅を広げて長い名前に対応
        )
        self.save_name_entry.pack(side=tk.LEFT, padx=5)
    
    def setup_canvas(self):
        """キャンバスをセットアップ"""
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT
        )
        self.canvas.pack()
        return self.canvas
    
    def setup_sidebar(self):
        """サイドバーをセットアップ"""
        # タイトル
        title_label = tk.Label(
            self.sidebar_frame,
            text="詳細情報",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # アイテム番号
        self._create_centered_input_field(
            "番号", self.item_number_var, width=10
        )
        
        # リファレンス
        self._create_centered_input_field(
            "Rf", self.reference_var, width=15
        )
        
        # 不良名
        self._create_defect_selection()
        
        # コメント
        self._create_comment_field()
        
        # 修理済み
        self._create_repaired_selection()
    
    def _create_centered_input_field(self, label_text, variable, width=15):
        """中央寄せの入力フィールドを作成"""
        frame = tk.Frame(self.sidebar_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        content_frame = tk.Frame(frame)
        content_frame.pack(expand=True)
        
        label = tk.Label(content_frame, text=label_text, font=("Arial", 10))
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(content_frame, textvariable=variable, width=width)
        entry.pack(side=tk.LEFT, padx=5)
    
    def _create_defect_selection(self):
        """不良名選択フィールドを作成"""
        defect_frame = tk.Frame(self.sidebar_frame)
        defect_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(defect_frame, text="不良名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 外部ファイルから不良名リストを読み込み
        defect_values = self._load_defects_from_file()
        
        self.defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=defect_values,
            state="readonly",
            width=15
        )
        self.defect_combobox.pack(side=tk.LEFT, padx=5)
        self.defect_combobox.current(0)
    
    def _create_comment_field(self):
        """コメントフィールドを作成"""
        comment_frame = tk.Frame(self.sidebar_frame)
        comment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(comment_frame, text="コメント:", font=("Arial", 10)).pack(anchor='w')
        
        self.comment_text = tk.Text(comment_frame, height=12, width=30, font=("Arial", 9))
        self.comment_text.pack(fill=tk.X, pady=(2, 0))
    
    def _create_repaired_selection(self):
        """修理済み選択フィールドを作成"""
        repaired_frame = tk.Frame(self.sidebar_frame)
        repaired_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(repaired_frame, text="修理済み:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.repaired_yes = tk.Radiobutton(
            repaired_frame,
            text="はい",
            variable=self.repaired_var,
            value="はい",
            font=("Arial", 10)
        )
        self.repaired_yes.pack(side=tk.LEFT, padx=5)
        
        self.repaired_no = tk.Radiobutton(
            repaired_frame,
            text="いいえ",
            variable=self.repaired_var,
            value="いいえ",
            font=("Arial", 10)
        )
        self.repaired_no.pack(side=tk.LEFT, padx=5)
    
    def update_model_combobox(self):
        """モデル選択リストを更新"""
        if hasattr(self, 'model_combobox'):
            # 新しいモデルリストを取得
            model_values = self._load_models_from_file()
            
            # コンボボックスの値を更新
            self.model_combobox['values'] = model_values
            
            # 現在の選択値が新しいリストに存在するかチェック
            current_value = self.model_var.get()
            if current_value not in model_values and model_values:
                # 存在しない場合は最初の項目を選択
                self.model_combobox.current(0)
            
            # 画像を更新
            self._load_and_display_image()
    
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
    
    def set_form_data(self, data):
        """フォームデータを設定"""
        if 'date' in data:
            self.selected_date = data['date']
            self.update_date_label(self.selected_date)
        if 'mode' in data:
            self.mode_var.set(data['mode'])
        if 'model' in data:
            self.model_var.set(data['model'])
        if 'save_name' in data:
            self.save_name_var.set(data['save_name'])
        if 'item_number' in data:
            self.item_number_var.set(data['item_number'])
        if 'reference' in data:
            self.reference_var.set(data['reference'])
        if 'defect' in data:
            self.defect_var.set(data['defect'])
        if 'comment' in data and self.comment_text:
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert("1.0", data['comment'])
        if 'repaired' in data:
            self.repaired_var.set(data['repaired'])
    
    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        self._load_and_display_image()
    
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
            
            # 設定から画像ディレクトリを取得
            settings = self._load_settings()
            image_directory = settings.get('image_directory', '')
            
            if not image_directory or not os.path.exists(image_directory):
                return
            
            # 画像ファイルのパスを構築
            # サポートする拡張子を順番に試す
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']
            image_path = None
            
            for ext in image_extensions:
                potential_path = os.path.join(image_directory, selected_model + ext)
                if os.path.exists(potential_path):
                    image_path = potential_path
                    break
            
            if not image_path:
                # 画像ファイルが見つからない場合はキャンバスをクリア
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.delete("all")
                return
            
            # 画像を読み込み
            with Image.open(image_path) as pil_image:
                # キャンバスサイズに合わせて画像をリサイズ（アスペクト比を保持）
                canvas_width = self.CANVAS_WIDTH
                canvas_height = self.CANVAS_HEIGHT
                
                # 元の画像サイズ
                orig_width, orig_height = pil_image.size
                
                # アスペクト比を計算
                aspect_ratio = orig_width / orig_height
                
                # キャンバスに収まるサイズを計算
                if aspect_ratio > canvas_width / canvas_height:
                    # 横長の画像
                    new_width = canvas_width
                    new_height = int(canvas_width / aspect_ratio)
                else:
                    # 縦長の画像
                    new_height = canvas_height
                    new_width = int(canvas_height * aspect_ratio)
                
                # 画像をリサイズ
                resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # PhotoImageに変換
                self.current_image = ImageTk.PhotoImage(resized_image)
                
                # キャンバスに表示
                if hasattr(self, 'canvas') and self.canvas:
                    self.canvas.delete("all")
                    
                    # 画像を中央に配置
                    x = (canvas_width - new_width) // 2
                    y = (canvas_height - new_height) // 2
                    
                    self.canvas.create_image(x, y, anchor=tk.NW, image=self.current_image)
                    
                    # 画像の表示領域をcoordinate_managerに通知
                    if self.callbacks.get('on_image_loaded'):
                        self.callbacks['on_image_loaded']({
                            'image_path': image_path,
                            'display_x': x,
                            'display_y': y,
                            'display_width': new_width,
                            'display_height': new_height,
                            'original_width': orig_width,
                            'original_height': orig_height
                        })
        
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            # エラーが発生した場合はキャンバスをクリア
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.delete("all")
