"""
Sidebar View
サイドバー詳細情報ビュー
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Callable, Optional, List


class SidebarView:
    """サイドバービュークラス"""
    
    def __init__(self, parent_frame: tk.Frame, mode: str = "編集"):
        self.parent_frame = parent_frame
        self.mode = mode
        
        # UI変数
        self.item_number_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.defect_var = tk.StringVar()
        self.repaired_var = tk.StringVar(value="いいえ")
        
        # UI要素
        self.worker_label: Optional[tk.Label] = None
        self.lot_number_label: Optional[tk.Label] = None
        self.item_number_entry: Optional[tk.Entry] = None
        self.reference_entry: Optional[tk.Entry] = None
        self.defect_combobox: Optional[ttk.Combobox] = None
        self.comment_text: Optional[tk.Text] = None
        self.repaired_yes: Optional[tk.Radiobutton] = None
        self.repaired_no: Optional[tk.Radiobutton] = None
        
        # コールバック関数
        self._callbacks: Dict[str, Callable] = {}
        
        # 不良名リスト
        self._defect_list: List[str] = ["ズレ", "裏", "飛び"]
        
        # セットアップ
        self._setup_sidebar()
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self._callbacks.update(callbacks)
    
    def set_defect_list(self, defect_list: List[str]):
        """不良名リストを設定"""
        self._defect_list = defect_list
        if self.defect_combobox:
            self.defect_combobox['values'] = defect_list
    
    def _setup_sidebar(self):
        """サイドバーをセットアップ"""
        # サイドバーのスタイル設定
        bg_color = '#f0f8ff' if self.mode == "閲覧" else '#f5f5f5'
        self.parent_frame.config(bg=bg_color, relief='ridge', bd=1)
        
        # タイトル
        title_label = tk.Label(
            self.parent_frame,
            text="不良詳細情報",
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg='#333333'
        )
        title_label.pack(pady=(15, 20))
        
        # 区切り線
        self._create_separator()
        
        # 作業者ラベル
        self.worker_label = tk.Label(
            self.parent_frame,
            text="作業者: 未設定",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        self.worker_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        self._create_separator()
        
        # ロット番号ラベル
        self.lot_number_label = tk.Label(
            self.parent_frame,
            text="指図番号: 未設定",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        self.lot_number_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        self._create_separator()
        
        # アイテム番号（常に読み取り専用）
        self.item_number_entry = self._create_styled_input_field(
            "項目番号", self.item_number_var, width=12, readonly=True
        )
        
        # リファレンス
        readonly = (self.mode == "閲覧")
        self.reference_entry = self._create_styled_input_field(
            "リファレンス", self.reference_var, width=15, readonly=readonly
        )
        
        self._create_separator()
        
        # 不良名
        self._create_defect_field()
        
        # 修理済み
        self._create_repaired_field()
        
        self._create_separator()
        
        # コメント
        self._create_comment_field()
    
    def _create_separator(self):
        """区切り線を作成"""
        separator = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator.pack(fill=tk.X, padx=15, pady=(15, 10))
    
    def _create_styled_input_field(self, label_text: str, variable: tk.StringVar, 
                                 width: int = 15, readonly: bool = False) -> tk.Entry:
        """スタイル付きの入力フィールドを作成"""
        bg_color = '#f0f8ff' if self.mode == "閲覧" else '#f5f5f5'
        
        # メインフレーム
        main_frame = tk.Frame(self.parent_frame, bg=bg_color)
        main_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            main_frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # 入力フィールド
        entry_state = "readonly" if readonly else "normal"
        entry_bg = '#e8f4f8' if self.mode == "閲覧" else ('#f0f0f0' if readonly else 'white')
        
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
        
        # 変更検出のイベントをバインド（読み取り専用でない場合のみ）
        if not readonly and self.mode == "編集":
            variable.trace_add('write', self._on_form_data_changed)
        
        return entry
    
    def _create_defect_field(self):
        """不良名選択フィールドを作成"""
        bg_color = '#f0f8ff' if self.mode == "閲覧" else '#f5f5f5'
        
        # メインフレーム
        defect_frame = tk.Frame(self.parent_frame, bg=bg_color)
        defect_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            defect_frame,
            text="不良名",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # コンボボックス
        state = "disabled" if self.mode == "閲覧" else "readonly"
        combobox_bg = '#e8f4f8' if self.mode == "閲覧" else 'white'
        
        self.defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=self._defect_list,
            state=state,
            font=("Arial", 10)
        )
        self.defect_combobox.pack(fill=tk.X)
        
        # 初期値は空に設定
        self.defect_var.set("")
        
        # 変更検出のイベントをバインド（編集モードのみ）
        if self.mode == "編集":
            self.defect_var.trace_add('write', self._on_form_data_changed)
    
    def _create_repaired_field(self):
        """修理済み選択フィールドを作成"""
        bg_color = '#f0f8ff' if self.mode == "閲覧" else '#f5f5f5'
        
        # メインフレーム
        repaired_frame = tk.Frame(self.parent_frame, bg=bg_color)
        repaired_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            repaired_frame,
            text="修理済み",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 5))
        
        # ラジオボタンフレーム
        radio_frame = tk.Frame(repaired_frame, bg=bg_color)
        radio_frame.pack(fill=tk.X)
        
        state = "disabled" if self.mode == "閲覧" else "normal"
        
        self.repaired_yes = tk.Radiobutton(
            radio_frame,
            text="はい",
            variable=self.repaired_var,
            value="はい",
            font=("Arial", 10),
            bg=bg_color,
            state=state
        )
        self.repaired_yes.pack(side=tk.LEFT, padx=(10, 20))
        
        self.repaired_no = tk.Radiobutton(
            radio_frame,
            text="いいえ",
            variable=self.repaired_var,
            value="いいえ",
            font=("Arial", 10),
            bg=bg_color,
            state=state
        )
        self.repaired_no.pack(side=tk.LEFT, padx=10)
        
        # 変更検出（編集モードのみ）
        if self.mode == "編集":
            self.repaired_var.trace_add('write', self._on_form_data_changed)
    
    def _create_comment_field(self):
        """コメントフィールドを作成"""
        bg_color = '#f0f8ff' if self.mode == "閲覧" else '#f5f5f5'
        
        # メインフレーム
        comment_frame = tk.Frame(self.parent_frame, bg=bg_color)
        comment_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            comment_frame,
            text="コメント",
            font=("Arial", 10, "bold"),
            bg=bg_color,
            fg='#555555',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # テキストフィールドとスクロールバーのフレーム
        text_frame = tk.Frame(comment_frame, bg=bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # テキストフィールド
        text_state = "disabled" if self.mode == "閲覧" else "normal"
        text_bg = '#e8f4f8' if self.mode == "閲覧" else 'white'
        
        self.comment_text = tk.Text(
            text_frame,
            height=8,
            font=("Arial", 9),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#4CAF50',
            bg=text_bg,
            wrap=tk.WORD,
            state=text_state
        )
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = tk.Scrollbar(text_frame, command=self.comment_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_text.config(yscrollcommand=scrollbar.set)
        
        # コメントフィールドの変更検出（編集モードのみ）
        if self.mode == "編集":
            self.comment_text.bind('<KeyRelease>', self._on_comment_changed)
            self.comment_text.bind('<FocusOut>', self._on_comment_changed)
    
    def _on_form_data_changed(self, *args):
        """フォームデータが変更された時のイベントハンドラー"""
        callback = self._callbacks.get('on_form_data_changed')
        if callback:
            callback()
    
    def _on_comment_changed(self, event=None):
        """コメントフィールドが変更された時のイベントハンドラー"""
        callback = self._callbacks.get('on_form_data_changed')
        if callback:
            callback()
    
    def update_worker_label(self, worker_name: str):
        """作業者ラベルを更新"""
        if self.worker_label:
            if worker_name:
                self.worker_label.config(text=f"作業者: {worker_name}")
            else:
                self.worker_label.config(text="作業者: 未設定")
    
    def update_lot_number_label(self, lot_number: str):
        """ロット番号ラベルを更新"""
        if self.lot_number_label:
            if lot_number:
                self.lot_number_label.config(text=f"指図番号: {lot_number}")
            else:
                self.lot_number_label.config(text="指図番号: 未設定")
    
    def get_form_data(self) -> Dict[str, Any]:
        """フォームデータを取得"""
        comment_text = ""
        if self.comment_text:
            comment_text = self.comment_text.get("1.0", tk.END).strip()
        
        return {
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get(),
            'comment': comment_text,
            'repaired': self.repaired_var.get()
        }
    
    def set_form_data(self, data: Dict[str, Any]):
        """フォームデータを設定"""
        if 'item_number' in data:
            self.item_number_var.set(data['item_number'])
        if 'reference' in data:
            self.reference_var.set(data['reference'])
        if 'defect' in data:
            self.defect_var.set(data['defect'])
        if 'repaired' in data:
            self.repaired_var.set(data['repaired'])
        if 'comment' in data and self.comment_text:
            if self.mode == "閲覧":
                self.comment_text.config(state="normal")
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", data['comment'])
                self.comment_text.config(state="disabled")
            else:
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", data['comment'])
    
    def clear_form(self):
        """フォームをクリア"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("")
        self.repaired_var.set("いいえ")
        
        if self.comment_text:
            if self.mode == "閲覧":
                self.comment_text.config(state="normal")
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.config(state="disabled")
            else:
                self.comment_text.delete("1.0", tk.END)
    
    def focus_reference_entry(self):
        """リファレンス入力フィールドにフォーカスを当てる"""
        if self.reference_entry and self.mode == "編集":
            self.reference_entry.focus_set()
            self.reference_entry.icursor(tk.END)
    
    def update_sidebar_title(self, title: str):
        """サイドバータイトルを更新"""
        # サイドバーのタイトルラベルを検索して更新
        for child in self.parent_frame.winfo_children():
            if isinstance(child, tk.Label) and hasattr(child, 'config'):
                current_text = child.cget('text')
                if '不良詳細情報' in current_text or '座標' in current_text:
                    child.config(text=title)
                    break
