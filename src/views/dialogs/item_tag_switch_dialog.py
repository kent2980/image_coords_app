"""
現品票切り替えダイアログ
製番と指図番号を入力して切り替えを行う
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple


class ItemTagSwitchDialog:
    """現品票切り替えダイアログクラス"""
    
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.result = None
        
        # ダイアログウィンドウを作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("現品票で切り替え")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        
        # モーダルにする
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 親ウィンドウの中央に配置
        self._center_window()
        
        # UI要素の変数
        self.product_number_var = tk.StringVar()
        self.lot_number_var = tk.StringVar()
        
        self._setup_ui()
        
        # Escapeキーで閉じる
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # 最初の入力フィールドにフォーカス
        self.dialog.after(100, self._set_initial_focus)
    
    def _setup_ui(self):
        """UIをセットアップ"""
        # メインフレーム
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = tk.Label(
            main_frame,
            text="現品票情報を入力してください",
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # 入力エリアフレーム
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 製番入力
        product_frame = tk.Frame(input_frame)
        product_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            product_frame,
            text="製番:",
            font=("Arial", 10),
            width=8,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.product_number_entry = tk.Entry(
            product_frame,
            textvariable=self.product_number_var,
            font=("Arial", 10),
            width=25
        )
        self.product_number_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Enterキーで次のフィールドに移動
        self.product_number_entry.bind('<Return>', self._on_product_enter)
        
        # 指図入力
        lot_frame = tk.Frame(input_frame)
        lot_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            lot_frame,
            text="指図:",
            font=("Arial", 10),
            width=8,
            anchor="w"
        ).pack(side=tk.LEFT)
        
        self.lot_number_entry = tk.Entry(
            lot_frame,
            textvariable=self.lot_number_var,
            font=("Arial", 10),
            width=25
        )
        self.lot_number_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Enterキーで確定
        self.lot_number_entry.bind('<Return>', self._on_ok)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            font=("Arial", 10),
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # OKボタン
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            font=("Arial", 10),
            width=10,
            default=tk.ACTIVE
        )
        ok_button.pack(side=tk.RIGHT)
    
    def _center_window(self):
        """ウィンドウを親の中央に配置"""
        self.dialog.update_idletasks()
        
        # 親ウィンドウの位置とサイズを取得
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # ダイアログのサイズを取得
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 中央に配置する座標を計算
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def _set_initial_focus(self):
        """初期フォーカスを設定"""
        self.product_number_entry.focus_set()
        self.product_number_entry.icursor(tk.END)
    
    def _on_product_enter(self, event=None):
        """製番入力でEnterキーが押された時の処理"""
        self.lot_number_entry.focus_set()
    
    def _on_ok(self, event=None):
        """OKボタンが押された時の処理"""
        product_number = self.product_number_var.get().strip()
        lot_number = self.lot_number_var.get().strip()
        
        # 入力チェック
        if not product_number:
            messagebox.showwarning("入力エラー", "製番を入力してください。", parent=self.dialog)
            self.product_number_entry.focus_set()
            return
        
        if not lot_number:
            messagebox.showwarning("入力エラー", "指図を入力してください。", parent=self.dialog)
            self.lot_number_entry.focus_set()
            return
        
        # 結果を設定
        self.result = (product_number, lot_number)
        self.dialog.destroy()
    
    def _on_cancel(self, event=None):
        """キャンセルボタンが押された時の処理"""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[Tuple[str, str]]:
        """ダイアログを表示して結果を返す
        
        Returns:
            Optional[Tuple[str, str]]: (製番, 指図) のタプル。キャンセル時はNone
        """
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
        return self.result


def show_item_tag_switch_dialog(parent: tk.Tk) -> Optional[Tuple[str, str]]:
    """現品票切り替えダイアログを表示する便利関数
    
    Args:
        parent: 親ウィンドウ
    
    Returns:
        Optional[Tuple[str, str]]: (製番, 指図) のタプル。キャンセル時はNone
    """
    dialog = ItemTagSwitchDialog(parent)
    return dialog.show()
