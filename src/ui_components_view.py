"""
UI Components View Mode Module
閲覧モード専用のUIコンポーネント
"""

import tkinter as tk
from tkinter import ttk
from .ui_components_base import UIComponentsBase

class UIComponentsView(UIComponentsBase):
    """閲覧モード専用のUIコンポーネントクラス"""
    
    def __init__(self, root, callbacks=None):
        super().__init__(root, callbacks)
    
    def setup_canvas_top(self):
        """キャンバス上段エリアをセットアップ（閲覧モード用）"""
        # グリッドレイアウトの設定
        self.canvas_top_frame.grid_columnconfigure(0, weight=0)  # モデル選択
        self.canvas_top_frame.grid_columnconfigure(1, weight=1)  # 検索エリア（拡張可能）
        self.canvas_top_frame.grid_rowconfigure(0, weight=1)
        
        # モデル選択フレーム
        model_frame = tk.Frame(self.canvas_top_frame)
        model_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
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
        
        # 検索エリアフレーム
        search_frame = tk.Frame(self.canvas_top_frame)
        search_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # 検索ボタン（右寄せ）    
        self.search_button = tk.Button(
            search_frame,
            text="座標を検索",
            command=self.callbacks.get('search_coordinates'),
            font=("Arial", 10),
            relief='raised',
            padx=15,
        )
        self.search_button.pack(side=tk.RIGHT, padx=10)

    def setup_sidebar(self):
        """サイドバーをセットアップ（閲覧モード用）"""
        # サイドバーのスタイル設定
        self.sidebar_frame.config(bg='#f0f8ff', relief='ridge', bd=1)  # 閲覧モードは薄い青色
        
        # タイトル
        self.title_label = tk.Label(
            self.sidebar_frame,
            text="不良詳細情報",
            font=("Arial", 14, "bold"),
            bg='#f0f8ff',
            fg='#2c3e50'
        )
        self.title_label.pack(pady=(15, 20))

        # 区切り線
        separator5 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator5.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 作業者ラベル
        self.worker_label = tk.Label(
            self.sidebar_frame,
            text="作業者: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        self.worker_label.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        # 区切り線
        separator1 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator1.pack(fill=tk.X, padx=15, pady=(0, 15))

        # ロット番号ラベル
        self.lot_number_label = tk.Label(
            self.sidebar_frame,
            text="指図番号: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        self.lot_number_label.pack(fill=tk.X, padx=15, pady=(0, 5))

        # 区切り線
        separator4 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator4.pack(fill=tk.X, padx=15, pady=(0, 15))

        # アイテム番号（読み取り専用）
        self.item_number_entry = self._create_styled_input_field(
            "項目番号", self.item_number_var, width=12, readonly=True
        )
        
        # リファレンス（読み取り専用）
        self.reference_entry = self._create_styled_input_field(
            "リファレンス", self.reference_var, width=15, readonly=True
        )
        
        # 区切り線
        separator2 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator2.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # 不良名（読み取り専用）
        self._create_defect_display()
        
        # 修理済み（読み取り専用）
        self._create_repaired_display()
        
        # 区切り線
        separator3 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # コメント（読み取り専用）
        self._create_comment_display()
    
    def _create_styled_input_field(self, label_text, variable, width=15, readonly=True):
        """スタイル付きの入力フィールドを作成（閲覧モード用）"""
        # メインフレーム
        main_frame = tk.Frame(self.sidebar_frame, bg='#f0f8ff')
        main_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            main_frame, 
            text=label_text, 
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # 入力フィールド（閲覧モードは常に読み取り専用）
        entry = tk.Entry(
            main_frame, 
            textvariable=variable, 
            width=width,
            font=("Arial", 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db',
            bg='#e8f4f8',  # 閲覧モード用の薄い青色
            state="readonly"
        )
        entry.pack(fill=tk.X)
        
        return entry
    
    def _create_defect_display(self):
        """不良名表示フィールドを作成（閲覧モード用）"""
        # メインフレーム
        defect_frame = tk.Frame(self.sidebar_frame, bg='#f0f8ff')
        defect_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            defect_frame, 
            text="不良名", 
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # 不良名表示フィールド（読み取り専用のEntry）
        self.defect_display = tk.Entry(
            defect_frame,
            textvariable=self.defect_var,
            font=("Arial", 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db',
            bg='#e8f4f8',
            state="readonly"
        )
        self.defect_display.pack(fill=tk.X)
    
    def _create_comment_display(self):
        """コメント表示フィールドを作成（閲覧モード用）"""
        # メインフレーム
        comment_frame = tk.Frame(self.sidebar_frame, bg='#f0f8ff')
        comment_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            comment_frame, 
            text="コメント", 
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 3))
        
        # テキストフィールドとスクロールバーのフレーム
        text_frame = tk.Frame(comment_frame, bg='#f0f8ff')
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # テキストフィールド（読み取り専用）
        self.comment_text = tk.Text(
            text_frame, 
            height=8, 
            font=("Arial", 9),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db',
            bg='#e8f4f8',
            wrap=tk.WORD,
            state="disabled"  # 読み取り専用
        )
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = tk.Scrollbar(text_frame, command=self.comment_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_text.config(yscrollcommand=scrollbar.set)
    
    def _create_repaired_display(self):
        """修理済み表示フィールドを作成（閲覧モード用）"""
        # メインフレーム
        repaired_frame = tk.Frame(self.sidebar_frame, bg='#f0f8ff')
        repaired_frame.pack(fill=tk.X, padx=15, pady=8)
        
        # ラベル
        label = tk.Label(
            repaired_frame, 
            text="修理済み", 
            font=("Arial", 10, "bold"),
            bg='#f0f8ff',
            fg='#34495e',
            anchor='w'
        )
        label.pack(fill=tk.X, pady=(0, 5))
        
        # 修理済み表示フィールド（読み取り専用のEntry）
        self.repaired_display = tk.Entry(
            repaired_frame,
            textvariable=self.repaired_var,
            font=("Arial", 10),
            relief='solid',
            bd=1,
            highlightthickness=1,
            highlightcolor='#3498db',
            bg='#e8f4f8',
            state="readonly"
        )
        self.repaired_display.pack(fill=tk.X)
    
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
    
    def update_form_with_coordinate_detail(self, detail):
        """座標の詳細情報でフォームを更新（閲覧モード用）"""
        if detail:
            self.item_number_var.set(detail.get('item_number', ''))
            self.reference_var.set(detail.get('reference', ''))
            self.defect_var.set(detail.get('defect', ''))
            self.repaired_var.set(detail.get('repaired', 'いいえ'))
            
            # コメントフィールドを更新（読み取り専用なので一時的に有効にして更新）
            if self.comment_text:
                self.comment_text.config(state="normal")
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", detail.get('comment', ''))
                self.comment_text.config(state="disabled")
    
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
            print(f"  不良名: {detail.get('defect', '未設定')}")
            print(f"  修理済み: {detail.get('repaired', 'いいえ')}")
            comment = detail.get('comment', '')
            if comment:
                print(f"  コメント: {comment}")
            else:
                print("  コメント: なし")
    
    def _update_sidebar_title_for_viewing(self, coord_num):
        """閲覧モード用のサイドバータイトルを更新"""
        if hasattr(self, 'title_label'):
            self.title_label.config(text=f"座標 {coord_num} の詳細情報")
    
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
        if hasattr(self, 'title_label'):
            self.title_label.config(text="不良詳細情報")
    
    def clear_form(self):
        """フォームをクリア（閲覧モード用）"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("")
        self.repaired_var.set("いいえ")
        
        # コメントフィールドをクリア（読み取り専用なので一時的に有効にして更新）
        if self.comment_text:
            self.comment_text.config(state="normal")
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.config(state="disabled")
    
    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        self._load_and_display_image()
    
    def get_current_coordinate_detail(self):
        """現在のフォームから座標詳細情報を取得（閲覧モード用）"""
        return {
            'item_number': self.item_number_var.get(),
            'reference': self.reference_var.get(),
            'defect': self.defect_var.get(),
            'comment': self.comment_text.get("1.0", tk.END).strip() if self.comment_text else "",
            'repaired': self.repaired_var.get()
        }
    
    def set_form_data(self, data):
        """フォームデータを設定（閲覧モード用）"""
        if 'date' in data:
            self.selected_date = data['date']
            self.update_date_label(self.selected_date)
        if 'mode' in data:
            self.mode_var.set(data['mode'])
        if 'model' in data:
            self.model_var.set(data['model'])
        if 'item_number' in data:
            self.item_number_var.set(data['item_number'])
        if 'reference' in data:
            self.reference_var.set(data['reference'])
        if 'defect' in data:
            self.defect_var.set(data['defect'])
        if 'comment' in data and self.comment_text:
            self.comment_text.config(state="normal")
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert("1.0", data['comment'])
            self.comment_text.config(state="disabled")
        if 'repaired' in data:
            self.repaired_var.set(data['repaired'])
    
    def set_readonly_mode(self, readonly=True):
        """閲覧モード用の読み取り専用設定"""
        # 閲覧モードでは常に読み取り専用として動作するため、
        # このメソッドは特に何もする必要がない
        pass
