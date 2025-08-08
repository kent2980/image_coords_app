"""
サイドバービュー
座標詳細情報の表示と編集を管理
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List


class SidebarView:
    """サイドバーを管理するビュー"""
    
    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        
        # 変数
        self.item_number_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.defect_var = tk.StringVar()
        
        # ロット番号（表示用）
        self.current_lot_number = ""
        
        # 製番（表示用）
        self.current_product_number = ""
        
        # 作業者番号（表示用）
        self.current_worker_no = ""
        
        # UI要素の参照
        self.item_entry = None
        self.reference_entry = None
        self.defect_combobox = None
        self.comment_text = None
        self.worker_label = None
        self.lot_label = None
        self.product_label = None
        
        # コールバック関数
        self.callbacks: Dict[str, Callable] = {}
        
        # 不良項目リスト（デフォルト）
        self.defect_items = [
            "ズレ", "裏", "飛び", "傷", "汚れ", "欠け", 
            "変色", "寸法不良", "形状不良", "その他"
        ]
        
        # 読み取り専用モード
        self.readonly_mode = False
        
        self._setup_sidebar()
    
    def _setup_sidebar(self):
        """サイドバーUIを設定"""
        # サイドバーのスタイル設定（旧コードと一致）
        self.parent_frame.config(bg='#f5f5f5', relief='ridge', bd=1)
        
        # タイトル
        title_label = tk.Label(
            self.parent_frame,
            text="不良詳細情報",
            font=("Arial", 14, "bold"),
            bg='#f5f5f5',
            fg='#333333'
        )
        title_label.pack(pady=(15, 20))

        # 区切り線
        separator5 = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator5.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 作業者ラベル
        self.worker_label = tk.Label(
            self.parent_frame,
            text="作業者: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        self.worker_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        # 区切り線
        separator1 = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator1.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 製番ラベル
        self.product_label = tk.Label(
            self.parent_frame,
            text="製番: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        self.product_label.pack(fill=tk.X, padx=15, pady=(0, 5))

        # ロット番号ラベル
        self.lot_label = tk.Label(
            self.parent_frame,
            text="指図番号: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
            anchor='w'
        )
        self.lot_label.pack(fill=tk.X, padx=15, pady=(0, 5))

        # 区切り線
        separator4 = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator4.pack(fill=tk.X, padx=15, pady=(0, 15))

        # アイテム番号（読み取り専用）
        self.item_entry = self._create_styled_input_field(
            "項目番号", self.item_number_var, width=12, readonly=True
        )
        
        # リファレンス
        self.reference_entry = self._create_styled_input_field(
            "リファレンス", self.reference_var, width=15
        )
        
        # 区切り線
        separator2 = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator2.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # 不良名
        self._create_defect_selection()
        
        # 修理済み
        self._create_repaired_selection()
        
        # 区切り線
        separator3 = tk.Frame(self.parent_frame, height=1, bg='#cccccc')
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # コメント
        self._create_comment_field()
    
    def _create_styled_input_field(self, label_text, variable, width=15, readonly=False):
        """スタイル付きの入力フィールドを作成"""
        # メインフレーム
        main_frame = tk.Frame(self.parent_frame, bg='#f5f5f5')
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
        
        return entry
    
    def _create_defect_selection(self):
        """不良名選択フィールドを作成"""
        # メインフレーム
        defect_frame = tk.Frame(self.parent_frame, bg='#f5f5f5')
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
        
        self.defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=self.defect_items,
            state="readonly",
            font=("Arial", 10)
        )
        self.defect_combobox.pack(fill=tk.X)
        
        # 初期値は空に設定
        self.defect_var.set("")
    
    def _create_repaired_selection(self):
        """修理済み選択フィールドを作成"""
        self.repaired_var = tk.StringVar(value="いいえ")
        
        # メインフレーム
        repaired_frame = tk.Frame(self.parent_frame, bg='#f5f5f5')
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
    
    def _create_comment_field(self):
        """コメントフィールドを作成"""
        # メインフレーム
        comment_frame = tk.Frame(self.parent_frame, bg='#f5f5f5')
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
        # 変更イベントバインド
        self._bind_change_events()
    
    def _bind_change_events(self):
        """変更イベントをバインド"""
        # 各入力フィールドの変更を監視
        self.reference_var.trace_add("write", self._on_data_changed)
        self.defect_var.trace_add("write", self._on_data_changed)
        if hasattr(self, 'repaired_var'):
            self.repaired_var.trace_add("write", self._on_data_changed)
    
    def _on_data_changed(self, *args):
        """データ変更時のコールバック"""
        if 'on_form_data_changed' in self.callbacks:
            self.callbacks['on_form_data_changed']()
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self.callbacks.update(callbacks)
    
    def set_readonly_mode(self, readonly: bool):
        """読み取り専用モードを設定"""
        self.readonly_mode = readonly
        
        state = tk.DISABLED if readonly else tk.NORMAL
        
        # 入力フィールドの状態を設定
        if hasattr(self, 'reference_entry') and self.reference_entry:
            self.reference_entry.config(state=state)
        
        # コンボボックス
        combo_state = "disabled" if readonly else "readonly"
        if hasattr(self, 'defect_combobox') and self.defect_combobox:
            self.defect_combobox.config(state=combo_state)
        
        # ラジオボタンの状態を設定
        if hasattr(self, 'repaired_yes') and hasattr(self, 'repaired_no'):
            radio_state = tk.DISABLED if readonly else tk.NORMAL
            self.repaired_yes.config(state=radio_state)
            self.repaired_no.config(state=radio_state)
        
        # コメントフィールドの状態を設定
        if hasattr(self, 'comment_text') and self.comment_text:
            self.comment_text.config(state=state)
    
    def update_model_options(self, models: List[str]):
        """モデル選択肢を更新 - MVCでは使用しない"""
        pass
    
    def update_defect_options(self, defects: List[str]):
        """不良項目選択肢を更新"""
        self.defect_items = defects
        if hasattr(self, 'defect_combobox') and self.defect_combobox:
            self.defect_combobox['values'] = defects
    
    def clear_form(self):
        """フォームをクリア"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("")
        if hasattr(self, 'repaired_var'):
            self.repaired_var.set("いいえ")
        
        # コメントフィールドをクリア
        if hasattr(self, 'comment_text') and self.comment_text:
            self.comment_text.delete("1.0", tk.END)
    
    def set_coordinate_detail(self, detail: Dict[str, Any]):
        """座標詳細情報を設定"""
        self.item_number_var.set(detail.get('item_number', ''))
        self.reference_var.set(detail.get('reference', ''))
        self.defect_var.set(detail.get('defect', ''))
        
        # 修理済み情報を設定
        if hasattr(self, 'repaired_var'):
            self.repaired_var.set(detail.get('repaired', 'いいえ'))
        
        # コメント情報を設定
        if hasattr(self, 'comment_text') and self.comment_text:
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert("1.0", detail.get('comment', ''))
    
    def get_coordinate_detail(self) -> Dict[str, Any]:
        """座標詳細情報を取得"""
        detail = {
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get()
        }
        
        # 修理済み情報を追加
        if hasattr(self, 'repaired_var'):
            detail['repaired'] = self.repaired_var.get()
        
        # コメント情報を追加
        if hasattr(self, 'comment_text') and self.comment_text:
            detail['comment'] = self.comment_text.get("1.0", tk.END).strip()
        
        return detail
    
    def get_form_data(self) -> Dict[str, Any]:
        """全フォームデータを取得（MVCでは座標詳細のみ）"""
        return self.get_coordinate_detail()
    
    def set_form_data(self, data: Dict[str, Any]):
        """フォームデータを設定（MVCでは座標詳細のみ）"""
        self.set_coordinate_detail(data)
    
    def focus_reference_entry(self):
        """リファレンス入力フィールドにフォーカス"""
        if hasattr(self, 'reference_entry') and self.reference_entry and not self.readonly_mode:
            self.reference_entry.focus_set()
    
    def update_worker_label(self, worker_text: str):
        """作業者ラベルを更新"""
        if hasattr(self, 'worker_label') and self.worker_label:
            self.worker_label.config(text=worker_text)
    
    def get_selected_model(self) -> str:
        """選択されているモデル名を取得"""
        # MVCではメインビューのモデル選択から取得
        if hasattr(self, 'main_view_ref') and self.main_view_ref:
            return self.main_view_ref.get_selected_model()
        return ""
    
    def set_main_view_reference(self, main_view):
        """MainViewの参照を設定"""
        self.main_view_ref = main_view
    
    def set_save_name(self, save_name: str):
        """保存名を設定"""
        # MVCではメインビューの保存名フィールドに設定
        if hasattr(self, 'main_view_ref') and self.main_view_ref:
            self.main_view_ref.set_save_name(save_name)
    
    def get_save_name(self) -> str:
        """保存名を取得"""
        # MVCではメインビューの保存名フィールドから取得
        if hasattr(self, 'main_view_ref') and self.main_view_ref:
            return self.main_view_ref.get_save_name()
        return ""
    
    def update_lot_label(self, lot_text: str):
        """ロット番号ラベルを更新"""
        if hasattr(self, 'lot_label') and self.lot_label:
            self.lot_label.config(text=lot_text)
    
    def set_lot_number(self, lot_number: str):
        """ロット番号を設定"""
        self.current_lot_number = lot_number
        if hasattr(self, 'lot_label') and self.lot_label:
            self.lot_label.config(text=f"指図番号: {lot_number}")
    
    def set_product_number(self, product_number: str):
        """製番を設定"""
        self.current_product_number = product_number
        if hasattr(self, 'product_label') and self.product_label:
            self.product_label.config(text=f"製番: {product_number}")
    
    def get_product_number(self) -> str:
        """製番を取得"""
        return self.current_product_number
    
    def get_lot_number(self) -> str:
        """ロット番号を取得"""
        return self.current_lot_number
    
    def clear_lot_number(self):
        """ロット番号をクリア（モデル変更時用）"""
        self.current_lot_number = ""
        if hasattr(self, 'lot_label') and self.lot_label:
            self.lot_label.config(text="指図番号: 未設定")
    
    def get_worker_no(self) -> str:
        """作業者番号を取得"""
        return self.current_worker_no
    
    def set_worker_no(self, worker_no: str):
        """作業者番号を設定"""
        self.current_worker_no = worker_no
