"""
メインビュー（ttkbootstrap版）
アプリケーションのメインウィンドウを管理
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime
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
    delete_file: CallbackProtocol

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
    save_all_boards: CallbackProtocol
    load_board_session: CallbackProtocol


class MainView:
    """メインビューを管理するクラス（ttkbootstrap版）"""

    def __init__(self, root: ttk.Window):
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
        self.mode_var = ttk.StringVar(value="編集")
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
        self.save_name_var = ttk.StringVar(value="")

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
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=YES)

        # コンテンツフレーム
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=BOTH, expand=YES)

        # サイドバーフレーム（左側）
        self.sidebar_frame = ttk.Frame(
            self.content_frame, 
            width=self.SIDEBAR_WIDTH,
            bootstyle="light"
        )
        self.sidebar_frame.pack(side=LEFT, fill=Y, padx=5, pady=5)
        self.sidebar_frame.pack_propagate(False)

        # コンテンツヘッダーフレーム（右側上部）
        self.content_header_frame = ttk.Frame(
            self.content_frame, 
            height=40,
            bootstyle="light"
        )
        self.content_header_frame.pack(fill=X, padx=5, pady=5)
        self.content_header_frame.pack_propagate(False)

        # キャンバス上段フレーム
        self.canvas_top_frame = ttk.Frame(
            self.content_frame, 
            height=35,
            bootstyle="light"
        )
        self.canvas_top_frame.pack(fill=X, pady=(0, 5))
        self.canvas_top_frame.pack_propagate(False)

        # canvas_top_frameにコントロールを設定
        self._setup_canvas_top_controls()

        # メニューボタンフレーム（最上部に配置 - 旧コードと同じ位置）
        self.menu_frame = ttk.Frame(self.content_frame, bootstyle="light")
        self.menu_frame.pack(fill=X, padx=5, pady=5)

        # キャンバスフレーム
        self.canvas_frame = ttk.Frame(
            self.content_frame, 
            relief="sunken", 
            borderwidth=3,
            bootstyle="secondary"
        )
        self.canvas_frame.pack(
            side=RIGHT, fill=BOTH, expand=YES, padx=30, pady=30
        )

    def setup_menu_frame(self):
        """メニューフレームを設定"""

        # メインメニュー
        self.root.option_add('*tearOff', False)

        # ファイルメニューボタン
        file_menu_btn = ttk.Menubutton(
            self.menu_frame, 
            text="ファイル",
            bootstyle="outline-primary"
        )
        file_menu_btn.pack(side=LEFT, padx=2)
        
        file_menu = ttk.Menu(file_menu_btn)
        file_menu_btn["menu"] = file_menu
        
        file_menu.add_command(label="開く", command=self.get_callback("open_file"))
        file_menu.add_command(label="保存", command=self.get_callback("save_file"))
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.get_callback("exit_app"))

        # 編集メニューボタン
        edit_menu_btn = ttk.Menubutton(
            self.menu_frame, 
            text="編集",
            bootstyle="outline-primary"
        )
        edit_menu_btn.pack(side=LEFT, padx=2)
        
        edit_menu = ttk.Menu(edit_menu_btn)
        edit_menu_btn["menu"] = edit_menu
        
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

        # 基盤メニューボタン
        board_menu_btn = ttk.Menubutton(
            self.menu_frame, 
            text="基盤",
            bootstyle="outline-primary"
        )
        board_menu_btn.pack(side=LEFT, padx=2)
        
        board_menu = ttk.Menu(board_menu_btn)
        board_menu_btn["menu"] = board_menu
        
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
        settings_frame = ttk.Frame(self.content_header_frame)
        settings_frame.pack(side=RIGHT, padx=15, pady=5)

        self.settings_button = ttk.Button(
            settings_frame,
            text="⚙ 設定",
            command=self.get_callback("open_settings"),
            bootstyle="info-outline"
        )
        self.settings_button.pack()

        # モード選択
        mode_frame = ttk.Frame(self.content_header_frame)
        mode_frame.pack(side=RIGHT, padx=5, pady=5)

        ttk.Label(
            mode_frame, 
            text="モード:", 
            font=("Arial", 10),
            bootstyle="secondary"
        ).pack(side=LEFT)

        mode_edit = ttk.Radiobutton(
            mode_frame,
            text="編集",
            variable=self.mode_var,
            value="編集",
            command=self.get_callback("on_mode_change"),
            bootstyle="success-toolbutton"
        )
        mode_edit.pack(side=LEFT, padx=5)

        mode_view = ttk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.mode_var,
            value="閲覧",
            command=self.get_callback("on_mode_change"),
            bootstyle="info-toolbutton"
        )
        mode_view.pack(side=LEFT, padx=5)

    def _setup_canvas_top_controls(self):
        """キャンバス上段エリアをセットアップ（編集モード用）"""
        # グリッドレイアウトの設定
        self.canvas_top_frame.grid_columnconfigure(0, weight=0)
        self.canvas_top_frame.grid_columnconfigure(1, weight=1)
        self.canvas_top_frame.grid_columnconfigure(2, weight=0)
        self.canvas_top_frame.grid_columnconfigure(3, weight=0)
        self.canvas_top_frame.grid_columnconfigure(4, weight=0)
        self.canvas_top_frame.grid_rowconfigure(0, weight=1)

        # モデル選択フレーム
        ttk.Label(
            self.canvas_top_frame, 
            text="モデル:", 
            font=("Arial", 10),
            bootstyle="secondary"
        ).grid(row=0, column=0, padx=5, pady=5, sticky=W)

        self.model_var = ttk.StringVar()
        self.model_combobox = ttk.Combobox(
            self.canvas_top_frame,
            textvariable=self.model_var,
            state=READONLY,
            width=50,
            bootstyle="primary"
        )
        self.model_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        # モデル選択時のイベントをバインド
        self.model_combobox.bind("<<ComboboxSelected>>", self._on_model_selected)

        # ロット番号入力エリア
        ttk.Label(
            self.canvas_top_frame, 
            text="指図:", 
            font=("Arial", 10),
            bootstyle="secondary"
        ).grid(row=0, column=2, padx=5, pady=5, sticky=W)
        
        self.lot_number_var = ttk.StringVar()
        self.lot_number_entry = ttk.Entry(
            self.canvas_top_frame,
            textvariable=self.lot_number_var,
            width=20,
            bootstyle="primary"
        )
        self.lot_number_entry.grid(row=0, column=3, padx=5, pady=5, sticky=EW)

        # Enterキーで保存処理を実行
        self.lot_number_entry.bind("<Return>", self._on_lot_number_enter)

        # 「現品票で切り替え」ボタン
        print(f"[DEBUG] 現品票切り替えボタンを作成中...")
        print(
            f"[DEBUG] コールバック 'on_item_tag_change': {self.get_callback('on_item_tag_change')}"
        )

        self.item_tag_change_button = ttk.Button(
            self.canvas_top_frame,
            text="現品票で切り替え",
            command=self.get_callback("on_item_tag_change"),
            bootstyle="warning-outline"
        )
        self.item_tag_change_button.grid(row=0, column=4, padx=5, pady=5, sticky=EW)

        print(
            f"[DEBUG] 現品票切り替えボタンが作成されました: {self.item_tag_change_button}"
        )

        # ボタンのコマンドをテスト
        def test_button_click():
            print("[DEBUG] 現品票切り替えボタンがクリックされました")

        # デバッグ用に直接コールバック関数を設定
        if not self.has_callback("on_item_tag_change"):
            print("[DEBUG] on_item_tag_change コールバックが未設定です")

    def initialize_models(self):
        """モデル選択肢を初期化（旧コード互換機能）"""
        if self.has_callback("load_models_from_file"):
            self.callbacks["load_models_from_file"]()

    def set_callbacks(self, callbacks: CallbackTypes):
        """コールバック関数を設定"""
        print(
            f"[DEBUG] set_callbacks が呼び出されました: {len(callbacks)}個のコールバック"
        )
        for key in callbacks:
            print(f"[DEBUG] コールバック設定: {key}")

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
                cmd = self.get_callback("on_item_tag_change")
                if cmd:
                    self.item_tag_change_button.configure(command=cmd)
                    print(f"[DEBUG] 現品票切り替えボタンのコマンドを更新しました: {cmd}")
        except Exception as e:
            print(f"[ERROR] ボタンコマンド更新エラー: {e}")

    def update_date_label(self, date_str: str):
        """日付ラベルを更新"""
        if self.date_label:
            self.date_label.configure(text=date_str)

    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Undo/Redoボタンの状態を更新"""
        if self.undo_button:
            state = NORMAL if can_undo else DISABLED
            self.undo_button.configure(state=state)
        if self.redo_button:
            state = NORMAL if can_redo else DISABLED
            self.redo_button.configure(state=state)

    def get_current_mode(self) -> str:
        """現在のモードを取得"""
        return self.mode_var.get()

    def set_mode(self, mode: str):
        """モードを設定"""
        self.mode_var.set(mode)

    def update_model_combobox(self, models: list):
        """モデル選択肢を更新"""
        if hasattr(self, "model_combobox"):
            self.model_combobox.configure(values=models)

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
            values = self.model_combobox["values"]
            if model in values:
                self.model_combobox.current(values.index(model))

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
            self.coordinate_number_label.configure(text=text)

    def update_coordinate_number_display(self, current_index: int, total_count: int):
        """座標番号表示を更新（例：1/5）"""
        if total_count > 0:
            display_text = f"{current_index + 1}/{total_count}"
        else:
            display_text = "0/0"
        self.set_coordinate_number_text(display_text)
        
        # デバッグログ出力
        print(f"[DEBUG] 座標番号表示更新: {display_text} (index: {current_index}, total: {total_count})")

    def show_message(self, message: str, title: str = "情報"):
        """情報メッセージを表示"""
        Messagebox.show_info(message, title, parent=self.root)

    def show_error(self, message: str, title: str = "エラー"):
        """エラーメッセージを表示"""
        Messagebox.show_error(message, title, parent=self.root)

    def show_warning(self, message: str, title: str = "警告"):
        """警告メッセージを表示"""
        Messagebox.show_warning(message, title, parent=self.root)

    def show_confirmation_dialog(self, message: str, title: str = "確認") -> bool:
        """確認ダイアログを表示"""
        result = Messagebox.show_question(message, title, parent=self.root)
        return result == "Yes"

    def show_item_tag_switch_dialog(self):
        """現品票切り替えダイアログを表示"""
        # カスタムダイアログの実装
        dialog = ttk.Toplevel(self.root)
        dialog.title("現品票で切り替え")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ダイアログの中央配置
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # ダイアログコンテンツ
        ttk.Label(
            dialog, 
            text="現品票情報を入力してください",
            font=("Arial", 12, "bold"),
            bootstyle="primary"
        ).pack(pady=20)
        
        # 入力フィールド
        input_frame = ttk.Frame(dialog)
        input_frame.pack(padx=20, pady=10, fill=X)
        
        ttk.Label(input_frame, text="現品票番号:").pack(anchor=W)
        tag_entry = ttk.Entry(input_frame, width=30, bootstyle="primary")
        tag_entry.pack(fill=X, pady=(5, 15))
        
        # ボタンフレーム
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_ok():
            tag_number = tag_entry.get().strip()
            if tag_number:
                # ここで現品票切り替え処理を実行
                print(f"[DEBUG] 現品票切り替え: {tag_number}")
                dialog.destroy()
            else:
                self.show_warning("現品票番号を入力してください")
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(
            button_frame, 
            text="OK", 
            command=on_ok,
            bootstyle="success"
        ).pack(side=LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="キャンセル", 
            command=on_cancel,
            bootstyle="secondary"
        ).pack(side=LEFT, padx=10)
        
        # Enterキーでも実行
        tag_entry.bind("<Return>", lambda e: on_ok())
        tag_entry.focus_set()

    def _on_model_selected(self, event=None):
        """モデル選択時のイベントハンドラー"""
        if self.has_callback("on_model_selected"):
            self.callbacks["on_model_selected"]()

    def _on_lot_number_enter(self, event):
        """ロット番号入力フィールドでEnterキーが押された時の処理"""
        if self.has_callback("on_lot_number_save"):
            self.callbacks["on_lot_number_save"]()

    def get_form_data(self) -> Dict[str, Any]:
        """フォームデータを取得"""
        return {
            "model": self.get_model(),
            "lot_number": self.get_lot_number(),
            "mode": self.get_current_mode(),
            "save_name": self.get_save_name()
        }

    def update_model_options(self, model_data: List[Dict[str, str]]):
        """モデル選択肢を更新"""
        model_names = [model.get("name", "") for model in model_data]
        self.update_model_combobox(model_names)

    def get_model_image_path(self, model_name: str) -> str:
        """モデル名から画像パスを取得"""
        # この機能は別途実装が必要
        return ""
