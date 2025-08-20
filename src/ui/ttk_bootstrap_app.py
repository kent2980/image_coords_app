"""
統合ttkbootstrapアプリケーション
既存のMVCアーキテクチャをttkbootstrapで実装
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ttkbootstrap版のビューをインポート
from ..views.main_view_ttk import MainView
from ..views.sidebar_view_ttk import SidebarView
from ..views.coordinate_canvas_view_ttk import CoordinateCanvasView

# 既存のコントローラーをインポート
from ..controllers.main_controller import MainController
from ..controllers.coordinate_controller import CoordinateController
from ..controllers.file_controller import FileController
from ..controllers.board_controller import BoardController

# 必要なモデルをインポート
from ..models.coordinate_model import CoordinateModel
from ..models.app_settings_model import AppSettingsModel
from ..models.worker_model import WorkerModel
from ..models.board_model import BoardModel
from ..models.lot_model import LotModel
from ..models.image_model import ImageModel


class TtkBootstrapApp:
    """ttkbootstrap版メインアプリケーション"""
    
    def __init__(self, theme: str = "flatly"):
        """
        アプリケーションを初期化
        
        Args:
            theme: ttkbootstrapテーマ名
                  - flatly (デフォルト、モダンでクリーンなデザイン)
                  - darkly (ダークテーマ)
                  - pulse (赤アクセント)
                  - cosmo (青アクセント)
                  - journal (クラシック)
                  - lumen (明るいテーマ)
                  - minty (緑アクセント)
                  - sandstone (暖色系)
                  - superhero (ダークヒーロー)
                  - yeti (シンプル)
        """
        self.theme = theme
        
        # ttkbootstrapウィンドウを作成
        self.root = ttk.Window(
            title="Image Coordinate App (Modern UI)",
            themename=theme,
            size=(1400, 900),
            resizable=(True, True)
        )
        
        # ウィンドウを最大化
        self.root.state("zoomed")
        
        # ビューを初期化
        self._setup_views()
        
        # コントローラーを初期化
        self._setup_controllers()
        
        # ビューとコントローラーを連携
        self._connect_views_and_controllers()
        
        print(f"[INFO] ttkbootstrapアプリケーションが初期化されました (テーマ: {theme})")
    
    def _setup_views(self):
        """ビューを設定"""
        # メインビュー
        self.main_view = MainView(self.root)
        
        # サイドバービュー
        self.sidebar_view = SidebarView(self.main_view.sidebar_frame)
        
        # キャンバスビュー
        self.canvas_view = CoordinateCanvasView(self.main_view.canvas_frame)
        
        # メニューとトップコントロールを設定
        self.main_view.setup_menu_frame()
        self.main_view.setup_top_controls()
        
        print("[INFO] ttkbootstrapビューが設定されました")
    
    def _setup_controllers(self):
        """コントローラーを設定"""
        # モデルを初期化
        self.coordinate_model = CoordinateModel()
        self.settings_model = AppSettingsModel()
        self.worker_model = WorkerModel()
        self.board_model = BoardModel()
        self.lot_model = LotModel()
        self.image_model = ImageModel()
        
        # ファイルコントローラー
        self.file_controller = FileController(
            coordinate_model=self.coordinate_model,
            settings_model=self.settings_model,
            worker_model=self.worker_model,
            board_model=self.board_model,
            lot_model=self.lot_model
        )
        
        # 基盤コントローラー
        self.board_controller = BoardController(
            board_model=self.board_model,
            coordinate_model=self.coordinate_model,
            image_model=self.image_model
        )
        
        # 座標コントローラー
        self.coordinate_controller = CoordinateController(
            coordinate_model=self.coordinate_model,
            image_model=self.image_model
        )
        
        # メインコントローラー
        self.main_controller = MainController(
            main_view=self.main_view,
            sidebar_view=self.sidebar_view,
            canvas_view=self.canvas_view,
            file_controller=self.file_controller,
            coordinate_controller=self.coordinate_controller,
            board_controller=self.board_controller,
            coordinate_model=self.coordinate_model,
            settings_model=self.settings_model,
            worker_model=self.worker_model,
            image_model=self.image_model,
            board_model=self.board_model,
            lot_model=self.lot_model,
            dialogs={}  # 空の辞書でダイアログを初期化
        )
        
        print("[INFO] コントローラーが設定されました")
    
    def _connect_views_and_controllers(self):
        """ビューとコントローラーを連携"""
        # サイドバービューにコントローラー参照を設定
        self.sidebar_view.set_coordinate_controller(self.coordinate_controller)
        
        # 座標コントローラーにファイルコントローラーを設定（メソッドが存在する場合）
        if hasattr(self.coordinate_controller, 'set_file_controller'):
            self.coordinate_controller.set_file_controller(self.file_controller)
        
        # メインコントローラーの初期化を実行（メソッドが存在する場合）
        if hasattr(self.main_controller, 'initialize'):
            self.main_controller.initialize()
        
        print("[INFO] ビューとコントローラーが連携されました")
    
    def run(self):
        """アプリケーションを実行"""
        print(f"[INFO] ttkbootstrapアプリケーションを開始します (テーマ: {self.theme})")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("[INFO] アプリケーションが中断されました")
        except Exception as e:
            print(f"[ERROR] アプリケーション実行エラー: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("[INFO] アプリケーションが終了しました")
    
    def change_theme(self, new_theme: str):
        """テーマを変更"""
        try:
            self.root.style.theme_use(new_theme)
            self.theme = new_theme
            print(f"[INFO] テーマが変更されました: {new_theme}")
        except Exception as e:
            print(f"[ERROR] テーマ変更エラー: {e}")
    
    def get_available_themes(self) -> list:
        """利用可能なテーマ一覧を取得"""
        return list(self.root.style.theme_names())
    
    def toggle_dark_mode(self):
        """ダークモードの切り替え"""
        current_theme = self.theme
        if "dark" in current_theme.lower():
            # ダークテーマの場合は明るいテーマに変更
            self.change_theme("flatly")
        else:
            # 明るいテーマの場合はダークテーマに変更
            self.change_theme("darkly")
    
    def show_theme_selector(self):
        """テーマ選択ダイアログを表示"""
        dialog = ttk.Toplevel(self.root)
        dialog.title("テーマ選択")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # ダイアログの中央配置
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 100
        ))
        
        # タイトル
        ttk.Label(
            dialog, 
            text="テーマを選択してください",
            font=("Arial", 12, "bold"),
            bootstyle="primary"
        ).pack(pady=20)
        
        # テーマリスト
        theme_frame = ttk.Frame(dialog)
        theme_frame.pack(fill=BOTH, expand=YES, padx=20, pady=10)
        
        # スクロール可能なリストボックス
        listbox_frame = ttk.Frame(theme_frame)
        listbox_frame.pack(fill=BOTH, expand=YES)
        
        listbox = ttk.Treeview(
            listbox_frame,
            columns=("theme",),
            show="tree headings",
            height=10
        )
        listbox.heading("#0", text="テーマ名")
        listbox.heading("theme", text="説明")
        
        # テーマ情報
        theme_info = {
            "flatly": "モダンでクリーン (推奨)",
            "darkly": "ダークテーマ",
            "pulse": "赤アクセント",
            "cosmo": "青アクセント", 
            "journal": "クラシック",
            "lumen": "明るいテーマ",
            "minty": "緑アクセント",
            "sandstone": "暖色系",
            "superhero": "ダークヒーロー",
            "yeti": "シンプル"
        }
        
        # テーマをリストに追加
        for theme in self.get_available_themes():
            description = theme_info.get(theme, "標準テーマ")
            listbox.insert("", "end", text=theme, values=(description,))
        
        listbox.pack(fill=BOTH, expand=YES)
        
        # 現在のテーマを選択
        for item in listbox.get_children():
            if listbox.item(item, "text") == self.theme:
                listbox.selection_set(item)
                listbox.focus(item)
                break
        
        # ボタンフレーム
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_apply():
            selection = listbox.selection()
            if selection:
                selected_theme = listbox.item(selection[0], "text")
                self.change_theme(selected_theme)
                dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(
            button_frame, 
            text="適用", 
            command=on_apply,
            bootstyle="success"
        ).pack(side=LEFT, padx=10)
        
        ttk.Button(
            button_frame, 
            text="キャンセル", 
            command=on_cancel,
            bootstyle="secondary"
        ).pack(side=LEFT, padx=10)
        
        # ダブルクリックでも適用
        listbox.bind("<Double-1>", lambda e: on_apply())


def create_app(theme: str = "flatly") -> TtkBootstrapApp:
    """ttkbootstrapアプリケーションを作成"""
    return TtkBootstrapApp(theme)


def main():
    """メイン関数 - アプリケーションの実行例"""
    app = create_app("flatly")  # モダンなフラットデザイン
    app.run()


if __name__ == "__main__":
    main()
