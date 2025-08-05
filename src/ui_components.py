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
        model_data = self.callbacks.get('load_models_from_file', lambda: [])()
        
        # 辞書リストからファイル名のみを抽出してコンボボックス用のリストを作成
        model_values = [list(item.keys())[0] for item in model_data]
        
        # 辞書データを保持（画像パス取得で使用）
        self.model_data = model_data
        
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
            width=50,  # 幅を広げて長い名前に対応    
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
        # サイドバーのスタイル設定
        self.sidebar_frame.config(bg='#f5f5f5', relief='ridge', bd=1)
        
        # タイトル
        title_label = tk.Label(
            self.sidebar_frame,
            text="不良詳細情報",
            font=("Arial", 14, "bold"),
            bg='#f5f5f5',
            fg='#333333'
        )
        title_label.pack(pady=(15, 20))
        
        # 区切り線
        separator1 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator1.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        # アイテム番号（読み取り専用）
        self.item_number_entry = self._create_styled_input_field(
            "項目番号", self.item_number_var, width=12, readonly=True
        )
        
        # リファレンス
        self.reference_entry = self._create_styled_input_field(
            "リファレンス", self.reference_var, width=15
        )
        
        # 区切り線
        separator2 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator2.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # 不良名
        self._create_defect_selection()
        
        # 修理済み
        self._create_repaired_selection()
        
        # 区切り線
        separator3 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # コメント
        self._create_comment_field()
    
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
        
        return entry  # Entryウィジェットを返す
    
    def _create_styled_input_field(self, label_text, variable, width=15, readonly=False):
        """スタイル付きの入力フィールドを作成"""
        # メインフレーム
        main_frame = tk.Frame(self.sidebar_frame, bg='#f5f5f5')
        main_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            main_frame, 
            text=label_text, 
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # 入力フィールド
        entry_state = "readonly" if readonly else "normal"
        entry_bg = '#f0f0f0' if readonly else 'white'
        
        entry = tk.Entry(
            main_frame, 
            textvariable=variable, 
            width=width,
            font=("Arial", 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#4CAF50',
            bg=entry_bg,
            state=entry_state
        )
        entry.pack(fill=tk.X)
        
        # 読み取り専用でない場合のみ変更検出のイベントをバインド
        if not readonly:
            variable.trace_add('write', self._on_form_data_changed)
        
        return entry
    
    def _create_defect_selection(self):
        """不良名選択フィールドを作成"""
        # メインフレーム
        defect_frame = tk.Frame(self.sidebar_frame, bg='#f5f5f5')
        defect_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            defect_frame, 
            text="不良名", 
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # 外部ファイルから不良名リストを読み込み
        defect_values = self._load_defects_from_file()
        
        self.defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=defect_values,
            state="readonly",
            font=("Arial", 10)
        )
        self.defect_combobox.pack(fill=tk.X)
        self.defect_combobox.current(0)
        
        # 変更検出のイベントをバインド
        self.defect_var.trace_add('write', self._on_form_data_changed)
    
    def _create_comment_field(self):
        """コメントフィールドを作成"""
        # メインフレーム
        comment_frame = tk.Frame(self.sidebar_frame, bg='#f5f5f5')
        comment_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            comment_frame, 
            text="コメント", 
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # テキストフィールドとスクロールバーのフレーム
        text_frame = tk.Frame(comment_frame, bg='#f5f5f5')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # テキストフィールド
        self.comment_text = tk.Text(
            text_frame, 
            height=8, 
            font=("Arial", 9),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#4CAF50',
            bg='white',
            wrap=tk.WORD
        )
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = tk.Scrollbar(text_frame, command=self.comment_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_text.config(yscrollcommand=scrollbar.set)
        
        # コメントフィールドの変更検出
        self.comment_text.bind('<KeyRelease>', self._on_comment_changed)
        self.comment_text.bind('<FocusOut>', self._on_comment_changed)
    
    def _create_repaired_selection(self):
        """修理済み選択フィールドを作成"""
        # メインフレーム
        repaired_frame = tk.Frame(self.sidebar_frame, bg='#f5f5f5')
        repaired_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            repaired_frame, 
            text="修理済み", 
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 5))
        
        # ラジオボタンフレーム
        radio_frame = tk.Frame(repaired_frame, bg='#f5f5f5')
        radio_frame.pack(fill=tk.X)
        
        self.repaired_yes = tk.Radiobutton(
            radio_frame,
            text="はい",
            variable=self.repaired_var,
            value="はい",
            font=("Arial", 10),
        )
        self.repaired_yes.pack(side=tk.LEFT, padx=(10, 20))
        
        self.repaired_no = tk.Radiobutton(
            radio_frame,
            text="いいえ",
            variable=self.repaired_var,
            value="いいえ",
            font=("Arial", 10),
        )
        self.repaired_no.pack(side=tk.LEFT, padx=10)
    
    def update_model_combobox(self):
        """モデル選択リストを更新"""
        if hasattr(self, 'model_combobox'):
            # 新しいモデルデータを取得
            model_data = self.callbacks.get('load_models_from_file', lambda: [])()
            
            # 辞書リストからファイル名のみを抽出
            model_values = [list(item.keys())[0] for item in model_data]
            
            # 辞書データを保持
            self.model_data = model_data
            
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
    
    def focus_reference_entry(self):
        """リファレンス入力フィールドにフォーカスを当てる"""
        if hasattr(self, 'reference_entry') and self.reference_entry:
            self.reference_entry.focus_set()
            self.reference_entry.icursor(tk.END)  # カーソルを末尾に移動
    
    def update_form_with_coordinate_detail(self, detail):
        """座標の詳細情報でフォームを更新"""
        if detail:
            self.item_number_var.set(detail.get('item_number', ''))
            self.reference_var.set(detail.get('reference', ''))
            self.defect_var.set(detail.get('defect', 'ズレ'))
            self.repaired_var.set(detail.get('repaired', 'いいえ'))
            
            # コメントフィールドを更新
            if self.comment_text:
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", detail.get('comment', ''))
    
    def display_coordinate_info_for_viewing(self, detail, coordinate_index):
        """閲覧モード用の座標情報表示（より詳細な情報を含む）"""
        if detail:
            # 基本情報を更新
            self.update_form_with_coordinate_detail(detail)
            
            # 閲覧モード時は座標番号も表示
            coord_num = coordinate_index + 1
            
            # サイドバーのタイトルを更新
            self._update_sidebar_title_for_viewing(coord_num)
            
            print(f"[閲覧モード] 座標 {coord_num} の詳細:")
            print(f"  項目番号: {detail.get('item_number', '未設定')}")
            print(f"  リファレンス: {detail.get('reference', '未設定')}")
            print(f"  不良名: {detail.get('defect', 'ズレ')}")
            print(f"  修理済み: {detail.get('repaired', 'いいえ')}")
            comment = detail.get('comment', '')
            if comment:
                print(f"  コメント: {comment}")
            else:
                print("  コメント: なし")
    
    def _update_sidebar_title_for_viewing(self, coord_num):
        """閲覧モード用のサイドバータイトルを更新"""
        # サイドバーのタイトルラベルを検索して更新
        for child in self.sidebar_frame.winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'config'):
                current_text = child.cget('text')
                if '不良詳細情報' in current_text or '座標' in current_text:
                    child.config(text=f"座標 {coord_num} の詳細情報")
                    break
    
    def display_coordinate_summary_for_viewing(self, summary):
        """閲覧モード用の座標概要情報を表示"""
        if summary:
            total = summary.get('total_count', 0)
            repaired = summary.get('repaired_count', 0)
            unrepaired = summary.get('unrepaired_count', 0)
            defect_counts = summary.get('defect_counts', {})
            
            print(f"[閲覧モード] 座標の概要:")
            print(f"  総座標数: {total}個")
            print(f"  修理済み: {repaired}個")
            print(f"  未修理: {unrepaired}個")
            
            if defect_counts:
                print("  不良種別:")
                for defect, count in defect_counts.items():
                    print(f"    {defect}: {count}個")
    
    def reset_sidebar_title_for_viewing(self):
        """閲覧モード用のサイドバータイトルをリセット"""
        # サイドバーのタイトルラベルを検索してリセット
        for child in self.sidebar_frame.winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'config'):
                current_text = child.cget('text')
                if '座標' in current_text and '詳細情報' in current_text:
                    child.config(text="不良詳細情報")
                    break
    
    def get_current_coordinate_detail(self):
        """現在のフォームから座標詳細情報を取得"""
        return {
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get(),
            'comment': self.comment_text.get("1.0", tk.END).strip() if self.comment_text else "",
            'repaired': self.repaired_var.get()
        }
    
    def clear_form(self):
        """フォームをクリア"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("ズレ")
        self.repaired_var.set("いいえ")
        
        # コメントフィールドをクリア
        if self.comment_text:
            self.comment_text.delete("1.0", tk.END)
    
    def set_readonly_mode(self, readonly=True):
        """サイドバーの読み取り専用モードを設定"""
        state = "readonly" if readonly else "normal"
        
        # 項目番号とリファレンス入力フィールド
        if hasattr(self, 'reference_entry'):
            self.reference_entry.config(state=state)
        
        # 不良名コンボボックス
        if hasattr(self, 'defect_combobox'):
            self.defect_combobox.config(state="disabled" if readonly else "readonly")
        
        # 修理済みラジオボタン
        if hasattr(self, 'repaired_yes'):
            self.repaired_yes.config(state="disabled" if readonly else "normal")
        if hasattr(self, 'repaired_no'):
            self.repaired_no.config(state="disabled" if readonly else "normal")
        
        # コメントテキストフィールド
        if self.comment_text:
            self.comment_text.config(state="disabled" if readonly else "normal")
            
        # 閲覧モード時は背景色を変更して視覚的に分かりやすくする
        if readonly:
            bg_color = '#f0f0f0'  # 薄いグレー
            if hasattr(self, 'reference_entry'):
                self.reference_entry.config(readonlybackground=bg_color)
            if hasattr(self, 'defect_combobox'):
                self.defect_combobox.config(background=bg_color)
            if self.comment_text:
                self.comment_text.config(bg=bg_color)
        else:
            # 編集モード時は通常の背景色に戻す
            bg_color = 'white'
            if hasattr(self, 'reference_entry'):
                self.reference_entry.config(readonlybackground=bg_color)
            if hasattr(self, 'defect_combobox'):
                self.defect_combobox.config(background=bg_color)
            if self.comment_text:
                self.comment_text.config(bg=bg_color)
            
        # 項目番号フィールドは常に読み取り専用
        # (項目番号は自動生成されるため)
    
    def _on_form_data_changed(self, *args):
        """フォームデータが変更された時のイベントハンドラー"""
        if self.callbacks.get('on_form_data_changed'):
            self.callbacks['on_form_data_changed']()
    
    def _on_comment_changed(self, event=None):
        """コメントフィールドが変更された時のイベントハンドラー"""
        if self.callbacks.get('on_form_data_changed'):
            self.callbacks['on_form_data_changed']()
    
    def enable_auto_save(self, enable=True):
        """自動保存機能の有効/無効を切り替え"""
        self._auto_save_enabled = enable
    
    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        self._load_and_display_image()
        
        # 保存ディレクトリをセットアップ
        if self.callbacks.get('setup_json_save_dir'):
            self.callbacks['setup_json_save_dir']()
        
        # 保存名エントリを自動設定
        if self.callbacks.get('setup_save_name_entry'):
            self.callbacks['setup_save_name_entry']()
        
    
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
            else:
                # フォールバック: 従来の方法で画像を読み込み
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
