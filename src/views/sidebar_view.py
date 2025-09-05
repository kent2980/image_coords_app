"""
サイドバービュー
座標詳細情報の表示と編集を管理
"""

from pathlib import Path
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional
import unicodedata


class SidebarView:
    """サイドバーを管理するビュー"""

    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame

        # 変数
        self.item_number_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        self.defect_var = tk.StringVar()
        self.serial_var = tk.StringVar()

        # ロット番号（表示用）
        self.current_lot_number = ""

        # 製番（表示用）
        self.current_product_number = ""

        # 作業者番号（表示用）
        self.current_worker_no = ""

        # 現在の基盤番号（表示用）
        self.current_board_number = 1

        # UI要素の参照
        self.item_entry = None
        self.reference_entry = None
        self.defect_combobox = None
        self.comment_text = None
        self.worker_label = None
        self.lot_label = None
        self.product_label = None
        self.board_label = None

        # コールバック関数
        self.callbacks: Dict[str, Callable] = {}

        # CoordinateControllerへの参照（自動保存用）
        self.coordinate_controller = None

        # 不良項目リスト（デフォルト）
        self.defect_items = [
            "ズレ",
            "裏",
            "飛び",
            "傷",
            "汚れ",
            "欠け",
            "変色",
            "寸法不良",
            "形状不良",
            "その他",
        ]

        # 読み取り専用モード
        self.readonly_mode = False

        self._setup_sidebar()

    def set_item_number(self, value: str):
        """item_number_varの値を設定"""
        self.item_number_var.set(value)

    def set_reference(self, value: str):
        """reference_varの値を設定"""
        self.reference_var.set(value)

    def set_defect(self, value: str):
        """defect_varの値を設定"""
        self.defect_var.set(value)

    def set_serial(self, value: str):
        """serial_varの値を設定"""
        self.serial_var.set(value)

    def set_comment(self, value: str):
        """コメントテキストフィールドの値を設定"""
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert("1.0", value)

    def clear_comment(self):
        """コメントテキストフィールドを初期化"""
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.delete("1.0", tk.END)

    def get_comment(self) -> str:
        """コメントテキストフィールドの値を取得"""
        if hasattr(self, "comment_text") and self.comment_text:
            return self.comment_text.get("1.0", tk.END).strip()
        return ""

    def set_repaired(self, value: str):
        """repaired_varの値を設定"""
        if hasattr(self, "repaired_var"):
            self.repaired_var.set(value)

    def get_repaired(self) -> str:
        """repaired_varの値を取得"""
        if hasattr(self, "repaired_var"):
            return self.repaired_var.get()
        return "いいえ"

    def get_item_number(self) -> int:
        """item_number_varの値を取得"""
        return int(self.item_number_var.get()) if self.item_number_var.get().isdigit() else 0

    def get_reference(self) -> str:
        """reference_varの値を取得"""
        return self.reference_var.get()

    def get_defect(self) -> str:
        """defect_varの値を取得"""
        return self.defect_var.get()

    def get_serial(self) -> str:
        """serial_varの値を取得"""
        return self.serial_var.get()

    def _setup_sidebar(self):
        """サイドバーUIを設定"""
        # サイドバーのスタイル設定（旧コードと一致）
        self.parent_frame.config(bg="#f5f5f5", relief="ridge", bd=1)

        # タイトル
        title_label = tk.Label(
            self.parent_frame,
            text="不良詳細情報",
            font=("Arial", 14, "bold"),
            bg="#f5f5f5",
            fg="#333333",
        )
        title_label.pack(pady=(15, 20))

        # 区切り線
        separator5 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator5.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 作業者フィールドを作成
        self.worker_label = self._create_info_field("作業者: ", "未設定")

        # 区切り線
        separator1 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator1.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 製番フィールドを作成
        self.product_label = self._create_info_field("品目コード: ", "未設定")

        # ロット番号フィールドを作成
        self.lot_label = self._create_info_field("指図: ", "未設定")

        # 区切り線
        separator1 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator1.pack(fill=tk.X, padx=15, pady=(0, 15))

        # 基板番号とアイテム番号フィールドを作成（横並び）
        self.board_label, self.item_entry = self._create_dual_info_field(
            "基板No: ", "1", "#555555", "座標No: ", "1", "#555555"
        )

        # 区切り線
        separator4 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator4.pack(fill=tk.X, padx=15, pady=(0, 15))

        # リファレンス
        self.reference_entry = self._create_styled_input_field(
            "Rf", self.reference_var, width=15
        )

        # リファレンス入力フィールドにEnterキーのバインド
        self.reference_entry.bind("<Return>", self._on_entry_return)
        # リファレンス入力フィールドに入力があるたびに呼ばれる
        self.reference_entry.bind("<KeyRelease>", self.to_ref_halfwidth)

        # 不良名
        self.defect_combobox = self._create_defect_selection()

        # 不良名入力フィールドの値が変更されたら
        self.defect_combobox.bind("<<ComboboxSelected>>", self._on_defect_selected)

        # 区切り線
        separator3 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))

        # シリアル番号
        self.serial_entry = self._create_styled_input_field(
            "シリアル", self.serial_var, width=15
        )

        # シリアル番号入力フィールドにEnterキーのバインド
        self.serial_entry.bind("<Return>", self._on_entry_return)

        # 区切り線
        separator3 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))

        # 修理済み
        self._create_repaired_selection()

        # 区切り線
        separator3 = tk.Frame(self.parent_frame, height=1, bg="#cccccc")
        separator3.pack(fill=tk.X, padx=15, pady=(15, 10))

        # コメント
        self._create_comment_field()

        # コメント入力フィールドにEnterキーのバインド
        self.comment_text.bind("<Return>", self._on_entry_return)

    def to_ref_halfwidth(self, event):
        print("[DEBUG] to_ref_halfwidth")
        text = self.reference_entry.get()
        print(text)
        # 全角を半角に変換
        half = unicodedata.normalize("NFKC", text)
        # 小文字を大文字に変換
        half = half.upper()
        if text != half:
            self.reference_entry.delete(0, tk.END)
            self.reference_entry.insert(0, half)

    def _on_entry_return(self, event: tk.Event):
        """エンターキーが押されたときの処理"""
        # コントローラーのコールバックを呼び出し
        if "on_entry_return" in self.callbacks:
            self.callbacks["on_entry_return"](event)

    def _on_defect_selected(self, event: tk.Event):
        """不良名が選択されたときの処理"""
        # コントローラーのコールバックを呼び出し
        if "on_defect_selected" in self.callbacks:
            self.callbacks["on_defect_selected"](event)

    def _create_info_field(
        self, title_text: str, value_text: str, fg_color: str = "#555555"
    ) -> tk.Label:
        """情報表示フィールドを作成（横並び）"""
        # フレーム作成
        info_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 5))

        # タイトルラベル
        title_label = tk.Label(
            info_frame,
            text=title_text,
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
        )
        title_label.pack(side=tk.LEFT)

        # 値ラベル
        value_label = tk.Label(
            info_frame,
            text=value_text,
            font=("Arial", 14, "bold"),
            bg="#f5f5f5",
            fg=fg_color,
            anchor="w",
        )
        value_label.pack(side=tk.LEFT)

        return value_label

    def _create_dual_info_field(
        self,
        title1_text: str,
        value1_text: str,
        fg1_color: str,
        title2_text: str,
        value2_text: str,
        fg2_color: str,
    ) -> tuple[tk.Label, tk.Label]:
        """2つの情報表示フィールドを横並びで作成"""
        # フレーム作成
        info_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        info_frame.pack(fill=tk.X, padx=15, pady=(0, 5))

        # 左側の情報フィールド
        left_frame = tk.Frame(info_frame, bg="#f5f5f5")
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 左側タイトルラベル
        title1_label = tk.Label(
            left_frame,
            text=title1_text,
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
        )
        title1_label.pack(side=tk.LEFT)

        # 左側値ラベル
        value1_label = tk.Label(
            left_frame,
            text=value1_text,
            font=("Arial", 14, "bold"),
            bg="#f5f5f5",
            fg=fg1_color,
            anchor="w",
        )
        value1_label.pack(side=tk.LEFT)

        # 右側の情報フィールド
        right_frame = tk.Frame(info_frame, bg="#f5f5f5")
        right_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # 右側タイトルラベル
        title2_label = tk.Label(
            right_frame,
            text=title2_text,
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
        )
        title2_label.pack(side=tk.LEFT)

        # 右側値ラベル
        value2_label = tk.Label(
            right_frame,
            text=value2_text,
            font=("Arial", 14, "bold"),
            bg="#f5f5f5",
            fg=fg2_color,
            anchor="w",
        )
        value2_label.pack(side=tk.LEFT)

        return value1_label, value2_label

    def _create_styled_input_field(
        self, label_text, variable, width=15, readonly=False
    ):
        """スタイル付きの入力フィールドを作成"""
        # メインフレーム
        main_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        main_frame.pack(fill=tk.X, padx=15, pady=8)

        # ラベル
        label = tk.Label(
            main_frame,
            text=label_text,
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
            width=7,  # ラベルの幅を調整
        )
        label.pack(side=tk.LEFT, pady=(0, 3))

        # 入力フィールド
        entry_state = "readonly" if readonly else "normal"
        entry_bg = "#f0f0f0" if readonly else "white"

        entry = tk.Entry(
            main_frame,
            textvariable=variable,
            width=width,
            font=("Arial", 14),
            relief="solid",
            bd=1,
            highlightthickness=1,
            state=entry_state,
            justify="center",
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 英数字を大文字に変換するバインド
        if entry_state == "normal":
            entry.bind(
                "<KeyRelease>",
                lambda event: self._convert_to_uppercase(event, variable),
            )
            # 英数入力に固定（IME無効化）
            entry.bind("<FocusIn>", self._set_alphanumeric_mode)
            entry.bind("<Button-1>", self._set_alphanumeric_mode)

            # Windows環境での追加設定
            import platform

            if platform.system() == "Windows":
                # WindowsでのIME制御を強化
                entry.configure(
                    validate="key",
                    validatecommand=(
                        self.parent_frame.register(self._validate_alphanumeric),
                        "%P",
                    ),
                )

        return entry

    def _create_defect_selection(self) -> ttk.Combobox:
        """不良名選択フィールドを作成"""
        # メインフレーム
        defect_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        defect_frame.pack(fill=tk.X, padx=15, pady=8)

        # ラベル
        label = tk.Label(
            defect_frame,
            text="不良名",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
            width=7,
        )
        label.pack(side=tk.LEFT, pady=(0, 3))

        defect_combobox = ttk.Combobox(
            defect_frame,
            textvariable=self.defect_var,
            values=self.defect_items,
            state="readonly",
            font=("Arial", 14),
            justify="center",
        )
        defect_combobox.pack(side=tk.LEFT, fill=tk.X)

        # 初期値は空に設定 
        self.defect_var.set("")

        return defect_combobox

    def _create_repaired_selection(self):
        """修理済み選択フィールドを作成"""
        self.repaired_var = tk.StringVar(value="いいえ")

        # メインフレーム
        repaired_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        repaired_frame.pack(fill=tk.X, padx=15, pady=8)

        # ラベル
        label = tk.Label(
            repaired_frame,
            text="修理済み",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
        )
        label.pack(fill=tk.X, pady=(0, 5))

        # ラジオボタンフレーム
        radio_frame = tk.Frame(repaired_frame, bg="#f5f5f5")
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
        comment_frame = tk.Frame(self.parent_frame, bg="#f5f5f5")
        comment_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

        # ラベル
        label = tk.Label(
            comment_frame,
            text="コメント",
            font=("Arial", 10, "bold"),
            bg="#f5f5f5",
            fg="#555555",
            anchor="w",
        )
        label.pack(fill=tk.X, pady=(0, 3))

        # テキストフィールドとスクロールバーのフレーム
        text_frame = tk.Frame(comment_frame, bg="#f5f5f5")
        text_frame.pack(fill=tk.BOTH, expand=True)

        # テキストフィールド
        self.comment_text = tk.Text(
            text_frame,
            height=8,
            font=("Arial", 14),
            relief="solid",
            bd=1,
            highlightthickness=1,
            wrap=tk.WORD,
        )
        self.comment_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # コメントフィールドはかな入力モードに設定
        self.comment_text.bind("<FocusIn>", self._set_kana_mode)
        self.comment_text.bind("<Button-1>", self._set_kana_mode)

        # スクロールバー
        scrollbar = tk.Scrollbar(text_frame, command=self.comment_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.comment_text.config(yscrollcommand=scrollbar.set)

        # 変更イベントバインド
        self._bind_change_events()

    def _convert_to_uppercase(self, event, variable):
        """入力文字を大文字に変換"""
        current_value = variable.get()
        upper_value = current_value.upper()
        if current_value != upper_value:
            # カーソル位置を保存
            cursor_pos = event.widget.index(tk.INSERT)
            # 大文字に変換
            variable.set(upper_value)
            # カーソル位置を復元
            event.widget.icursor(cursor_pos)

    def _validate_alphanumeric(self, value):
        """英数字のみを許可する検証関数（Windows用）"""
        import re

        # 英数字、ハイフン、アンダースコアのみを許可
        return re.match(r"^[A-Za-z0-9\-_]*$", value) is not None

    def _set_alphanumeric_mode(self, event):
        """入力フィールドを英数入力モードに設定"""
        try:
            import platform
            import subprocess

            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to key code 102',
                    ],
                    check=False,
                    capture_output=True,
                )
            elif system == "Windows":  # Windows
                # WindowsでIMEを英数モードに切り替え
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Add-Type -AssemblyName System.Windows.Forms; "
                        "[System.Windows.Forms.SendKeys]::SendWait('^{F10}')",
                    ],
                    check=False,
                    capture_output=True,
                )
        except Exception:
            # エラーが発生しても無視（IME切り替えは補助的な機能）
            pass

    def _set_kana_mode(self, event):
        """入力フィールドをかな入力モードに設定"""
        try:
            import platform
            import subprocess

            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to key code 104',
                    ],
                    check=False,
                    capture_output=True,
                )
            elif system == "Windows":  # Windows
                # WindowsでIMEをひらがなモードに切り替え
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Add-Type -AssemblyName System.Windows.Forms; "
                        "[System.Windows.Forms.SendKeys]::SendWait('^{F7}')",
                    ],
                    check=False,
                    capture_output=True,
                )
        except Exception:
            # エラーが発生しても無視（IME切り替えは補助的な機能）
            pass

    def _bind_change_events(self):
        """変更イベントをバインド"""
        # 各入力フィールドの変更を監視
        self.reference_var.trace_add("write", self._on_data_changed)
        self.defect_var.trace_add("write", self._on_data_changed)
        if hasattr(self, "repaired_var"):
            self.repaired_var.trace_add("write", self._on_data_changed)

        # コメントフィールドの変更を監視
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.bind("<KeyRelease>", self._on_comment_changed)
            self.comment_text.bind("<FocusOut>", self._on_comment_changed)

    def _on_data_changed(self, *args):
        """データ変更時のコールバック"""
        if "on_form_data_changed" in self.callbacks:
            self.callbacks["on_form_data_changed"]()

        # 座標詳細情報の自動保存
        self._auto_save_coordinate_detail(self.current_lot_number)

    def _on_comment_changed(self, event=None):
        """コメントフィールド変更時のコールバック"""
        # 座標詳細情報の自動保存
        self._auto_save_coordinate_detail(self.current_lot_number)

    def _auto_save_coordinate_detail(self, lot_number: str):
        """座標詳細情報を自動保存"""
        try:
            # CoordinateControllerが設定されていない場合は何もしない
            if not self.coordinate_controller:
                return

            # 現在のフォームデータを取得
            detail = self.get_coordinate_detail(self.current_lot_number, self.current_board_number)

            # CoordinateControllerを通じて詳細情報を更新（自動保存も実行される）
            self.coordinate_controller.update_current_coordinate_detail(detail)

        except Exception as e:
            print(f"[ERROR] 座標詳細自動保存エラー: {e}")
            import traceback

            traceback.print_exc()

    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self.callbacks.update(callbacks)

    def set_coordinate_controller(self, coordinate_controller) -> None:
        """CoordinateControllerを設定"""
        self.coordinate_controller = coordinate_controller

    def set_readonly_mode(self, readonly: bool):
        """読み取り専用モードを設定"""
        self.readonly_mode = readonly

        state = tk.DISABLED if readonly else tk.NORMAL

        # 入力フィールドの状態を設定
        if hasattr(self, "reference_entry") and self.reference_entry:
            self.reference_entry.config(state=state)

        # コンボボックス
        combo_state = "disabled" if readonly else "readonly"
        if hasattr(self, "defect_combobox") and self.defect_combobox:
            self.defect_combobox.config(state=combo_state)

        # ラジオボタンの状態を設定
        if hasattr(self, "repaired_yes") and hasattr(self, "repaired_no"):
            radio_state = tk.DISABLED if readonly else tk.NORMAL
            self.repaired_yes.config(state=radio_state)
            self.repaired_no.config(state=radio_state)

        # コメントフィールドの状態を設定
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.config(state=state)

    def update_model_options(self, models: List[str]):
        """モデル選択肢を更新 - MVCでは使用しない"""
        pass

    def update_defect_options(self, defects: List[str]):
        """不良項目選択肢を更新"""
        self.defect_items = defects
        if hasattr(self, "defect_combobox") and self.defect_combobox:
            self.defect_combobox["values"] = defects

    def clear_form(self):
        """フォームをクリア"""
        self.item_number_var.set("")
        self.reference_var.set("")
        self.defect_var.set("")
        if hasattr(self, "repaired_var"):
            self.repaired_var.set("いいえ")

        # コメントフィールドをクリア
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.delete("1.0", tk.END)

    def set_coordinate_detail(self, detail: Dict[str, Any]):
        """座標詳細情報を設定"""
        self.item_number_var.set(detail.get("item_number", ""))
        self.reference_var.set(detail.get("reference", ""))
        self.defect_var.set(detail.get("defect", ""))

        # 修理済み情報を設定
        if hasattr(self, "repaired_var"):
            self.repaired_var.set(detail.get("repaired", "いいえ"))

        print(f"Setting comment: {detail.get('comment', '')}")

        # コメント情報を設定
        if hasattr(self, "comment_text") and self.comment_text:
            self.comment_text.delete("1.0", tk.END)
            self.comment_text.insert("1.0", detail.get("comment", ""))

    def get_coordinate_detail(self, lot_number: str, board_number: int) -> Dict[str, Any]:
        """座標詳細情報を取得"""

        detail = {
            "lot_number": lot_number,
            "board_number": board_number,
            "count_number": self.get_item_number(),
            "reference": self.reference_var.get(),
            "defect": self.defect_var.get(),
        }

        # コメント情報を追加
        if hasattr(self, "comment_text") and self.comment_text:
            detail["comment"] = self.comment_text.get("1.0", tk.END).strip()

        return detail

    def get_form_data(self) -> Dict[str, Any]:
        """全フォームデータを取得（MVCでは座標詳細のみ）"""
        return self.get_coordinate_detail(self.current_lot_number, self.current_board_number)

    def set_form_data(self, data: Dict[str, Any]):
        """フォームデータを設定（MVCでは座標詳細のみ）"""
        self.set_coordinate_detail(data)

    def focus_reference_entry(self):
        """リファレンス入力フィールドにフォーカス"""
        if (
            hasattr(self, "reference_entry")
            and self.reference_entry
            and not self.readonly_mode
        ):
            self.reference_entry.focus_set()

    def update_worker_label(self, worker_text: str):
        """作業者ラベルを更新"""
        if hasattr(self, "worker_label") and self.worker_label:
            self.worker_label.config(text=worker_text)

    def get_selected_model(self) -> str:
        """選択されているモデル名を取得"""
        # MVCではメインビューのモデル選択から取得
        if hasattr(self, "main_view_ref") and self.main_view_ref:
            return self.main_view_ref.get_selected_model()
        return ""

    def set_main_view_reference(self, main_view):
        """MainViewの参照を設定"""
        self.main_view_ref = main_view

    def set_save_name(self, save_name: str):
        """保存名を設定"""
        # MVCではメインビューの保存名フィールドに設定
        if hasattr(self, "main_view_ref") and self.main_view_ref:
            self.main_view_ref.set_save_name(save_name)

    def get_save_name(self) -> str:
        """保存名を取得"""
        # MVCではメインビューの保存名フィールドから取得
        if hasattr(self, "main_view_ref") and self.main_view_ref:
            return self.main_view_ref.get_save_name()
        return ""

    def update_lot_label(self, lot_text: str):
        """ロット番号ラベルを更新"""
        if hasattr(self, "lot_label") and self.lot_label:
            self.lot_label.config(text=lot_text)

    def set_lot_number(self, lot_number: str):
        """ロット番号を設定"""
        self.current_lot_number = lot_number
        if hasattr(self, "lot_label") and self.lot_label:
            self.lot_label.config(text=lot_number)

    def set_product_number(self, product_number: str):
        """製番を設定"""
        self.current_product_number = product_number
        if hasattr(self, "product_label") and self.product_label:
            self.product_label.config(text=product_number)

    def get_product_number(self) -> str:
        """製番を取得"""
        return self.current_product_number

    def get_lot_number(self) -> str:
        """ロット番号を取得"""
        return self.current_lot_number

    def clear_lot_number(self):
        """ロット番号をクリア（モデル変更時用）"""
        self.current_lot_number = ""
        if hasattr(self, "lot_label") and self.lot_label:
            self.lot_label.config(text="未設定")

    def get_worker_no(self) -> str:
        """作業者番号を取得"""
        return self.current_worker_no

    def set_worker_no(self, worker_no: str):
        """作業者番号を設定"""
        self.current_worker_no = worker_no

    def set_board_label(self, board_number: int):
        """基盤番号表示を更新"""
        self.current_board_number = board_number
        if hasattr(self, "board_label") and self.board_label:
            self.board_label.config(text=board_number)

    def set_item_entry(self, item_entry: int):
        """アイテム番号を設定"""
        self.current_item_entry = item_entry
        if hasattr(self, "item_entry") and self.item_entry:
            self.item_entry.config(text=item_entry)

    def get_current_board_number(self) -> int:
        """現在の基盤番号を取得"""
        return self.current_board_number

    def display_coordinate_info(self, detail: Dict[str, Any], index: int):
        """座標詳細情報を表示（閲覧モード用）"""
        # 座標詳細情報を設定
        self.set_coordinate_detail(detail)

        # 項目番号を表示
        if "item_number" not in detail:
            detail_with_item = detail.copy()
            detail_with_item["item_number"] = str(index + 1)
            self.set_coordinate_detail(detail_with_item)

    def display_coordinate_summary(self, summary: Dict[str, Any]):
        """座標概要情報を表示（閲覧モード用）"""
        # 概要情報に基づいてフォームをクリア
        self.clear_form()

        # 概要情報があれば表示（現在は特別な処理なし）
        # 必要に応じて将来的に概要情報の表示機能を追加

    def change_sidebar_board_label(self, data_file_path: Path):
        """ロットナンバー変更処理"""
        # data_file_pathからファイル名を取得
        file_name = data_file_path.name.split(".")[0]
        # ファイル名からインデックス番号を取得
        data_index = int(file_name)
        # サイドバーの基板番号を変更
        self.set_board_label(data_index)
        # その他項目を初期化
        self.set_defect("")
        self.set_reference("")
        self.set_serial("")
        self.clear_comment()
        self.set_repaired("いいえ")