"""
メインビュー
アプリケーションのメインウィンドウを管理
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List


class MainView:
    """メインビューを管理するクラス"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Coordinate App")
        self.root.geometry("1400x900")
        
        # ウィンドウを最大化
        self.root.state('zoomed')  # Windows用の最大化
        
        # 定数 - 既存UIと同じサイズ
        self.SIDEBAR_WIDTH = 250
        
        # 現在の日付
        self.selected_date = datetime.now().date()
        
        # UI要素の参照
        self.mode_var = tk.StringVar(value="編集")
        self.date_label = None
        self.undo_button = None
        self.redo_button = None
        self.settings_button = None
        
        # コールバック関数
        self.callbacks: Dict[str, Callable] = {}
        
        # レイアウト用フレーム
        self.main_frame = None
        self.content_frame = None
        self.sidebar_frame = None
        self.content_header_frame = None
        self.canvas_top_frame = None
        self.canvas_frame = None
        
        self._setup_layout()
    
    def _setup_layout(self):
        """レイアウトを設定 - 既存UIと同じ構造"""
        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # コンテンツフレーム
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # サイドバーフレーム（左側）
        self.sidebar_frame = tk.Frame(self.content_frame, width=self.SIDEBAR_WIDTH)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)
        
        # コンテンツヘッダーフレーム（右側上部）
        self.content_header_frame = tk.Frame(self.content_frame, height=40)
        self.content_header_frame.pack(fill=tk.X, padx=5, pady=5)
        self.content_header_frame.pack_propagate(False)
        
        # キャンバス上段フレーム
        self.canvas_top_frame = tk.Frame(self.content_frame, height=35)
        self.canvas_top_frame.pack(fill=tk.X, pady=(0, 5))
        self.canvas_top_frame.pack_propagate(False)
        
        # canvas_top_frameにコントロールを設定
        self._setup_canvas_top_controls()
        
        # キャンバスフレーム（右側下部）
        self.canvas_frame = tk.Frame(self.content_frame)
        self.canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
    
        # メニューボタンフレーム（最上部に配置 - 旧コードと同じ位置）
        self.menu_frame = tk.Frame(self.canvas_frame)
        self.menu_frame.pack(fill=tk.X, padx=5, pady=5)

    def setup_top_controls(self):
        """トップコントロールを設定 - 既存UIと同じスタイル"""
        # 日付表示フレーム
        date_frame = tk.Frame(self.content_header_frame)
        date_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 日付ラベル
        self.date_label = tk.Label(
            date_frame,
            text=f"日付: {self.selected_date.strftime('%Y年%m月%d日')}",
            font=("Arial", 12)
        )
        self.date_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 日付選択ボタン
        date_select_button = tk.Button(
            date_frame,
            text="日付を選択",
            command=self.callbacks.get('select_date'),
            font=("Arial", 10)
        )
        date_select_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Undo/Redoボタン
        undo_redo_frame = tk.Frame(self.content_header_frame)
        undo_redo_frame.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.undo_button = tk.Button(
            undo_redo_frame,
            text="↶ 元に戻す",
            command=self.callbacks.get('undo'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.undo_button.pack(side=tk.LEFT, padx=2)
        
        self.redo_button = tk.Button(
            undo_redo_frame,
            text="↷ 進む",
            command=self.callbacks.get('redo'),
            font=("Arial", 10),
            relief='raised',
            padx=8
        )
        self.redo_button.pack(side=tk.LEFT, padx=2)
        
        # 設定ボタン
        settings_frame = tk.Frame(self.content_header_frame)
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=5)
        
        self.settings_button = tk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self.callbacks.get('open_settings'),
            font=("Arial", 10),
            relief='raised',
            padx=10
        )
        self.settings_button.pack()
        
        # モード選択
        mode_frame = tk.Frame(self.content_header_frame)
        mode_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        tk.Label(mode_frame, text="モード:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        mode_edit = tk.Radiobutton(
            mode_frame,
            text="編集",
            variable=self.mode_var,
            value="編集",
            command=self.callbacks.get('on_mode_change'),
            font=("Arial", 10)
        )
        mode_edit.pack(side=tk.LEFT, padx=5)
        
        mode_view = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            command=self.callbacks.get('on_mode_change'),
            font=("Arial", 10)
        )
        mode_view.pack(side=tk.LEFT, padx=5)
    
    def _setup_canvas_top_controls(self):
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
        
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            state="readonly",
            width=50  # 画像ファイル名が長い場合があるので幅を広げる
        )
        self.model_combobox.pack(side=tk.LEFT, padx=5)
        # モデル選択時のイベントをバインド
        self.model_combobox.bind('<<ComboboxSelected>>', self._on_model_selected)
        
        # 保存名フレーム
        save_frame = tk.Frame(self.canvas_top_frame)
        save_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        tk.Label(save_frame, text="保存名:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.save_name_var = tk.StringVar()
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
            command=self.callbacks.get('on_save_button_click'),
            font=("Arial", 10),
            relief='raised',
            padx=15,
        )
        self.save_button.pack(side=tk.LEFT, padx=10)
    
        # 「現品票で切り替え」ボタン
        print(f"[DEBUG] 現品票切り替えボタンを作成中...")
        print(f"[DEBUG] コールバック 'on_item_tag_change': {self.callbacks.get('on_item_tag_change')}")
        
        self.item_tag_change_button = tk.Button(
            lot_frame,
            text="現品票で切り替え",
            command=self.callbacks.get('on_item_tag_change'),
            font=("Arial", 10),
            relief='raised',
            padx=10,
        )
        self.item_tag_change_button.pack(side=tk.LEFT, padx=10)
        
        print(f"[DEBUG] 現品票切り替えボタンが作成されました: {self.item_tag_change_button}")
        
        # ボタンのコマンドをテスト
        def test_button_click():
            print("[DEBUG] 現品票切り替えボタンがクリックされました（テスト関数）")
            if 'on_item_tag_change' in self.callbacks:
                print("[DEBUG] on_item_tag_changeコールバックが存在します")
                self.callbacks['on_item_tag_change']()
            else:
                print("[DEBUG] on_item_tag_changeコールバックが見つかりません")
        
        # デバッグ用に直接コールバック関数を設定
        if not self.callbacks.get('on_item_tag_change'):
            print("[DEBUG] コールバックが設定されていないため、テスト関数を設定します")
            self.item_tag_change_button.config(command=test_button_click)        

    def initialize_models(self):
        """モデル選択肢を初期化（旧コード互換機能）"""
        if 'load_models_from_file' in self.callbacks:
            try:
                model_data = self.callbacks['load_models_from_file']()
                self.update_model_options(model_data)
                
                # 最初のモデルを自動選択（旧コードと同じ動作）
                if hasattr(self, 'model_combobox') and self.model_combobox['values']:
                    self.model_combobox.current(0)
                    self._on_model_selected()  # 選択イベントをトリガー
                    
                print(f"モデル初期化完了: {len(self.model_combobox['values']) if hasattr(self, 'model_combobox') else 0}個のモデル")
            except Exception as e:
                print(f"モデル初期化エラー: {e}")
                # エラーの場合はデフォルト値を設定
                if hasattr(self, 'model_combobox'):
                    self.model_combobox['values'] = ["設定エラー"]
                    self.model_combobox.current(0)
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        print(f"[DEBUG] set_callbacks が呼び出されました: {len(callbacks)}個のコールバック")
        for key in callbacks:
            print(f"[DEBUG] 設定中のコールバック '{key}': {callbacks[key]}")
        
        self.callbacks.update(callbacks)
        
        print(f"[DEBUG] コールバック設定後: {len(self.callbacks)}個")
        print(f"[DEBUG] on_item_tag_change設定確認: {self.callbacks.get('on_item_tag_change')}")
        
        # ボタンのコマンドを更新
        self._update_button_commands()
    
    def _update_button_commands(self):
        """ボタンのコマンドを更新"""
        try:
            if hasattr(self, 'item_tag_change_button') and self.item_tag_change_button:
                callback = self.callbacks.get('on_item_tag_change')
                if callback:
                    print(f"[DEBUG] 現品票切り替えボタンのコマンドを更新: {callback}")
                    self.item_tag_change_button.config(command=callback)
                else:
                    print("[DEBUG] on_item_tag_changeコールバックが見つかりません")
        except Exception as e:
            print(f"[DEBUG] ボタンコマンド更新エラー: {e}")
    
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
    
    def update_model_combobox(self, models: list):
        """モデル選択肢を更新"""
        if hasattr(self, 'model_combobox'):
            self.model_combobox['values'] = models
            if models and not self.model_var.get():
                self.model_combobox.current(0)
    
    def get_model(self) -> str:
        """選択されたモデルを取得"""
        return self.model_var.get()
    
    def get_model_values(self) -> list:
        """モデルコンボボックスの全ての選択肢を取得"""
        if hasattr(self, 'model_combobox') and self.model_combobox:
            return list(self.model_combobox['values'])
        return []
    
    def get_model_count(self) -> int:
        """モデルコンボボックスの選択肢数を取得"""
        return len(self.get_model_values())
    
    def get_selected_model(self) -> str:
        """選択されたモデルを取得（旧コード互換）"""
        return self.model_var.get()
    
    def set_model(self, model: str):
        """モデルを設定"""
        self.model_var.set(model)
        
        # コンボボックスの選択インデックスも更新
        if hasattr(self, 'model_combobox') and self.model_combobox:
            values = list(self.model_combobox['values'])
            if model in values:
                index = values.index(model)
                self.model_combobox.current(index)
                print(f"[DEBUG] コンボボックスで '{model}' を選択しました（インデックス: {index}）")
    
    def get_save_name(self) -> str:
        """保存名を取得"""
        return self.save_name_var.get()
    
    def set_save_name(self, save_name: str):
        """保存名を設定"""
        self.save_name_var.set(save_name)
    
    def get_lot_number(self) -> str:
        """ロット番号を取得"""
        return self.lot_number_var.get()
    
    def set_lot_number(self, lot_number: str):
        """ロット番号を設定"""
        self.lot_number_var.set(lot_number)
    
    def clear_lot_number(self):
        """ロット番号入力をクリア"""
        self.lot_number_var.set("")
    
    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        if 'on_model_selected' in self.callbacks:
            self.callbacks['on_model_selected']()
    
    def _on_lot_number_enter(self, event):
        """ロット番号入力フィールドでEnterキーが押された時の処理"""
        if 'on_lot_number_save' in self.callbacks:
            self.callbacks['on_lot_number_save']()
    
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
    
    def show_item_tag_switch_dialog(self):
        """現品票切り替えダイアログを表示"""
        print("[DEBUG] show_item_tag_switch_dialog が呼び出されました")
        try:
            from src.views.dialogs.item_tag_switch_dialog import show_item_tag_switch_dialog
            print("[DEBUG] ダイアログ関数のインポートに成功しました")
            print(f"[DEBUG] root ウィンドウ: {self.root}")
            result = show_item_tag_switch_dialog(self.root)
            print(f"[DEBUG] ダイアログの戻り値: {result}")
            return result
        except ImportError as e:
            print(f"ダイアログのインポートエラー: {e}")
            self.show_error(f"現品票切り替えダイアログの読み込みに失敗しました:\n{str(e)}")
            return None
        except Exception as e:
            print(f"ダイアログ表示エラー: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"ダイアログ表示中にエラーが発生しました:\n{str(e)}")
            return None
    
    def setup_menu_buttons(self):
        """メニューボタンを設定（旧コードと同じ配置）"""
        # 画像選択ボタン
        select_button = tk.Button(
            self.menu_frame,
            text="画像を選択",
            command=self.callbacks.get('select_image'),
            font=("Arial", 10)
        )
        select_button.pack(side=tk.LEFT, padx=5)
        
        # JSON読み込みボタン
        load_button = tk.Button(
            self.menu_frame,
            text="JSONを読み込みだ",
            command=self.callbacks.get('load_json'),
            font=("Arial", 10)
        )
        load_button.pack(side=tk.LEFT, padx=5)
        
        # 保存ボタン
        save_button = tk.Button(
            self.menu_frame,
            text="座標を保存",
            command=self.callbacks.get('save_coordinates'),
            font=("Arial", 10)
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # クリアボタン
        clear_button = tk.Button(
            self.menu_frame,
            text="座標をクリア",
            command=self.callbacks.get('clear_coordinates'),
            font=("Arial", 10)
        )
        clear_button.pack(side=tk.LEFT, padx=5)
    
    def get_form_data(self) -> Dict[str, Any]:
        """フォームデータを取得（旧コード互換）"""
        return {
            'model': self.get_selected_model(),
            'save_name': self.get_save_name(),
            'lot_number': self.get_lot_number()
        }
    
    def update_model_options(self, model_data: List[Dict[str, str]]):
        """モデル選択リストを更新（旧コード互換機能）"""
        if not hasattr(self, 'model_combobox') or not self.model_combobox:
            return
        
        # 辞書リストからファイル名のみを抽出
        model_values = [list(item.keys())[0] for item in model_data if item]
        
        # 辞書データを保持（画像パス取得で使用）
        self.model_data = model_data
        
        # コンボボックスの値を更新
        self.model_combobox['values'] = model_values
        
        # 現在の選択値が新しいリストに存在するかチェック
        current_value = self.model_var.get()
        if current_value not in model_values and model_values:
            # 存在しない場合は最初の項目を選択
            self.model_combobox.current(0)
            # モデル選択イベントをトリガー
            self._on_model_selected()
        
        print(f"モデル選択肢を更新しました: {len(model_values)}個のモデル")
    
    def get_model_image_path(self, model_name: str) -> str:
        """選択されたモデルの画像パスを取得"""
        if not hasattr(self, 'model_data') or not self.model_data:
            return ""
        
        for model_dict in self.model_data:
            if model_name in model_dict:
                return model_dict[model_name]
        
        return ""
