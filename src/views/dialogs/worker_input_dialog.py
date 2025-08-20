"""
作業者入力ダイアログ
作業者番号の入力と登録を管理
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, Optional


class WorkerInputDialog:
    """作業者入力ダイアログ"""

    def __init__(self, parent: tk.Tk, worker_model=None):
        self.parent = parent
        self.worker_model = worker_model
        self.result = None
        self.dialog = None

        # 入力変数
        self.worker_input_var = tk.StringVar()

    def show(self) -> Optional[Dict[str, Any]]:
        """ダイアログを表示"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("作業者入力")
        self.dialog.geometry("350x260")
        self.dialog.resizable(False, False)

        # モーダルダイアログに設定
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # センタリング
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"350x260+{x}+{y}")

        self._setup_ui()

        # フォーカスを確実に入力フィールドに設定
        self.dialog.after(100, self._set_focus)  # 少し遅延させてフォーカス設定

        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()

        return self.result

    def _set_focus(self):
        """入力フィールドにフォーカスを設定"""
        if hasattr(self, "worker_entry") and self.worker_entry:
            self.worker_entry.focus_set()
            self.worker_entry.icursor(tk.END)  # カーソルを末尾に移動

    def _setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # タイトル
        title_label = tk.Label(
            main_frame, text="作業者番号を入力してください", font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)

        # 説明
        info_label = tk.Label(
            main_frame, text="既存の作業者番号または新しい番号を入力", font=("Arial", 9)
        )
        info_label.pack(pady=5)

        # 入力フレーム
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)

        tk.Label(input_frame, text="作業者番号:", font=("Arial", 10)).pack(anchor="w")

        self.worker_entry = tk.Entry(
            input_frame,
            textvariable=self.worker_input_var,
            font=("Arial", 12),
            width=20,
        )
        self.worker_entry.pack(fill=tk.X, pady=5)
        self.worker_entry.focus_set()

        # Enterキーでも入力確定できるようにバインド
        self.worker_entry.bind("<Return>", lambda event: self._on_ok())

        # 状態表示ラベル
        self.status_label = tk.Label(input_frame, text="", font=("Arial", 9), fg="gray")
        self.status_label.pack(anchor="w", pady=2)

        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # OKボタン
        ok_button = tk.Button(
            button_frame, text="OK", command=self._on_ok, font=("Arial", 10), width=10
        )
        ok_button.pack(side=tk.RIGHT, padx=5)

        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            font=("Arial", 10),
            width=10,
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)

        # イベントバインド
        self.worker_entry.bind("<Return>", lambda e: self._on_ok())
        self.worker_entry.bind("<Escape>", lambda e: self._on_cancel())
        self.worker_input_var.trace_add("write", self._on_input_changed)

        # ダイアログ閉じるイベント
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_input_changed(self, *args):
        """入力変更時の処理"""
        if not self.worker_model:
            return

        worker_input = self.worker_input_var.get().strip()

        if not worker_input:
            self.status_label.config(text="", fg="gray")
            return

        # 入力検証
        validation = self.worker_model.validate_worker_input(worker_input)

        if validation["valid"]:
            if validation["is_new"]:
                self.status_label.config(text="新規作業者として登録されます", fg="blue")
            else:
                self.status_label.config(
                    text=f"登録済み: {validation['worker_name']}", fg="green"
                )
        else:
            self.status_label.config(text=validation["message"], fg="red")

    def _on_ok(self):
        """OKボタン押下時の処理"""
        worker_input = self.worker_input_var.get().strip()

        if not worker_input:
            messagebox.showwarning("入力エラー", "作業者番号を入力してください。")
            return

        if self.worker_model:
            # 入力検証
            validation = self.worker_model.validate_worker_input(worker_input)

            if not validation["valid"]:
                messagebox.showerror("入力エラー", validation["message"])
                return

            # 新規作業者の場合は登録
            if validation["is_new"]:
                confirm = messagebox.askyesno(
                    "新規作業者登録",
                    f"作業者番号 '{worker_input}' を新規登録しますか？",
                )
                if not confirm:
                    return

                # 作業者を登録
                if not self.worker_model.add_worker(worker_input, worker_input):
                    messagebox.showerror("エラー", "作業者の登録に失敗しました。")
                    return

            # 現在の作業者として設定
            self.worker_model.current_worker_no = validation["worker_no"]

            self.result = {
                "worker_no": validation["worker_no"],
                "worker_name": validation["worker_name"],
                "is_new": validation["is_new"],
            }
        else:
            # worker_modelがない場合は入力値をそのまま返す
            self.result = {
                "worker_no": worker_input,
                "worker_name": worker_input,
                "is_new": True,
            }

        self.dialog.destroy()

    def _on_cancel(self):
        """キャンセルボタン押下時の処理"""
        self.result = None
        self.dialog.destroy()
