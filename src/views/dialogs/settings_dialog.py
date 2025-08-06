"""
設定ダイアログ
アプリケーション設定の編集を管理
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Dict, Any, Callable


class SettingsDialog:
    """設定ダイアログ"""
    
    def __init__(self, parent: tk.Tk, settings_model=None, callback: Optional[Callable] = None):
        self.parent = parent
        self.settings_model = settings_model
        self.callback = callback
        self.dialog = None
        
        # 設定変数
        self.image_directory_var = tk.StringVar()
        self.data_directory_var = tk.StringVar()
        self.default_mode_var = tk.StringVar()
        
        # 変更フラグ
        self.settings_changed = False
    
    def show(self):
        """ダイアログを表示"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("設定")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        
        # モーダルダイアログに設定
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # センタリング
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"500x300+{x}+{y}")
        
        self._load_current_settings()
        self._setup_ui()
        
        # ダイアログが閉じられるまで待機
        self.dialog.wait_window()
    
    def _load_current_settings(self):
        """現在の設定を読み込み"""
        if self.settings_model:
            self.image_directory_var.set(self.settings_model.image_directory)
            self.data_directory_var.set(self.settings_model.data_directory)
            self.default_mode_var.set(self.settings_model.default_mode)
        else:
            self.image_directory_var.set("未選択")
            self.data_directory_var.set("未選択")
            self.default_mode_var.set("編集")
    
    def _setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(
            main_frame, 
            text="アプリケーション設定", 
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # 設定項目フレーム
        settings_frame = tk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 画像ディレクトリ設定
        self._setup_directory_setting(
            settings_frame, 
            "画像ディレクトリ:",
            self.image_directory_var,
            self._select_image_directory,
            0
        )
        
        # データディレクトリ設定
        self._setup_directory_setting(
            settings_frame,
            "データディレクトリ:",
            self.data_directory_var,
            self._select_data_directory,
            1
        )
        
        # デフォルトモード設定
        self._setup_mode_setting(settings_frame, 2)
        
        # ボタンフレーム
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 保存ボタン
        save_button = tk.Button(
            button_frame,
            text="保存",
            command=self._on_save,
            font=("Arial", 10),
            width=10
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # キャンセルボタン
        cancel_button = tk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            font=("Arial", 10),
            width=10
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # リセットボタン
        reset_button = tk.Button(
            button_frame,
            text="リセット",
            command=self._on_reset,
            font=("Arial", 10),
            width=10
        )
        reset_button.pack(side=tk.LEFT)
        
        # ダイアログ閉じるイベント
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
    
    def _setup_directory_setting(self, parent, label_text, var, command, row):
        """ディレクトリ設定UI"""
        # ラベル
        label = tk.Label(parent, text=label_text, font=("Arial", 10))
        label.grid(row=row, column=0, sticky="w", pady=5)
        
        # パス表示エントリ
        entry = tk.Entry(parent, textvariable=var, font=("Arial", 9), state="readonly")
        entry.grid(row=row, column=1, sticky="ew", padx=(10, 5), pady=5)
        
        # 選択ボタン
        button = tk.Button(parent, text="選択", command=command, font=("Arial", 9))
        button.grid(row=row, column=2, padx=5, pady=5)
        
        # グリッド設定
        parent.grid_columnconfigure(1, weight=1)
    
    def _setup_mode_setting(self, parent, row):
        """モード設定UI"""
        # ラベル
        label = tk.Label(parent, text="デフォルトモード:", font=("Arial", 10))
        label.grid(row=row, column=0, sticky="w", pady=5)
        
        # モード選択フレーム
        mode_frame = tk.Frame(parent)
        mode_frame.grid(row=row, column=1, sticky="w", padx=(10, 5), pady=5)
        
        # 編集モードラジオボタン
        edit_radio = tk.Radiobutton(
            mode_frame,
            text="編集",
            variable=self.default_mode_var,
            value="編集",
            font=("Arial", 9)
        )
        edit_radio.pack(side=tk.LEFT, padx=5)
        
        # 閲覧モードラジオボタン
        view_radio = tk.Radiobutton(
            mode_frame,
            text="閲覧",
            variable=self.default_mode_var,
            value="閲覧",
            font=("Arial", 9)
        )
        view_radio.pack(side=tk.LEFT, padx=5)
    
    def _select_image_directory(self):
        """画像ディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="画像ディレクトリを選択",
            initialdir=self.image_directory_var.get() if self.image_directory_var.get() != "未選択" else None
        )
        
        if directory:
            self.image_directory_var.set(directory)
            self.settings_changed = True
    
    def _select_data_directory(self):
        """データディレクトリを選択"""
        directory = filedialog.askdirectory(
            title="データディレクトリを選択",
            initialdir=self.data_directory_var.get() if self.data_directory_var.get() != "未選択" else None
        )
        
        if directory:
            self.data_directory_var.set(directory)
            self.settings_changed = True
    
    def _on_save(self):
        """保存ボタン押下時の処理"""
        try:
            if self.settings_model:
                # 設定を更新
                self.settings_model.image_directory = self.image_directory_var.get()
                self.settings_model.data_directory = self.data_directory_var.get()
                self.settings_model.default_mode = self.default_mode_var.get()
                
                # 設定ファイルに保存
                if self.settings_model.save_settings():
                    messagebox.showinfo("設定保存", "設定を保存しました。")
                    
                    # コールバック実行
                    if self.callback:
                        self.callback()
                    
                    self.dialog.destroy()
                else:
                    messagebox.showerror("保存エラー", "設定の保存に失敗しました。")
            else:
                messagebox.showwarning("エラー", "設定モデルが初期化されていません。")
                
        except Exception as e:
            messagebox.showerror("エラー", f"設定保存中にエラーが発生しました: {e}")
    
    def _on_cancel(self):
        """キャンセルボタン押下時の処理"""
        if self.settings_changed:
            result = messagebox.askyesnocancel(
                "設定変更",
                "設定が変更されています。保存しますか？"
            )
            
            if result is True:  # はい
                self._on_save()
                return
            elif result is None:  # キャンセル
                return
        
        self.dialog.destroy()
    
    def _on_reset(self):
        """リセットボタン押下時の処理"""
        result = messagebox.askyesno(
            "設定リセット",
            "設定をデフォルト値にリセットしますか？"
        )
        
        if result:
            if self.settings_model:
                self.settings_model.reset_to_defaults()
                self._load_current_settings()
                self.settings_changed = True
                messagebox.showinfo("リセット完了", "設定をデフォルト値にリセットしました。")
