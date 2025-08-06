"""
Main View
メインビューインターフェース
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, Optional
from datetime import datetime


class MainView:
    """メインビュークラス"""
    
    # 定数
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 600
    SIDEBAR_WIDTH = 300
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Coordinate App")
        
        # UI要素への参照
        self.main_frame: Optional[tk.Frame] = None
        self.content_frame: Optional[tk.Frame] = None
        self.sidebar_frame: Optional[tk.Frame] = None
        self.content_header_frame: Optional[tk.Frame] = None
        self.canvas_top_frame: Optional[tk.Frame] = None
        self.canvas_frame: Optional[tk.Frame] = None
        
        # フレーム要素
        self.date_label: Optional[tk.Label] = None
        self.date_button: Optional[tk.Button] = None
        self.undo_button: Optional[tk.Button] = None
        self.redo_button: Optional[tk.Button] = None
        self.settings_button: Optional[tk.Button] = None
        
        # モード選択
        self.mode_var = tk.StringVar(value="編集")
        self.edit_radio: Optional[tk.Radiobutton] = None
        self.view_radio: Optional[tk.Radiobutton] = None
        
        # モデル選択
        self.model_var = tk.StringVar()
        self.model_combobox: Optional[ttk.Combobox] = None
        self.model_data: list = []
        
        # 保存名とロット番号
        self.save_name_var = tk.StringVar()
        self.save_name_entry: Optional[tk.Entry] = None
        self.lot_number_var = tk.StringVar()
        self.lot_number_entry: Optional[tk.Entry] = None
        self.save_button: Optional[tk.Button] = None
        self.search_button: Optional[tk.Button] = None
        
        # 日付管理
        self.selected_date = datetime.now().date()
        
        # コールバック関数辞書
        self._callbacks: Dict[str, Callable] = {}
        
        # 初期セットアップ
        self._setup_main_layout()
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self._callbacks.update(callbacks)
    
    def _setup_main_layout(self):
        """メインレイアウトをセットアップ"""
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
    
    def setup_date_display(self):
        """日付表示エリアをセットアップ"""
        date_frame = tk.Frame(self.content_header_frame)
        date_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.date_label = tk.Label(
            date_frame,
            text=f"日付: {self.selected_date.strftime('%Y年%m月%d日')}",
            font=("Arial", 12)
        )
        self.date_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.date_button = tk.Button(
            date_frame,
            text="日付を選択",
            command=self._callbacks.get('select_date'),
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
            command=self._callbacks.get('undo_action'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        # 進むボタン
        self.redo_button = tk.Button(
            undo_redo_frame,
            text="↷ 進む",
            command=self._callbacks.get('redo_action'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.redo_button.pack(side=tk.LEFT, padx=2)
    
    def setup_settings_button(self):
        """設定ボタンをセットアップ"""
        settings_frame = tk.Frame(self.content_header_frame)
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.settings_button = tk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self._callbacks.get('open_settings'),
            font=("Arial", 10),
            relief='raised',
            padx=10
        )
        self.settings_button.pack()
    
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
            command=self._callbacks.get('on_mode_change')
        )
        self.edit_radio.pack(side=tk.LEFT, padx=5)
        
        self.view_radio = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            font=("Arial", 10),
            command=self._callbacks.get('on_mode_change')
        )
        self.view_radio.pack(side=tk.LEFT, padx=5)
    
    def setup_canvas_top(self):
        """キャンバス上段エリアをセットアップ"""
        # グリッドレイアウトの設定
        self.canvas_top_frame.grid_columnconfigure(0, weight=0)  # モデル選択
        self.canvas_top_frame.grid_columnconfigure(1, weight=1)  # 保存名（拡張可能）
        self.canvas_top_frame.grid_rowconfigure(0, weight=1)
        self.canvas_top_frame.grid_rowconfigure(1, weight=1)  # ロット番号用の行
        
        # モデル選択フレーム
        model_frame = tk.Frame(self.canvas_top_frame)
        model_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        tk.Label(model_frame, text="モデル:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=[],
            state="readonly",
            width=50
        )
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        self.model_combobox.bind('<<ComboboxSelected>>', self._callbacks.get('on_model_selected'))
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.save_name_entry = tk.Entry(
            save_frame,
            textvariable=self.save_name_var,
            width=50
        )
        self.save_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # ロット番号入力エリア
        lot_frame = tk.Frame(self.canvas_top_frame)
        lot_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w", columnspan=2)
        
        tk.Label(lot_frame, text="指図:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.lot_number_entry = tk.Entry(
            lot_frame,
            textvariable=self.lot_number_var,
            width=20
        )
        self.lot_number_entry.pack(side=tk.LEFT, padx=5)
        self.lot_number_entry.bind('<Return>', self._callbacks.get('on_lot_number_enter'))
        
        # 保存ボタン
        self.save_button = tk.Button(
            lot_frame,
            text="保存",
            command=self._callbacks.get('on_save_button_click'),
            font=("Arial", 10),
            relief='raised',
            padx=15
        )
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # 検索ボタン
        self.search_button = tk.Button(
            lot_frame,
            text="検索",
            command=self._callbacks.get('search_coordinates'),
            font=("Arial", 10),
            relief='raised',
            padx=15
        )
        # 初期状態では検索ボタンは非表示
    
    def update_date_label(self, date):
        """日付ラベルを更新"""
        self.selected_date = date
        if self.date_label:
            self.date_label.config(text=f"日付: {date.strftime('%Y年%m月%d日')}")
    
    def update_model_combobox(self, model_data: list):
        """モデル選択リストを更新"""
        self.model_data = model_data
        if self.model_combobox:
            # 辞書リストからファイル名のみを抽出
            model_values = [list(item.keys())[0] for item in model_data]
            self.model_combobox['values'] = model_values
            
            # 現在の選択値が新しいリストに存在するかチェック
            current_value = self.model_var.get()
            if current_value not in model_values and model_values:
                self.model_combobox.current(0)
    
    def set_mode(self, mode: str):
        """モードを設定"""
        self.mode_var.set(mode)
        self._update_button_visibility(mode == "閲覧")
    
    def _update_button_visibility(self, readonly_mode: bool):
        """モードに応じてボタンの表示・非表示を切り替え"""
        if readonly_mode:
            # 閲覧モード: 保存ボタンを非表示、検索ボタンを表示
            if self.save_button:
                self.save_button.pack_forget()
            if self.search_button:
                self.search_button.pack(side=tk.LEFT, padx=10)
        else:
            # 編集モード: 保存ボタンを表示、検索ボタンを非表示
            if self.search_button:
                self.search_button.pack_forget()
            if self.save_button:
                self.save_button.pack(side=tk.LEFT, padx=10)
    
    def get_canvas_frame(self) -> tk.Frame:
        """キャンバスフレームを取得"""
        return self.canvas_frame
    
    def get_sidebar_frame(self) -> tk.Frame:
        """サイドバーフレームを取得"""
        return self.sidebar_frame
    
    def get_form_data(self) -> Dict[str, Any]:
        """フォームデータを取得"""
        return {
            'date': self.selected_date,
            'mode': self.mode_var.get(),
            'model': self.model_var.get(),
            'save_name': self.save_name_var.get(),
            'lot_number': self.lot_number_var.get()
        }
    
    def set_form_data(self, data: Dict[str, Any]):
        """フォームデータを設定"""
        if 'date' in data:
            self.update_date_label(data['date'])
        if 'mode' in data:
            self.set_mode(data['mode'])
        if 'model' in data:
            self.model_var.set(data['model'])
        if 'save_name' in data:
            self.save_name_var.set(data['save_name'])
        if 'lot_number' in data:
            self.lot_number_var.set(data['lot_number'])
    
    def clear_lot_number_input(self):
        """ロット番号入力フィールドをクリア"""
        self.lot_number_var.set("")
    
    def get_current_lot_number(self) -> str:
        """現在のロット番号を取得"""
        return self.lot_number_var.get().strip()
    
    def set_lot_number(self, lot_number: str):
        """ロット番号を設定"""
        self.lot_number_var.set(lot_number)
