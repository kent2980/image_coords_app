"""
UI Components Edit Mode Module
編集モード専用のUIコンポーネント
"""

import tkinter as tk
from tkinter import ttk
import re
from .ui_components_base import UIComponentsBase

class UIComponentsEdit(UIComponentsBase):
    """編集モード専用のUIコンポーネントクラス"""
    
    def __init__(self, root, callbacks=None):
        super().__init__(root, callbacks)
    
    def setup_canvas_top(self):
        """キャンバス上段エリアをセットアップ（編集モード用）"""
        # グリッドレイアウトの設定
        self.canvas_top_frame.grid_columnconfigure(0, weight=0)  # モデル選択
        self.canvas_top_frame.grid_columnconfigure(1, weight=1)  # 保存名（拡張可能）
        self.canvas_top_frame.grid_rowconfigure(0, weight=1)
        self.canvas_top_frame.grid_rowconfigure(1, weight=1)  # ロット番号用の行
        
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
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.save_name_entry = tk.Entry(
            save_frame,
            textvariable=self.save_name_var,
            width=50,  # 幅を広げて長い名前に対応    
        )
        self.save_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # ロット番号入力エリア（1段下の行に配置）
        lot_frame = tk.Frame(self.canvas_top_frame)
        lot_frame.grid(row=1, column=0, padx=10, pady=5, sticky="w", columnspan=2)
        
        tk.Label(lot_frame, text="指図:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.lot_number_var = tk.StringVar()
        self.lot_number_entry = tk.Entry(   
            lot_frame,
            textvariable=self.lot_number_var,
            width=20,  # ロット番号は短いので幅を狭く設定
        )
        self.lot_number_entry.pack(side=tk.LEFT, padx=5)
        
        # Enterキーで保存処理を実行
        self.lot_number_entry.bind('<Return>', self._on_lot_number_enter)
        
        # 保存ボタン（ロット番号の右隣）
        self.save_button = tk.Button(
            lot_frame,
            text="保存",
            command=self._on_save_button_click,
            font=("Arial", 10),
            relief='raised',
            padx=15,
        )
        self.save_button.pack(side=tk.LEFT, padx=10)

    def setup_sidebar(self):
        """サイドバーをセットアップ（編集モード用）"""
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
        separator5 = tk.Frame(self.sidebar_frame, height=1, bg='#cccccc')
        separator5.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 作業者ラベル
        self.worker_label = tk.Label(
            self.sidebar_frame,
            text="作業者: 未設定",
            font=("Arial", 10, "bold"),
            bg='#f5f5f5',
            fg='#555555',
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
            bg='#f5f5f5',
            fg='#555555',
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
        # 初期値は空に設定
        self.defect_var.set("")
        
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
            self.defect_var.set(detail.get('defect', ''))  # デフォルトを空に変更
            self.repaired_var.set(detail.get('repaired', 'いいえ'))
            
            # コメントフィールドを更新
            if self.comment_text:
                self.comment_text.delete("1.0", tk.END)
                self.comment_text.insert("1.0", detail.get('comment', ''))
    
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
        self.defect_var.set("")  # 不良名を空に設定
        self.repaired_var.set("いいえ")
        
        # コメントフィールドをクリア
        if self.comment_text:
            self.comment_text.delete("1.0", tk.END)
    
    def _on_save_button_click(self):
        """保存ボタンクリック時の処理"""
        # 作業者が設定されているかチェック
        if not self.current_worker_no:
            from tkinter import messagebox
            messagebox.showerror("エラー", "作業者が設定されていません。")
            return
        
        # ロット番号を保存
        if hasattr(self, 'lot_number_var'):
            new_lot_number = self.lot_number_var.get().strip()
            if new_lot_number:
                # ロット番号の形式をチェック (7桁-2桁の形式)
                lot_pattern = r'^\d{7}-10$|^\d{7}-20$'
                if re.match(lot_pattern, new_lot_number):
                    self.current_lot_number = new_lot_number
                    self._update_lot_number_label()
                    print(f"ロット番号を保存しました: {self.current_lot_number}")
                    
                    # ロット番号入力フィールドをクリア
                    self.lot_number_var.set("")
        
                else:
                    # 形式が正しくない場合はエラーメッセージを表示
                    self._show_lot_number_error("ロット番号の形式が正しくありません。\n形式: 1234567-01 (7桁-2桁)")
                    return
            else:
                # ロット番号が空の場合はエラーメッセージを表示
                self._show_lot_number_error("ロット番号を入力してください。")
                return
         
    def _show_lot_number_error(self, message):
        """ロット番号エラーダイアログを表示"""
        from tkinter import messagebox
        messagebox.showerror("ロット番号エラー", message)
    
    def _on_lot_number_enter(self, event):
        """ロット番号入力フィールドでEnterキーが押された時の処理"""
        self._on_save_button_click()
    
    def _on_form_data_changed(self, *args):
        """フォームデータが変更された時のイベントハンドラー"""
        if self.callbacks.get('on_form_data_changed'):
            self.callbacks['on_form_data_changed']()
    
    def _on_comment_changed(self, event=None):
        """コメントフィールドが変更された時のイベントハンドラー"""
        if self.callbacks.get('on_form_data_changed'):
            self.callbacks['on_form_data_changed']()
    
    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        self._load_and_display_image()
        
        # 保存ディレクトリをセットアップ
        if self.callbacks.get('setup_json_save_dir'):
            self.callbacks['setup_json_save_dir']()
        
        # 保存名エントリを自動設定
        if self.callbacks.get('setup_save_name_entry'):
            self.callbacks['setup_save_name_entry']()
    
    def set_readonly_mode(self, readonly=True):
        """編集モードでは読み取り専用設定は適用しない"""
        # 編集モードでは常に入力可能状態を維持
        pass
    
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
