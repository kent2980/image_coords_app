"""
MVCアーキテクチャ版のメインエントリーポイント
新しいアーキテクチャで画像座標アプリケーションを起動
"""

import os
import signal
import sys
import tkinter as tk
from tkinter import messagebox

# プロジェクトルートを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.controllers import (
    BoardController,
    CoordinateController,
    FileController,
    MainController,
)
from src.models import (
    AppSettingsModel,
    BoardModel,
    CoordinateModel,
    ImageModel,
    LotModel,
    WorkerModel,
)
from src.views import CoordinateCanvasView, MainView, SidebarView
from src.views.dialogs import DateSelectDialog, SettingsDialog, WorkerInputDialog


class ImageCoordsApp:
    """MVCアーキテクチャによる画像座標アプリケーション"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像座標アプリケーション (MVC)")

        # サブディスプレイにフルスクリーンで表示設定
        self._setup_display()

        # アプリケーションのセットアップ
        self._setup_application()

    def _setup_display(self):
        """サブディスプレイにフルスクリーンで表示設定"""
        if os.getenv("DEBUG", "0") == "1" or "--debug" in sys.argv:
            # デバッグ時: サブディスプレイに移動してフルスクリーン
            # 環境変数 SUBDISPLAY で左右を指定可能 (LEFT/RIGHT)
            subdisplay = os.getenv("SUBDISPLAY", "LEFT").upper()

            if subdisplay == "RIGHT":
                # 右のサブディスプレイの場合
                self.root.geometry("1920x1080+1920+0")
                print("[DEBUG] 右のサブディスプレイにフルスクリーンで表示します")
            else:
                # 左のサブディスプレイの場合（デフォルト）
                self.root.geometry("1920x1080+-1920+0")
                print("[DEBUG] 左のサブディスプレイにフルスクリーンで表示します")

            self.root.state("zoomed")  # フルスクリーン化
        else:
            # 通常時: メインディスプレイで最大化
            self.root.state("zoomed")

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

        # 基盤モデル
        self.board_model = BoardModel()

        # ロットモデル
        self.lot_model = LotModel()

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
            self.coordinate_model,
            self.settings_model,
            self.worker_model,
            self.board_model,
            self.lot_model,
        )

        # 座標コントローラー
        self.coordinate_controller = CoordinateController(
            self.coordinate_model, self.image_model
        )

        # 基盤コントローラー
        self.board_controller = BoardController(
            self.board_model,
            self.coordinate_model,
            self.image_model,
        )

        # メインコントローラー（他のコントローラーを統括）
        self.main_controller = MainController(
            coordinate_model=self.coordinate_model,
            settings_model=self.settings_model,
            worker_model=self.worker_model,
            image_model=self.image_model,
            board_model=self.board_model,
            lot_model=self.lot_model,
            main_view=self.main_view,
            canvas_view=self.canvas_view,
            sidebar_view=self.sidebar_view,
            dialogs=self.dialogs,
            coordinate_controller=self.coordinate_controller,
            file_controller=self.file_controller,
            board_controller=self.board_controller,
        )

        # デバッグモードの設定（環境変数またはコマンドライン引数で制御）
        if os.getenv("DEBUG", "0") == "1" or "--debug" in sys.argv:
            self.main_controller.set_debug_mode(True)
            print("[DEBUG] デバッグモードが有効になりました")

        # アプリケーション終了時の処理を設定
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # シグナルハンドラーを設定
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """システム終了シグナルのハンドラーを設定"""

        def signal_handler(signum, frame):
            print(f"[シグナル受信] シグナル {signum} を受信しました")
            self._cleanup_and_exit()

        # SIGTERM（正常終了シグナル）とSIGINT（Ctrl+C）をキャッチ
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def _cleanup_and_exit(self):
        """クリーンアップしてアプリケーションを終了"""
        try:
            print("[クリーンアップ] アプリケーションを終了します...")

            # ロックファイルを削除
            if hasattr(self, "file_controller"):
                self.file_controller.remove_lot_number_dir_lock_file()
                print("[クリーンアップ] ロックファイルを削除しました")

        except Exception as e:
            print(f"[クリーンアップ] クリーンアップ中にエラーが発生しました: {e}")
        finally:
            # 強制終了
            os._exit(0)

    def _on_closing(self):
        """アプリケーション終了時の処理（ウィンドウの×ボタン）"""
        try:
            print("[終了処理] ウィンドウ終了が要求されました")

            # ロックファイルを削除
            if hasattr(self, "file_controller"):
                self.file_controller.delete_lot_number_dir_lock_file()
                print("[終了処理] ロックファイルを削除しました")

            # アプリケーションを終了
            self.root.destroy()

        except Exception as e:
            print(f"[終了処理] 終了処理中にエラーが発生しました: {e}")
            # エラーが発生してもアプリケーションは終了する
            self.root.destroy()

    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


def main():
    """メイン関数"""
    app = None
    try:
        app = ImageCoordsApp()
        app.run()
    except KeyboardInterrupt:
        print("アプリケーションが中断されました。")
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        messagebox.showerror("エラー", f"予期しないエラーが発生しました: {e}")
    finally:
        # 確実にクリーンアップを実行
        if app and hasattr(app, "file_controller"):
            try:
                app.file_controller.delete_lot_number_dir_lock_file()
                print("[クリーンアップ] ロックファイルのクリーンアップを実行しました")
            except Exception as cleanup_error:
                print(
                    f"[クリーンアップ] クリーンアップ中にエラーが発生しました: {cleanup_error}"
                )
        print("[終了] アプリケーションを終了しました。")


if __name__ == "__main__":
    main()
