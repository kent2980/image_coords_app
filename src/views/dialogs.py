"""
Dialog Views
各種ダイアログビュー
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
from typing import Dict, Any, Optional, Callable
from datetime import datetime, date
import calendar


class WorkerInputDialog:
    """作業者入力ダイアログ"""
    
    def __init__(self, parent: tk.Tk, workers: Dict[str, str]):
        self.parent = parent
        self.workers = workers
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """ダイアログを表示して作業者番号を取得"""
        if not self.workers:
            messagebox.showerror("エラー", "worker.csvが見つからないか、作業者データがありません。")
            return None
        
        while True:
            worker_no = simpledialog.askstring(
                "作業者設定",
                "作業者Noを入力してください:",
                parent=self.parent
            )
            
            if worker_no is None:
                # キャンセルされた場合
                response = messagebox.askyesno(
                    "確認",
                    "作業者Noは必須です。\nアプリケーションを終了しますか？",
                    parent=self.parent
                )
                if response:
                    return None
                continue
            
            worker_no = worker_no.strip()
            if not worker_no:
                messagebox.showerror("エラー", "作業者Noを入力してください。", parent=self.parent)
                continue
            
            if worker_no in self.workers:
                return worker_no
            else:
                available_workers = "\n".join([f"{no}: {name}" for no, name in self.workers.items()])
                messagebox.showerror(
                    "エラー",
                    f"作業者No '{worker_no}' は存在しません。\n\n利用可能な作業者:\n{available_workers}",
                    parent=self.parent
                )


class SettingsDialog:
    """設定ダイアログ"""
    
    def __init__(self, parent: tk.Tk, current_settings: Dict[str, str], callback: Callable):
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.callback = callback
        self.dialog = None
        self.settings_changed = False
        
        # UI変数
        self.image_dir_var = tk.StringVar(value=current_settings.get('image_directory', ''))
        self.data_dir_var = tk.StringVar(value=current_settings.get('data_directory', ''))
        self.default_mode_var = tk.StringVar(value=current_settings.get('default_mode', '編集'))
    
    def show(self):
        """設定ダイアログを表示"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("設定")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 中央配置
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 画像ディレクトリ設定
        self._create_directory_setting(
            main_frame, "画像ディレクトリ:", 
            self.image_dir_var, self._select_image_directory, 0
        )
        
        # データディレクトリ設定
        self._create_directory_setting(
            main_frame, "データディレクトリ:", 
            self.data_dir_var, self._select_data_directory, 1
        )
        
        # デフォルトモード設定
        mode_frame = tk.Frame(main_frame)
        mode_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        tk.Label(mode_frame, text="デフォルトモード:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.default_mode_var,
            values=["編集", "閲覧"],
            state="readonly",
            width=10
        )
        mode_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        tk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            width=10
        ).pack(side=tk.LEFT)
    
    def _create_directory_setting(self, parent: tk.Frame, label_text: str, 
                                var: tk.StringVar, command: Callable, row: int):
        """ディレクトリ設定行を作成"""
        tk.Label(parent, text=label_text, font=("Arial", 10)).grid(
            row=row, column=0, sticky="w", pady=5
        )
        
        entry = tk.Entry(parent, textvariable=var, width=40)
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        tk.Button(
            parent, text="参照", command=command, width=8
        ).grid(row=row, column=2, pady=5)
        
        parent.grid_columnconfigure(1, weight=1)
    
    def _select_image_directory(self):
        """画像ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="画像ディレクトリを選択",
            initialdir=self.image_dir_var.get()
        )
        if directory:
            self.image_dir_var.set(directory)
    
    def _select_data_directory(self):
        """データディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="データディレクトリを選択",
            initialdir=self.data_dir_var.get()
        )
        if directory:
            self.data_dir_var.set(directory)
    
    def _on_ok(self):
        """OKボタンが押された時の処理"""
        # 設定が変更されたかチェック
        new_settings = {
            'image_directory': self.image_dir_var.get(),
            'data_directory': self.data_dir_var.get(),
            'default_mode': self.default_mode_var.get()
        }
        
        if new_settings != self.current_settings:
            self.settings_changed = True
            self.callback(new_settings)
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """キャンセルボタンが押された時の処理"""
        self.dialog.destroy()


class DateSelectDialog:
    """日付選択ダイアログ"""
    
    def __init__(self, parent: tk.Tk, current_date: date):
        self.parent = parent
        self.current_date = current_date
        self.selected_date = current_date
        self.dialog = None
        self.result = {'cancelled': True, 'date': None}
        
        # カレンダー変数
        self.year_var = tk.StringVar(value=str(current_date.year))
        self.month_var = tk.StringVar(value=str(current_date.month))
    
    def show(self) -> Dict[str, Any]:
        """日付選択ダイアログを表示"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("日付を選択")
        self.dialog.geometry("320x280")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 中央配置
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 100,
            self.parent.winfo_rooty() + 100
        ))
        
        self._create_widgets()
        
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
        
        return self.result
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 年月選択フレーム
        date_control_frame = tk.Frame(main_frame)
        date_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 年選択
        tk.Label(date_control_frame, text="年:", font=("Arial", 10)).pack(side=tk.LEFT)
        year_combo = ttk.Combobox(
            date_control_frame,
            textvariable=self.year_var,
            values=[str(y) for y in range(2020, 2031)],
            width=6,
            state="readonly"
        )
        year_combo.pack(side=tk.LEFT, padx=(5, 15))
        year_combo.bind('<<ComboboxSelected>>', self._on_date_changed)
        
        # 月選択
        tk.Label(date_control_frame, text="月:", font=("Arial", 10)).pack(side=tk.LEFT)
        month_combo = ttk.Combobox(
            date_control_frame,
            textvariable=self.month_var,
            values=[str(m) for m in range(1, 13)],
            width=4,
            state="readonly"
        )
        month_combo.pack(side=tk.LEFT, padx=(5, 0))
        month_combo.bind('<<ComboboxSelected>>', self._on_date_changed)
        
        # カレンダーフレーム
        self.calendar_frame = tk.Frame(main_frame)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self._create_calendar()
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            button_frame,
            text="今日",
            command=self._select_today,
            width=8
        ).pack(side=tk.LEFT)
        
        tk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            width=8
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            width=8
        ).pack(side=tk.RIGHT)
    
    def _create_calendar(self):
        """カレンダーを作成"""
        # 既存のカレンダーをクリア
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        year = int(self.year_var.get())
        month = int(self.month_var.get())
        
        # 曜日ヘッダー
        days = ['月', '火', '水', '木', '金', '土', '日']
        for i, day in enumerate(days):
            label = tk.Label(
                self.calendar_frame,
                text=day,
                font=("Arial", 9, "bold"),
                width=4,
                relief='raised'
            )
            label.grid(row=0, column=i, padx=1, pady=1)
        
        # カレンダーデータを取得
        cal = calendar.monthcalendar(year, month)
        
        # カレンダーボタンを作成
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day == 0:
                    # 空のセル
                    label = tk.Label(self.calendar_frame, text="", width=4, height=2)
                    label.grid(row=week_num, column=day_num, padx=1, pady=1)
                else:
                    # 日付ボタン
                    bg_color = 'lightblue' if (year, month, day) == (
                        self.selected_date.year, self.selected_date.month, self.selected_date.day
                    ) else 'white'
                    
                    button = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=4,
                        height=2,
                        bg=bg_color,
                        command=lambda d=day: self._select_date(year, month, d)
                    )
                    button.grid(row=week_num, column=day_num, padx=1, pady=1)
    
    def _on_date_changed(self, event=None):
        """年月が変更された時の処理"""
        self._create_calendar()
    
    def _select_date(self, year: int, month: int, day: int):
        """日付を選択"""
        try:
            self.selected_date = date(year, month, day)
            self._create_calendar()  # カレンダーを更新してハイライト表示
        except ValueError:
            pass  # 無効な日付の場合は無視
    
    def _select_today(self):
        """今日の日付を選択"""
        today = date.today()
        self.year_var.set(str(today.year))
        self.month_var.set(str(today.month))
        self.selected_date = today
        self._create_calendar()
    
    def _on_ok(self):
        """OKボタンが押された時の処理"""
        self.result = {'cancelled': False, 'date': self.selected_date}
        self.dialog.destroy()
    
    def _on_cancel(self):
        """キャンセルボタンが押された時の処理"""
        self.result = {'cancelled': True, 'date': None}
        self.dialog.destroy()
