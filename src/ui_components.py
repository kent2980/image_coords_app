"""
UI Components Module
UIデザインとレイアウトを担当するモジュール
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


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
        self.sidebar_frame = tk.Frame(self.content_frame, width=self.SIDEBAR_WIDTH, bg='lightgray')
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
            bg='lightcyan',
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
            bg='lightcyan',
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
            bg='lightblue',
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
        
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["YOLOv8", "YOLOv5", "Faster R-CNN", "SSD", "Custom Model"],
            state="readonly",
            width=15
        )
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        self.model_combobox.current(0)
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.save_name_entry = tk.Entry(
            save_frame,
            textvariable=self.save_name_var,
            width=20
        )
        self.save_name_entry.pack(side=tk.LEFT, padx=5)
    
    def setup_canvas(self):
        """キャンバスをセットアップ"""
        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg='white'
        )
        self.canvas.pack()
        return self.canvas
    
    def setup_sidebar(self):
        """サイドバーをセットアップ"""
        # タイトル
        title_label = tk.Label(
            self.sidebar_frame,
            text="詳細情報",
            font=("Arial", 14, "bold"),
            bg='lightgray'
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
        frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        content_frame = tk.Frame(frame, bg='lightgray')
        content_frame.pack(expand=True)
        
        label = tk.Label(content_frame, text=label_text, font=("Arial", 10), bg='lightgray')
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(content_frame, textvariable=variable, width=width)
        entry.pack(side=tk.LEFT, padx=5)
    
    def _create_defect_selection(self):
        """不良名選択フィールドを作成"""
        defect_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        defect_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(defect_frame, text="不良名:", font=("Arial", 10), bg='lightgray').pack(side=tk.LEFT)
        
        self.defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=["ズレ", "裏", "飛び"],
            state="readonly",
            width=15
        )
        self.defect_combobox.pack(side=tk.LEFT, padx=5)
        self.defect_combobox.current(0)
    
    def _create_comment_field(self):
        """コメントフィールドを作成"""
        comment_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        comment_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(comment_frame, text="コメント:", font=("Arial", 10), bg='lightgray').pack(anchor='w')
        
        self.comment_text = tk.Text(comment_frame, height=12, width=30, font=("Arial", 9))
        self.comment_text.pack(fill=tk.X, pady=(2, 0))
    
    def _create_repaired_selection(self):
        """修理済み選択フィールドを作成"""
        repaired_frame = tk.Frame(self.sidebar_frame, bg='lightgray')
        repaired_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(repaired_frame, text="修理済み:", font=("Arial", 10), bg='lightgray').pack(side=tk.LEFT)
        
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
