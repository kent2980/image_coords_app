"""
メインビュー
アプリケーションのメインウィンドウを管理
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    overload,
)


# コールバック関数の型定義
class CallbackProtocol(Protocol):
    """コールバック関数のプロトコル"""

    def __call__(self) -> Any: ...


class ParameterCallbackProtocol(Protocol):
    """パラメータを受け取るコールバック関数のプロトコル"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


# 具体的なコールバック関数の型定義
class CallbackTypes(TypedDict, total=False):
    """コールバック関数の型定義辞書"""

    # ファイル操作
    open_file: CallbackProtocol
    save_file: CallbackProtocol
    exit_app: CallbackProtocol

    # 編集操作
    undo_action: CallbackProtocol
    redo_action: CallbackProtocol
    clear_coordinates: CallbackProtocol
    delete_coordinate: CallbackProtocol
    prev_coordinate: CallbackProtocol
    next_coordinate: CallbackProtocol

    # UI操作
    on_mode_change: CallbackProtocol
    on_model_selected: CallbackProtocol
    on_item_tag_change: CallbackProtocol
    on_lot_number_save: CallbackProtocol
    open_settings: CallbackProtocol

    # プロジェクト操作
    new_project: CallbackProtocol
    new_file: CallbackProtocol
    select_date: CallbackProtocol
    select_image: CallbackProtocol
    load_json: CallbackProtocol
    save_coordinates: CallbackProtocol
    save_data: CallbackProtocol
    on_save_button_click: CallbackProtocol
    load_models_from_file: CallbackProtocol
    setup_save_name_entry: CallbackProtocol

    # 基板操作
    prev_board: CallbackProtocol
    next_board: CallbackProtocol
    delete_board: CallbackProtocol


class MainView:
    """メインビューを管理するクラス"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Image Coordinate App")
        self.root.geometry("1400x900")

        # ウィンドウを最大化
        self.root.state("zoomed")  # Windows用の最大化

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

        # コールバック関数（型安全）
        self.callbacks: CallbackTypes = {}

        # レイアウト用フレーム
        self.menu_frame = None
        self.main_frame = None
        self.content_frame = None
        self.sidebar_frame = None
        self.content_header_frame = None
        self.canvas_top_frame = None
        self.canvas_frame = None

        # 生産情報用変数
        self.save_name_var = tk.StringVar(value="")

        # UI設定の初期化
        self._setup_layout()

    # 型安全なコールバック取得メソッド
    @overload
    def get_callback(self, key: str) -> Optional[CallbackProtocol]: ...

    @overload
    def get_callback(self, key: str, default: CallbackProtocol) -> CallbackProtocol: ...

    def get_callback(
        self, key: str, default: Optional[CallbackProtocol] = None
    ) -> Optional[CallbackProtocol]:
        """型安全なコールバック関数取得"""
        return self.callbacks.get(key, default)  # type: ignore

    def has_callback(self, key: str) -> bool:
        """コールバック関数の存在確認"""
        return key in self.callbacks and self.callbacks[key] is not None

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

        # メニューボタンフレーム（最上部に配置 - 旧コードと同じ位置）
        self.menu_frame = tk.Frame(self.content_frame)
        self.menu_frame.pack(fill=tk.X, padx=5, pady=5)

        # キャンバスフレーム
        self.canvas_frame = tk.Frame(
            self.content_frame, relief=tk.SUNKEN, borderwidth=3, bg="#f0f0f0"
        )
        self.canvas_frame.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=30, pady=30
        )

    def setup_menu_frame(self):
        """メニューフレームを設定"""

        # メインメニュー
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # ファイルメニュー
        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="開く", command=self.get_callback("open_file"))
        file_menu.add_command(label="保存", command=self.get_callback("save_file"))
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.get_callback("exit_app"))

        # 編集メニュー
        edit_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="編集", menu=edit_menu)
        edit_menu.add_command(
            label="元に戻す", command=self.get_callback("undo_action")
        )
        edit_menu.add_command(
            label="やり直し", command=self.get_callback("redo_action")
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="座標をクリア", command=self.get_callback("clear_coordinates")
        )

        # 基盤メニュー
        board_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="基盤", menu=board_menu)
        board_menu.add_command(
            label="全基盤保存", command=self.get_callback("save_all_boards")
        )
        board_menu.add_command(
            label="基盤セッション読み込み",
            command=self.get_callback("load_board_session"),
        )
        board_menu.add_separator()
        board_menu.add_command(
            label="前の基盤", command=self.get_callback("prev_board")
        )
        board_menu.add_command(
            label="次の基盤", command=self.get_callback("next_board")
        )
        board_menu.add_command(
            label="基盤削除", command=self.get_callback("delete_board")
        )

    def setup_top_controls(self):
        """トップコントロールを設定 - 既存UIと同じスタイル"""

        # 設定ボタン
        settings_frame = tk.Frame(self.content_header_frame)
        settings_frame.pack(side=tk.RIGHT, padx=15, pady=5)

        self.settings_button = tk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self.get_callback("open_settings"),
            font=("Arial", 10),
            relief="raised",
            padx=10,
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
            command=self.get_callback("on_mode_change"),
            font=("Arial", 10),
        )
        mode_edit.pack(side=tk.LEFT, padx=5)

        mode_view = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            command=self.get_callback("on_mode_change"),
            font=("Arial", 10),
        )
        mode_view.pack(side=tk.LEFT, padx=5)

    def _setup_canvas_top_controls(self):
        """キャンバス上段エリアをセットアップ（編集モード用）"""
        # グリッドレイアウトの設定
        self.canvas_top_frame.grid_columnconfigure(0, weight=0)
        self.canvas_top_frame.grid_columnconfigure(1, weight=0)
        self.canvas_top_frame.grid_columnconfigure(2, weight=0)
        self.canvas_top_frame.grid_columnconfigure(3, weight=0)
        self.canvas_top_frame.grid_columnconfigure(
            4, weight=0
        )  # 「現品票で切り替え」ボタンのために最後の列を広げる
        self.canvas_top_frame.grid_rowconfigure(0, weight=1)

        # モデル選択フレーム
        tk.Label(self.canvas_top_frame, text="モデル:", font=("Arial", 10)).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            self.canvas_top_frame,
            textvariable=self.model_var,
            state="readonly",
            width=50,  # 画像ファイル名が長い場合があるので幅を広げる
        )
        self.model_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        # モデル選択時のイベントをバインド
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)

        # ロット番号入力エリア（1段下の行に配置）
        tk.Label(self.canvas_top_frame, text="指図:", font=("Arial", 10)).grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.lot_number_var = tk.StringVar()
        self.lot_number_entry = tk.Entry(
            self.canvas_top_frame,
            textvariable=self.lot_number_var,
            width=20,  # ロット番号は短いので幅を狭く設定
        )
        self.lot_number_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Enterキーで保存処理を実行
        self.lot_number_entry.bind("<Return>", self._on_lot_number_enter)

        # 「現品票で切り替え」ボタン
        print(f"[DEBUG] 現品票切り替えボタンを作成中...")
        print(
            f"[DEBUG] コールバック 'on_item_tag_change': {self.get_callback('on_item_tag_change')}"
        )

        self.item_tag_change_button = tk.Button(
            self.canvas_top_frame,
            text="現品票で切り替え",
            command=self.get_callback("on_item_tag_change"),
            font=("Arial", 10),
            relief="raised",
            padx=10,
        )
        self.item_tag_change_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        print(
            f"[DEBUG] 現品票切り替えボタンが作成されました: {self.item_tag_change_button}"
        )

        # ボタンのコマンドをテスト
        def test_button_click():
            print("[DEBUG] 現品票切り替えボタンがクリックされました（テスト関数）")
            if self.has_callback("on_item_tag_change"):
                print("[DEBUG] on_item_tag_changeコールバックが存在します")
                callback = self.get_callback("on_item_tag_change")
                if callback:
                    callback()
            else:
                print("[DEBUG] on_item_tag_changeコールバックが見つかりません")

        # デバッグ用に直接コールバック関数を設定
        if not self.has_callback("on_item_tag_change"):
            print("[DEBUG] コールバックが設定されていないため、テスト関数を設定します")
            self.item_tag_change_button.config(command=test_button_click)

    def initialize_models(self):
        """モデル選択肢を初期化（旧コード互換機能）"""
        if self.has_callback("load_models_from_file"):
            try:
                callback = self.get_callback("load_models_from_file")
                if callback:
                    model_data = callback()
                    self.update_model_options(model_data)

                    # 最初のモデルを自動選択（旧コードと同じ動作）
                    if (
                        hasattr(self, "model_combobox")
                        and self.model_combobox["values"]
                    ):
                        self.model_combobox.current(0)
                        self._on_model_selected()  # 選択イベントをトリガー

                    print(
                        f"モデル初期化完了: {len(self.model_combobox['values']) if hasattr(self, 'model_combobox') else 0}個のモデル"
                    )
            except Exception as e:
                print(f"モデル初期化エラー: {e}")
                # エラーの場合はデフォルト値を設定
                if hasattr(self, "model_combobox"):
                    self.model_combobox["values"] = ["設定エラー"]
                    self.model_combobox.current(0)

    def set_callbacks(self, callbacks: CallbackTypes):
        """コールバック関数を設定"""
        print(
            f"[DEBUG] set_callbacks が呼び出されました: {len(callbacks)}個のコールバック"
        )
        for key in callbacks:
            print(f"[DEBUG] 設定中のコールバック '{key}': {callbacks[key]}")

        self.callbacks.update(callbacks)

        print(f"[DEBUG] コールバック設定後: {len(self.callbacks)}個")
        print(
            f"[DEBUG] on_item_tag_change設定確認: {self.get_callback('on_item_tag_change')}"
        )

        # ボタンのコマンドを更新
        self._update_button_commands()

    def _update_button_commands(self):
        """ボタンのコマンドを更新"""
        try:
            if hasattr(self, "item_tag_change_button") and self.item_tag_change_button:
                callback = self.get_callback("on_item_tag_change")
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
        if hasattr(self, "model_combobox"):
            self.model_combobox["values"] = models
            if models and not self.model_var.get():
                self.model_combobox.current(0)

    def get_model(self) -> str:
        """選択されたモデルを取得"""
        return self.model_var.get()

    def get_model_values(self) -> list:
        """モデルコンボボックスの全ての選択肢を取得"""
        if hasattr(self, "model_combobox") and self.model_combobox:
            return list(self.model_combobox["values"])
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
        if hasattr(self, "model_combobox") and self.model_combobox:
            values = list(self.model_combobox["values"])
            if model in values:
                index = values.index(model)
                self.model_combobox.current(index)
                print(
                    f"[DEBUG] コンボボックスで '{model}' を選択しました（インデックス: {index}）"
                )

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

    def get_coordinate_number_text(self) -> str:
        """座標番号ラベルのテキストを取得"""
        if hasattr(self, "coordinate_number_label") and self.coordinate_number_label:
            return self.coordinate_number_label.cget("text")
        return ""

    def set_coordinate_number_text(self, text: str):
        """座標番号ラベルのテキストを設定"""
        if hasattr(self, "coordinate_number_label") and self.coordinate_number_label:
            self.coordinate_number_label.config(text=text)

    def update_coordinate_number_display(self, current_index: int, total_count: int):
        """座標番号表示を更新（例：1/5）"""
        if total_count > 0:
            display_text = f"{current_index + 1}/{total_count}"
        else:
            display_text = "0/0"
        self.set_coordinate_number_text(display_text)

    def clear_coordinate_number_display(self):
        """座標番号表示をクリア"""
        self.set_coordinate_number_text("")

    def set_coordinate_number_style(
        self,
        bg_color: str = "white",
        fg_color: str = "black",
        font_tuple: tuple = ("Arial", 10),
    ):
        """座標番号ラベルのスタイルを設定"""
        if hasattr(self, "coordinate_number_label") and self.coordinate_number_label:
            self.coordinate_number_label.config(
                bg=bg_color, fg=fg_color, font=font_tuple
            )

    def highlight_coordinate_number(self, highlight: bool = True):
        """座標番号ラベルをハイライト表示"""
        if highlight:
            self.set_coordinate_number_style(bg_color="#ffeb3b", fg_color="black")
        else:
            self.set_coordinate_number_style(bg_color="white", fg_color="black")

    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        if self.has_callback("on_model_selected"):
            callback = self.get_callback("on_model_selected")
            if callback:
                callback()

    def _on_lot_number_enter(self, event):
        """ロット番号入力フィールドでEnterキーが押された時の処理"""
        print("[DEBUG] ロット番号入力フィールドでEnterキーが押されました")
        if self.has_callback("on_lot_number_save"):
            callback = self.get_callback("on_lot_number_save")
            if callback:
                callback()

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
            from src.views.dialogs.item_tag_switch_dialog import (
                show_item_tag_switch_dialog,
            )

            print("[DEBUG] ダイアログ関数のインポートに成功しました")
            print(f"[DEBUG] root ウィンドウ: {self.root}")
            result = show_item_tag_switch_dialog(self.root)
            print(f"[DEBUG] ダイアログの戻り値: {result}")
            return result
        except ImportError as e:
            print(f"ダイアログのインポートエラー: {e}")
            self.show_error(
                f"現品票切り替えダイアログの読み込みに失敗しました:\n{str(e)}"
            )
            return None
        except Exception as e:
            print(f"ダイアログ表示エラー: {e}")
            import traceback

            traceback.print_exc()
            self.show_error(f"ダイアログ表示中にエラーが発生しました:\n{str(e)}")
            return None

    def setup_menu_buttons(self):
        """メニューボタンを設定（旧コードと同じ配置）"""

        # 座標フレーム
        coordinate_frame = tk.Frame(self.menu_frame)
        coordinate_frame.pack(side=tk.LEFT, padx=5)

        # 座標ラベル
        coordinate_label = tk.Label(
            coordinate_frame, text="座標操作:", font=("Arial", 10)
        )
        coordinate_label.pack(side=tk.LEFT, padx=5)

        # 座標番号ラベル（白背景）
        self.coordinate_number_label = tk.Label(
            coordinate_frame,
            text="0 / 0",
            font=("Arial", 12),
            width=10,
        )
        self.coordinate_number_label.pack(side=tk.LEFT, padx=5)

        # 前へボタン
        prev_button = tk.Button(
            coordinate_frame,
            text="前へ",
            command=self.get_callback("prev_coordinate"),
            font=("Arial", 10),
        )
        prev_button.pack(side=tk.LEFT, padx=2)

        # 次へボタン
        next_button = tk.Button(
            coordinate_frame,
            text="次へ",
            command=self.get_callback("next_coordinate"),
            font=("Arial", 10),
        )
        next_button.pack(side=tk.LEFT, padx=2)

        # 削除ボタン
        clear_button = tk.Button(
            coordinate_frame,
            text="削除",
            command=self.get_callback("delete_coordinate"),
            font=("Arial", 10),
        )
        clear_button.pack(side=tk.LEFT, padx=2)

        # 全削除ボタン
        all_clear_button = tk.Button(
            coordinate_frame,
            text="全削除",
            command=self.get_callback("clear_coordinates"),
            font=("Arial", 10),
        )
        all_clear_button.pack(side=tk.LEFT, padx=2)

        # 基板選択フレーム
        board_frame = tk.Frame(self.menu_frame)
        board_frame.pack(side=tk.LEFT, padx=5)

        # 基板選択ラベル
        self.board_label = tk.Label(
            board_frame,
            text="基板選択:",
            font=("Arial", 12),
            width=10,
        )
        self.board_label.pack(side=tk.LEFT, padx=5)

        # 基板インデックスラベル
        self.board_index_label = tk.Label(board_frame, text="0 / 0", font=("Arial", 12))
        self.board_index_label.pack(side=tk.LEFT, padx=5)

        # 基板選択「前へ」ボタン
        prev_board_button = tk.Button(
            self.menu_frame,
            text="前へ",
            command=self.get_callback("prev_board"),
            font=("Arial", 10),
        )
        prev_board_button.pack(side=tk.LEFT, padx=5)

        # 基板選択「次へ」ボタン
        next_board_button = tk.Button(
            self.menu_frame,
            text="次へ",
            command=self.get_callback("next_board"),
            font=("Arial", 10),
        )
        next_board_button.pack(side=tk.LEFT, padx=5)

        # 基板削除ボタン
        delete_board_button = tk.Button(
            self.menu_frame,
            text="基板削除",
            command=self.get_callback("delete_board"),
            font=("Arial", 10),
        )
        delete_board_button.pack(side=tk.LEFT, padx=5)

    def get_form_data(self) -> Dict[str, Any]:
        """フォームデータを取得（旧コード互換）"""
        return {
            "model": self.get_selected_model(),
            "save_name": self.get_save_name(),
            "lot_number": self.get_lot_number(),
        }

    def update_model_options(self, model_data: List[Dict[str, str]]):
        """モデル選択リストを更新（旧コード互換機能）"""
        if not hasattr(self, "model_combobox") or not self.model_combobox:
            return

        # 辞書リストからファイル名のみを抽出
        model_values = [list(item.keys())[0] for item in model_data if item]

        # 辞書データを保持（画像パス取得で使用）
        self.model_data = model_data

        # コンボボックスの値を更新
        self.model_combobox["values"] = model_values

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
        if not hasattr(self, "model_data") or not self.model_data:
            return ""

        for model_dict in self.model_data:
            if model_name in model_dict:
                return model_dict[model_name]

        return ""
