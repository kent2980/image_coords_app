"""
MVCアーキテクチャ版のメインエントリーポイント
新しいアーキテクチャで画像座標アプリケーションを起動
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers import CoordinateController, FileController, MainController
from src.models import AppSettingsModel, CoordinateModel, ImageModel, WorkerModel
from src.views import CoordinateCanvasView, MainView, SidebarView
from src.views.dialogs import DateSelectDialog, SettingsDialog, WorkerInputDialog


class ImageCoordsApp:
    """MVCアーキテクチャによる画像座標アプリケーション"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像座標アプリケーション (MVC)")
        self.root.geometry("1400x900")

        # アプリケーションのセットアップ
        self._setup_application()

    def _setup_application(self):
        """アプリケーションのセットアップ"""
        try:
            # モデルの初期化
            self._initialize_models()

            # ビューの初期化
            self._initialize_views()

            # コントローラーの初期化
            self._initialize_controllers()

            # アプリケーションの初期化
            self.main_controller.initialize_application()

        except Exception as e:
            messagebox.showerror(
                "初期化エラー", f"アプリケーションの初期化中にエラーが発生しました: {e}"
            )
            sys.exit(1)

    def _initialize_models(self):
        """モデルの初期化"""
        # アプリケーション設定モデル
        self.settings_model = AppSettingsModel()

        # 作業者モデル
        self.worker_model = WorkerModel()

        # 座標モデル
        self.coordinate_model = CoordinateModel()

        # 画像モデル
        self.image_model = ImageModel()

    def _initialize_views(self):
        """ビューの初期化"""
        # メインビュー
        self.main_view = MainView(self.root)

        # キャンバスビュー
        self.canvas_view = CoordinateCanvasView(self.main_view.canvas_frame)

        # サイドバービュー
        self.sidebar_view = SidebarView(self.main_view.sidebar_frame)

        # ダイアログクラス
        self.dialogs = {
            "WorkerInputDialog": WorkerInputDialog,
            "SettingsDialog": SettingsDialog,
            "DateSelectDialog": DateSelectDialog,
        }

    def _initialize_controllers(self):
        """コントローラーの初期化"""
        # ファイルコントローラー
        self.file_controller = FileController(
            self.coordinate_model, self.settings_model, self.worker_model
        )

        # 座標コントローラー
        self.coordinate_controller = CoordinateController(
            self.coordinate_model, self.image_model
        )

        # メインコントローラー（他のコントローラーを統括）
        self.main_controller = MainController(
            coordinate_model=self.coordinate_model,
            settings_model=self.settings_model,
            worker_model=self.worker_model,
            image_model=self.image_model,
            main_view=self.main_view,
            canvas_view=self.canvas_view,
            sidebar_view=self.sidebar_view,
            dialogs=self.dialogs,
            coordinate_controller=self.coordinate_controller,
            file_controller=self.file_controller,
        )

        # デバッグモードの設定（環境変数またはコマンドライン引数で制御）
        if os.getenv("DEBUG", "0") == "1" or "--debug" in sys.argv:
            self.main_controller.set_debug_mode(True)
            print("[DEBUG] デバッグモードが有効になりました")

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


def main():
    """メイン関数"""
    try:
        app = ImageCoordsApp()
        app.run()
    except KeyboardInterrupt:
        print("アプリケーションが中断されました。")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        messagebox.showerror("エラー", f"予期しないエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
