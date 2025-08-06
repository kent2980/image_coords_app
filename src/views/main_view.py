"""
メインビュー
アプリケーションのメインウィンドウを管理
"""
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any


class MainView:
    """メインビューを管理するクラス"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("画像座標アプリケーション (MVC)")
        self.root.geometry("1400x900")
        
        # メインフレーム
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # レイアウト用フレーム
        self.top_frame = None
        self.content_frame = None
        self.canvas_frame = None
        self.sidebar_frame = None
        
        # UI要素の参照
        self.mode_var = tk.StringVar(value="編集")
        self.date_label = None
        self.undo_button = None
        self.redo_button = None
        self.settings_button = None
        
        # コールバック関数
        self.callbacks: Dict[str, Callable] = {}
        
        self._setup_layout()
    
    def _setup_layout(self):
        """レイアウトを設定"""
        # トップフレーム（ボタン類）
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # コンテンツフレーム（キャンバスとサイドバー）
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # キャンバスフレーム（左側）
        self.canvas_frame = tk.Frame(self.content_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # サイドバーフレーム（右側）
        self.sidebar_frame = tk.Frame(self.content_frame, width=350)
        self.sidebar_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)
    
    def setup_top_controls(self):
        """トップコントロールを設定"""
        # 日付表示とボタン
        date_frame = tk.Frame(self.top_frame)
        date_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 日付ラベル
        self.date_label = tk.Label(date_frame, text="日付: ", font=("Arial", 10))
        self.date_label.pack(side=tk.LEFT, padx=5)
        
        # 日付選択ボタン
        date_select_button = tk.Button(
            date_frame, 
            text="日付選択", 
            command=self.callbacks.get('select_date'),
            font=("Arial", 9)
        )
        date_select_button.pack(side=tk.LEFT, padx=5)
        
        # Undo/Redoボタン
        undo_redo_frame = tk.Frame(self.top_frame)
        undo_redo_frame.pack(side=tk.LEFT, padx=10)
        
        self.undo_button = tk.Button(
            undo_redo_frame, 
            text="元に戻す", 
            command=self.callbacks.get('undo'),
            font=("Arial", 9)
        )
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        self.redo_button = tk.Button(
            undo_redo_frame, 
            text="やり直し", 
            command=self.callbacks.get('redo'),
            font=("Arial", 9)
        )
        self.redo_button.pack(side=tk.LEFT, padx=2)
        
        # 設定ボタン
        self.settings_button = tk.Button(
            self.top_frame, 
            text="設定", 
            command=self.callbacks.get('open_settings'),
            font=("Arial", 9)
        )
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        # モード選択
        mode_frame = tk.Frame(self.top_frame)
        mode_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Label(mode_frame, text="モード:", font=("Arial", 9)).pack(side=tk.LEFT, padx=2)
        
        mode_edit = tk.Radiobutton(
            mode_frame, 
            text="編集", 
            variable=self.mode_var, 
            value="編集",
            command=self.callbacks.get('on_mode_change'),
            font=("Arial", 9)
        )
        mode_edit.pack(side=tk.LEFT, padx=2)
        
        mode_view = tk.Radiobutton(
            mode_frame, 
            text="閲覧", 
            variable=self.mode_var, 
            value="閲覧",
            command=self.callbacks.get('on_mode_change'),
            font=("Arial", 9)
        )
        mode_view.pack(side=tk.LEFT, padx=2)
    
    def setup_menu_buttons(self):
        """メニューボタンを設定"""
        menu_frame = tk.Frame(self.top_frame)
        menu_frame.pack(side=tk.LEFT, padx=5)
        
        # 画像選択ボタン
        select_image_btn = tk.Button(
            menu_frame,
            text="画像を選択",
            command=self.callbacks.get('select_image'),
            font=("Arial", 10)
        )
        select_image_btn.pack(side=tk.LEFT, padx=2)
        
        # JSON読み込みボタン
        load_json_btn = tk.Button(
            menu_frame,
            text="JSONを読み込み",
            command=self.callbacks.get('load_json'),
            font=("Arial", 10)
        )
        load_json_btn.pack(side=tk.LEFT, padx=2)
        
        # 保存ボタン
        save_btn = tk.Button(
            menu_frame,
            text="座標を保存",
            command=self.callbacks.get('save_coordinates'),
            font=("Arial", 10)
        )
        save_btn.pack(side=tk.LEFT, padx=2)
        
        # クリアボタン
        clear_btn = tk.Button(
            menu_frame,
            text="座標をクリア",
            command=self.callbacks.get('clear_coordinates'),
            font=("Arial", 10)
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self.callbacks.update(callbacks)
    
    def update_date_label(self, date_str: str):
        """日付ラベルを更新"""
        if self.date_label:
            self.date_label.config(text=f"日付: {date_str}")
    
    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Undo/Redoボタンの状態を更新"""
        if self.undo_button:
            self.undo_button.config(state=tk.NORMAL if can_undo else tk.DISABLED)
        if self.redo_button:
            self.redo_button.config(state=tk.NORMAL if can_redo else tk.DISABLED)
    
    def get_current_mode(self) -> str:
        """現在のモードを取得"""
        return self.mode_var.get()
    
    def set_mode(self, mode: str):
        """モードを設定"""
        self.mode_var.set(mode)
    
    def show_message(self, message: str, title: str = "情報"):
        """メッセージを表示"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def show_error(self, message: str, title: str = "エラー"):
        """エラーメッセージを表示"""
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    def show_warning(self, message: str, title: str = "警告"):
        """警告メッセージを表示"""
        from tkinter import messagebox
        messagebox.showwarning(title, message)
