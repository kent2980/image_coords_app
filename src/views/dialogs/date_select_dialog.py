"""
日付選択ダイアログ
日付の選択を管理
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from typing import Optional


class DateSelectDialog:
    """日付選択ダイアログ"""
    
    def __init__(self, parent: tk.Tk, current_date: Optional[date] = None):
        self.parent = parent
        self.current_date = current_date or date.today()
        self.selected_date = self.current_date
        self.result = None
        self.dialog = None
        
        # 年月日変数
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.day_var = tk.StringVar()
    
    def show(self) -> Optional[dict]:
        """ダイアログを表示"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("日付選択")
        self.dialog.geometry("300x150")
        self.dialog.resizable(False, False)
        
        # モーダルダイアログに設定
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # センタリング
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (150 // 2)
        self.dialog.geometry(f"300x150+{x}+{y}")
        
        self._setup_ui()
        self._set_current_date()
        
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
        
        return self.result
    
    def _setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(
            main_frame, 
            text="日付を選択してください", 
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)
        
        # 日付選択フレーム
        date_frame = tk.Frame(main_frame)
        date_frame.pack(pady=10)
        
        # 年選択
        tk.Label(date_frame, text="年:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        year_combo = ttk.Combobox(
            date_frame,
            textvariable=self.year_var,
            values=[str(year) for year in range(2020, 2031)],
            width=8,
            state="readonly"
        )
        year_combo.grid(row=0, column=1, padx=5)
        
        # 月選択
        tk.Label(date_frame, text="月:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        month_combo = ttk.Combobox(
            date_frame,
            textvariable=self.month_var,
            values=[f"{month:02d}" for month in range(1, 13)],
            width=5,
            state="readonly"
        )
        month_combo.grid(row=0, column=3, padx=5)
        
        # 日選択
        tk.Label(date_frame, text="日:", font=("Arial", 10)).grid(row=0, column=4, padx=5)
        self.day_combo = ttk.Combobox(
            date_frame,
            textvariable=self.day_var,
            width=5,
            state="readonly"
        )
        self.day_combo.grid(row=0, column=5, padx=5)
        
        # 年月変更時のイベント
        year_combo.bind('<<ComboboxSelected>>', self._update_days)
        month_combo.bind('<<ComboboxSelected>>', self._update_days)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        # 今日ボタン
        today_button = tk.Button(
            button_frame,
            text="今日",
            command=self._set_today,
            font=("Arial", 10),
            width=8
        )
        today_button.pack(side=tk.LEFT)
        
        # OKボタン
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=self._on_ok,
            font=("Arial", 10),
            width=8
        )
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            font=("Arial", 10),
            width=8
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # ダイアログ閉じるイベント
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _set_current_date(self):
        """現在の日付を設定"""
        self.year_var.set(str(self.current_date.year))
        self.month_var.set(f"{self.current_date.month:02d}")
        self._update_days()
        self.day_var.set(f"{self.current_date.day:02d}")
    
    def _set_today(self):
        """今日の日付を設定"""
        today = date.today()
        self.year_var.set(str(today.year))
        self.month_var.set(f"{today.month:02d}")
        self._update_days()
        self.day_var.set(f"{today.day:02d}")
    
    def _update_days(self, event=None):
        """日の選択肢を更新"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            
            # 月の日数を計算
            if month in [1, 3, 5, 7, 8, 10, 12]:
                days = 31
            elif month in [4, 6, 9, 11]:
                days = 30
            else:  # 2月
                if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                    days = 29  # うるう年
                else:
                    days = 28
            
            # 日の選択肢を更新
            day_values = [f"{day:02d}" for day in range(1, days + 1)]
            self.day_combo['values'] = day_values
            
            # 現在選択されている日が有効な範囲内かチェック
            current_day = self.day_var.get()
            if current_day and int(current_day) > days:
                self.day_var.set(f"{days:02d}")
            
        except ValueError:
            # 年月が不正な場合は何もしない
            pass
    
    def _on_ok(self):
        """OKボタン押下時の処理"""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            
            selected_date = date(year, month, day)
            
            self.result = {
                'date': selected_date,
                'cancelled': False
            }
            
            self.dialog.destroy()
            
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("エラー", "有効な日付を選択してください。")
    
    def _on_cancel(self):
        """キャンセルボタン押下時の処理"""
        self.result = {
            'date': None,
            'cancelled': True
        }
        self.dialog.destroy()
