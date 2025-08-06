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
        self.lot_number_var = tk.StringVar()
        self.worker_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.item_number_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.defect_var = tk.StringVar()
        self.save_name_var = tk.StringVar()
        
        # UI要素の参照
        self.lot_entry = None
        self.worker_entry = None
        self.model_combobox = None
        self.item_entry = None
        self.reference_entry = None
        self.defect_combobox = None
        self.save_name_entry = None
        self.info_text = None
        
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
        # タイトル
        title_label = tk.Label(
            self.parent_frame, 
            text="座標詳細情報", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=5)
        
        # 基本情報フレーム
        self._setup_basic_info_frame()
        
        # 座標詳細フレーム
        self._setup_coordinate_detail_frame()
        
        # 保存情報フレーム
        self._setup_save_info_frame()
        
        # 情報表示フレーム
        self._setup_info_frame()
        
        # アクションボタンフレーム
        self._setup_action_buttons()
    
    def _setup_basic_info_frame(self):
        """基本情報フレームを設定"""
        basic_frame = tk.LabelFrame(self.parent_frame, text="基本情報", font=("Arial", 10))
        basic_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # ロット番号
        tk.Label(basic_frame, text="ロット番号:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.lot_entry = tk.Entry(basic_frame, textvariable=self.lot_number_var, font=("Arial", 9))
        self.lot_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 作業者No
        tk.Label(basic_frame, text="作業者No:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.worker_entry = tk.Entry(basic_frame, textvariable=self.worker_var, font=("Arial", 9))
        self.worker_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # モデル選択
        tk.Label(basic_frame, text="モデル:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.model_combobox = ttk.Combobox(
            basic_frame, 
            textvariable=self.model_var, 
            font=("Arial", 9),
            state="readonly"
        )
        self.model_combobox.pack(fill=tk.X, padx=5, pady=2)
    
    def _setup_coordinate_detail_frame(self):
        """座標詳細フレームを設定"""
        detail_frame = tk.LabelFrame(self.parent_frame, text="座標詳細", font=("Arial", 10))
        detail_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 項目番号
        tk.Label(detail_frame, text="項目番号:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.item_entry = tk.Entry(detail_frame, textvariable=self.item_number_var, font=("Arial", 9))
        self.item_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # リファレンス
        tk.Label(detail_frame, text="リファレンス:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.reference_entry = tk.Entry(detail_frame, textvariable=self.reference_var, font=("Arial", 9))
        self.reference_entry.pack(fill=tk.X, padx=5, pady=2)
        
        # 不良名
        tk.Label(detail_frame, text="不良名:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.defect_combobox = ttk.Combobox(
            detail_frame, 
            textvariable=self.defect_var, 
            values=self.defect_items,
            font=("Arial", 9)
        )
        self.defect_combobox.pack(fill=tk.X, padx=5, pady=2)
        
        # 変更イベントバインド
        self._bind_change_events()
    
    def _setup_save_info_frame(self):
        """保存情報フレームを設定"""
        save_frame = tk.LabelFrame(self.parent_frame, text="保存設定", font=("Arial", 10))
        save_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 保存名
        tk.Label(save_frame, text="保存名:", font=("Arial", 9)).pack(anchor="w", padx=5)
        self.save_name_entry = tk.Entry(save_frame, textvariable=self.save_name_var, font=("Arial", 9))
        self.save_name_entry.pack(fill=tk.X, padx=5, pady=2)
    
    def _setup_info_frame(self):
        """情報表示フレームを設定"""
        info_frame = tk.LabelFrame(self.parent_frame, text="情報", font=("Arial", 10))
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # スクロール付きテキストエリア
        text_frame = tk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.info_text = tk.Text(text_frame, height=8, font=("Arial", 9), wrap=tk.WORD)
        info_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _setup_action_buttons(self):
        """アクションボタンを設定"""
        button_frame = tk.Frame(self.parent_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 検索ボタン（閲覧モード時のみ表示）
        self.search_button = tk.Button(
            button_frame,
            text="座標検索",
            command=self.callbacks.get('search_coordinates'),
            font=("Arial", 9)
        )
        self.search_button.pack(side=tk.LEFT, padx=2)
        self.search_button.pack_forget()  # 初期は非表示
    
    def _bind_change_events(self):
        """変更イベントをバインド"""
        # 各入力フィールドの変更を監視
        self.lot_number_var.trace_add("write", self._on_data_changed)
        self.worker_var.trace_add("write", self._on_data_changed)
        self.model_var.trace_add("write", self._on_data_changed)
        self.item_number_var.trace_add("write", self._on_data_changed)
        self.reference_var.trace_add("write", self._on_data_changed)
        self.defect_var.trace_add("write", self._on_data_changed)
    
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
        
        # 基本情報の入力フィールド
        if self.lot_entry:
            self.lot_entry.config(state=state)
        if self.worker_entry:
            self.worker_entry.config(state=state)
        
        # 座標詳細の入力フィールド
        if self.item_entry:
            self.item_entry.config(state=state)
        if self.reference_entry:
            self.reference_entry.config(state=state)
        
        # コンボボックス
        combo_state = "disabled" if readonly else "readonly"
        if self.model_combobox:
            self.model_combobox.config(state=combo_state)
        
        defect_state = "disabled" if readonly else "normal"
        if self.defect_combobox:
            self.defect_combobox.config(state=defect_state)
        
        # 保存設定
        if self.save_name_entry:
            self.save_name_entry.config(state=state)
        
        # 検索ボタンの表示/非表示
        if readonly:
            self.search_button.pack(side=tk.LEFT, padx=2)
        else:
            self.search_button.pack_forget()
    
    def update_model_options(self, models: List[str]):
        """モデル選択肢を更新"""
        if self.model_combobox:
            self.model_combobox['values'] = models
    
    def update_defect_options(self, defects: List[str]):
        """不良項目選択肢を更新"""
        self.defect_items = defects
        if self.defect_combobox:
            self.defect_combobox['values'] = defects
    
    def clear_form(self):
        """フォームをクリア"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("")
    
    def set_coordinate_detail(self, detail: Dict[str, Any]):
        """座標詳細情報を設定"""
        self.item_number_var.set(detail.get('item_number', ''))
        self.reference_var.set(detail.get('reference', ''))
        self.defect_var.set(detail.get('defect', ''))
    
    def get_coordinate_detail(self) -> Dict[str, Any]:
        """座標詳細情報を取得"""
        return {
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get()
        }
    
    def get_form_data(self) -> Dict[str, Any]:
        """全フォームデータを取得"""
        return {
            'lot_number': self.lot_number_var.get(),
            'worker_no': self.worker_var.get(),
            'model': self.model_var.get(),
            'save_name': self.save_name_var.get(),
            'coordinate_detail': self.get_coordinate_detail()
        }
    
    def set_form_data(self, data: Dict[str, Any]):
        """フォームデータを設定"""
        self.lot_number_var.set(data.get('lot_number', ''))
        self.worker_var.set(data.get('worker_no', ''))
        self.model_var.set(data.get('model', ''))
        self.save_name_var.set(data.get('save_name', ''))
        
        if 'coordinate_detail' in data:
            self.set_coordinate_detail(data['coordinate_detail'])
    
    def display_info_text(self, text: str):
        """情報テキストを表示"""
        if self.info_text:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, text)
    
    def append_info_text(self, text: str):
        """情報テキストに追記"""
        if self.info_text:
            self.info_text.insert(tk.END, text)
            self.info_text.see(tk.END)
    
    def display_coordinate_summary(self, summary: Dict[str, Any]):
        """座標概要を表示（閲覧モード用）"""
        text = f"総座標数: {summary.get('total_count', 0)}個\n"
        text += f"画像: {summary.get('image_path', 'なし')}\n"
        text += "="*30 + "\n"
        
        coordinates = summary.get('coordinates', [])
        details = summary.get('details', [])
        
        for i, (x, y) in enumerate(coordinates):
            text += f"座標 {i+1}: ({x}, {y})\n"
            if i < len(details) and details[i]:
                detail = details[i]
                if detail.get('reference'):
                    text += f"  リファレンス: {detail['reference']}\n"
                if detail.get('defect'):
                    text += f"  不良名: {detail['defect']}\n"
            text += "\n"
        
        self.display_info_text(text)
    
    def display_coordinate_info(self, detail: Dict[str, Any], index: int):
        """特定座標の詳細情報を表示（閲覧モード用）"""
        text = f"■ 座標 {index + 1} の詳細情報\n"
        text += "="*30 + "\n"
        text += f"項目番号: {detail.get('item_number', 'なし')}\n"
        text += f"リファレンス: {detail.get('reference', 'なし')}\n"
        text += f"不良名: {detail.get('defect', 'なし')}\n"
        
        self.display_info_text(text)
    
    def focus_reference_entry(self):
        """リファレンス入力フィールドにフォーカス"""
        if self.reference_entry and not self.readonly_mode:
            self.reference_entry.focus_set()
