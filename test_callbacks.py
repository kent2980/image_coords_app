#!/usr/bin/env python3
"""
MainViewクラスのコールバック関数をテストするスクリプト
"""

import os
import sys
import tkinter as tk
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.controllers.coordinate_controller import CoordinateController
    from src.controllers.file_controller import FileController
    from src.controllers.main_controller import MainController
    from src.models.app_settings_model import AppSettingsModel
    from src.models.coordinate_model import CoordinateModel
    from src.models.image_model import ImageModel
    from src.models.worker_model import WorkerModel
    from src.views.coordinate_canvas_view import CoordinateCanvasView
    from src.views.main_view import MainView
    from src.views.sidebar_view import SidebarView
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)


class CallbackTestApp:
    """コールバック関数のテスト用アプリケーション"""

    def __init__(self):
        self.root = tk.Tk()
        self.test_results = {}

        # モデルの初期化
        print("モデルを初期化中...")
        self.app_settings_model = AppSettingsModel()
        self.coordinate_model = CoordinateModel()
        self.image_model = ImageModel()
        self.worker_model = WorkerModel()

        # メインビューの初期化
        print("メインビューを初期化中...")
        self.main_view = MainView(self.root)

        # 他のビューの初期化
        print("他のビューを初期化中...")
        self.canvas_view = CoordinateCanvasView(self.main_view.canvas_frame)
        self.sidebar_view = SidebarView(self.main_view.sidebar_frame)

        # コントローラーの初期化
        print("コントローラーを初期化中...")
        self.coordinate_controller = CoordinateController(
            self.coordinate_model, self.image_model
        )
        self.file_controller = FileController(
            self.coordinate_model, self.app_settings_model, self.worker_model
        )

        # メインコントローラーの初期化
        print("メインコントローラーを初期化中...")
        self.main_controller = MainController(
            coordinate_model=self.coordinate_model,
            settings_model=self.app_settings_model,
            worker_model=self.worker_model,
            image_model=self.image_model,
            main_view=self.main_view,
            canvas_view=self.canvas_view,
            sidebar_view=self.sidebar_view,
            dialogs={},  # 空の辞書
            coordinate_controller=self.coordinate_controller,
            file_controller=self.file_controller,
        )

        # デバッグモードを有効にして初期化
        print("アプリケーションを初期化中...")
        os.environ["DEBUG"] = "1"  # デバッグモードを有効化

        # ダイアログクラスの追加
        try:
            from src.views.dialogs.date_select_dialog import DateSelectDialog
            from src.views.dialogs.item_tag_switch_dialog import ItemTagSwitchDialog
            from src.views.dialogs.settings_dialog import SettingsDialog
            from src.views.dialogs.worker_input_dialog import WorkerInputDialog

            self.main_controller.dialogs = {
                "WorkerInputDialog": WorkerInputDialog,
                "DateSelectDialog": DateSelectDialog,
                "SettingsDialog": SettingsDialog,
                "ItemTagSwitchDialog": ItemTagSwitchDialog,
            }
        except ImportError as e:
            print(f"ダイアログのインポートエラー: {e}")
            # 最低限必要なダイアログだけ空辞書で設定
            self.main_controller.dialogs = {}

        # MainControllerのデバッグモードを強制的に有効化
        self.main_controller.debug_mode = True

        self.main_controller.initialize_application()

        # テスト実行
        self.run_tests()

    def run_tests(self):
        """コールバック関数のテストを実行"""
        print("\n" + "=" * 50)
        print("コールバック関数テスト開始")
        print("=" * 50)

        # テスト対象のコールバック関数リスト
        test_callbacks = [
            "clear_coordinates",
            "delete_coordinate",
            "prev_coordinate",
            "next_coordinate",
            "on_model_selected",
            "on_item_tag_change",
            "undo_action",
            "redo_action",
            "open_settings",
            "prev_board",
            "next_board",
            "delete_board",
        ]

        for callback_name in test_callbacks:
            self.test_callback(callback_name)

        # テスト結果の表示
        self.show_test_results()

        # 画面を表示（5秒後に自動終了）
        self.root.after(5000, self.root.quit)
        self.root.mainloop()

    def test_callback(self, callback_name):
        """個別のコールバック関数をテスト"""
        print(f"\n[テスト] {callback_name}")

        try:
            # MainViewのコールバック辞書から関数を取得
            callback_func = self.main_view.callbacks.get(callback_name)

            if callback_func is None:
                result = f"❌ コールバック '{callback_name}' が見つかりません"
                print(f"  {result}")
                self.test_results[callback_name] = result
                return

            # MainControllerに同名のメソッドが存在するかチェック
            controller_method = getattr(self.main_controller, callback_name, None)
            if controller_method is None:
                result = f"❌ MainController.{callback_name}() メソッドが存在しません"
                print(f"  {result}")
                self.test_results[callback_name] = result
                return

            # 関数が呼び出し可能かチェック
            if not callable(callback_func):
                result = (
                    f"❌ コールバック '{callback_name}' は呼び出し可能ではありません"
                )
                print(f"  {result}")
                self.test_results[callback_name] = result
                return

            # 実際にコールバック関数を呼び出してテスト
            print(f"  📞 {callback_name}() を実行中...")
            callback_func()

            result = f"✅ 正常に実行されました"
            print(f"  {result}")
            self.test_results[callback_name] = result

        except Exception as e:
            result = f"❌ 実行中にエラーが発生: {str(e)}"
            print(f"  {result}")
            self.test_results[callback_name] = result

    def show_test_results(self):
        """テスト結果をまとめて表示"""
        print("\n" + "=" * 50)
        print("テスト結果")
        print("=" * 50)

        success_count = 0
        total_count = len(self.test_results)

        for callback_name, result in self.test_results.items():
            print(f"{callback_name:<20}: {result}")
            if result.startswith("✅"):
                success_count += 1

        print("-" * 50)
        print(f"成功: {success_count}/{total_count}")
        print(f"失敗: {total_count - success_count}/{total_count}")

        if success_count == total_count:
            print("🎉 全てのテストが成功しました！")
        else:
            print("⚠️  一部のテストが失敗しました。")


def main():
    """メイン関数"""
    print("MainViewコールバック関数テスト")
    print(f"開始時刻: {datetime.now()}")

    try:
        app = CallbackTestApp()
    except Exception as e:
        print(f"アプリケーション初期化エラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
