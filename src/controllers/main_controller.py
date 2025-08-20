"""
メインコントローラー
アプリケーション全体の制御と他のコントローラーとの連携を管理
"""

import json
import os
import re
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ..controllers.board_controller import BoardController
    from ..controllers.coordinate_controller import CoordinateController
    from ..controllers.file_controller import FileController
    from ..models.app_settings_model import AppSettingsModel
    from ..models.board_model import BoardModel
    from ..models.coordinate_model import CoordinateModel
    from ..models.image_model import ImageModel
    from ..models.lot_model import LotModel
    from ..models.worker_model import WorkerModel
    from ..views.coordinate_canvas_view import CoordinateCanvasView
    from ..views.main_view import MainView
    from ..views.sidebar_view import SidebarView


class MainController:
    """メインアプリケーションコントローラー"""

    # region コンストラクタ
    def __init__(
        self,
        coordinate_model: "CoordinateModel",
        settings_model: "AppSettingsModel",
        worker_model: "WorkerModel",
        image_model: "ImageModel",
        board_model: "BoardModel",
        lot_model: "LotModel",
        main_view: "MainView",
        canvas_view: "CoordinateCanvasView",
        sidebar_view: "SidebarView",
        dialogs: Dict[str, Any],
        coordinate_controller: "CoordinateController",
        file_controller: "FileController",
        board_controller: "BoardController",
    ):

        # モデル
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        self.image_model = image_model
        self.board_model = board_model
        self.lot_model = lot_model

        # ビュー
        self.main_view = main_view
        self.canvas_view = canvas_view
        self.sidebar_view = sidebar_view
        self.dialogs = dialogs

        # 他のコントローラー
        self.coordinate_controller = coordinate_controller
        self.file_controller = file_controller
        self.board_controller = board_controller

        # 現在の日付
        self.current_date = date.today()

        # 作業者情報
        self.current_worker_no: Optional[str] = None
        self.current_worker_name: Optional[str] = None

        # 現在のロット番号
        self.current_lot_number: Optional[str] = None

        # 現在のモデル名
        self.current_model: Optional[str] = None

        # 画像フォルダ内のモデルリスト
        self.model_list: List[Dict[str, str]] = None

        # 前回選択されたモデル（変更検出用）
        self.previous_model: Optional[str] = None

        # モデルデータ
        self.model_data: List[Any] = []

        # 初期化フラグ
        self.is_initialized: bool = False

        # デバッグフラグ（デバッグ時は作業者入力をスキップ）
        # 環境変数 DEBUG=1 でデバッグモードを有効化
        self.debug_mode: bool = os.getenv("DEBUG", "0") == "1"

    # endregion

    # region プロパティ
    @property
    def current_lot_number(self):
        return getattr(self, "_current_lot_number", None)

    @current_lot_number.setter
    def current_lot_number(self, value: str):
        self.sidebar_view.set_lot_number(value)
        self._current_lot_number = value

    @property
    def current_worker_name(self):
        return getattr(self, "_current_worker_name", None)

    @current_worker_name.setter
    def current_worker_name(self, value: str):
        self.sidebar_view.update_worker_label(value)
        self._current_worker_name = value

    @property
    def current_worker_no(self):
        return getattr(self, "_current_worker_no", None)

    @current_worker_no.setter
    def current_worker_no(self, value: str):
        self.sidebar_view.set_worker_no(value)
        self._current_worker_no = value

    @property
    def current_model(self):
        return getattr(self, "_current_model", None)

    @current_model.setter
    def current_model(self, value: str):
        self.sidebar_view.set_product_number(value)
        self._current_model = value

    # endregion

    # region アプリケーションの初期化
    # アプリケーションの初期化
    def initialize_application(self):
        """アプリケーションを初期化"""
        if self.is_initialized:
            return

        # 作業者入力（デバッグモード時はスキップ）
        if not self.debug_mode:
            self._setup_worker_input()
        else:
            # デバッグモード時はデフォルト作業者情報を設定
            self.current_worker_no = "DEBUG"
            self.current_worker_name = "デバッグユーザー"

            print("[DEBUG] デバッグモード: 作業者入力をスキップしました")

        # コントローラー間の連携を設定
        self.coordinate_controller.set_canvas_view(self.canvas_view)
        self.coordinate_controller.set_sidebar_view(self.sidebar_view)
        self.coordinate_controller.set_main_view(self.main_view)
        self.board_controller.set_sidebar_view(self.sidebar_view)
        self.board_controller.set_main_view(self.main_view)

        # SidebarViewにMainViewの参照を設定
        self.sidebar_view.set_main_view_reference(self.main_view)

        # SidebarViewにCoordinateControllerの参照を設定（自動保存用）
        self.sidebar_view.set_coordinate_controller(self.coordinate_controller)

        # ビューのコールバックを設定
        self._setup_view_callbacks()

        # ビューのイベントバインドを設定
        self._setup_canvas_events()

        # UI要素を初期化
        self._initialize_ui_elements()

        # 設定を読み込んで適用
        self._apply_settings()

        self.is_initialized = True

    def set_debug_mode(self, debug: bool = True):
        """デバッグモードを設定"""
        self.debug_mode = debug
        print(f"[DEBUG] デバッグモード: {'有効' if debug else '無効'}")

    def _setup_worker_input(self):
        """作業者入力ダイアログを表示"""
        dialog = self.dialogs["WorkerInputDialog"](
            self.main_view.root, self.worker_model
        )
        result = dialog.show()

        if result is None:
            # キャンセルされた場合はアプリを終了
            self.main_view.root.quit()
            return

        # 作業者情報をサイドバーに設定（ラベル更新）
        worker_text = f"作業者: {result['worker_name']}"
        self.sidebar_view.update_worker_label(worker_text)

        # 現在の作業者情報を保持
        self.current_worker_no = result["worker_no"]
        self.current_worker_name = result["worker_name"]

        # 作業者情報をロットモデルに設定
        self.lot_model.worker_no = self.current_worker_no

        # SidebarViewにも作業者番号を設定
        self.sidebar_view.set_worker_no(result["worker_no"])

    def _setup_view_callbacks(self):
        """ビューのコールバック関数を設定"""
        # メインビューのコールバック
        main_callbacks = {
            "select_date": self.select_date,
            "on_mode_change": self.on_mode_change,
            "open_settings": self.open_settings,
            "undo_action": self.undo_action,
            "redo_action": self.redo_action,
            "select_image": self.select_image,
            "load_json": self.load_json,
            "save_coordinates": self.save_coordinates,
            "on_save_button_click": self.on_save_button_click,  # 保存ボタン処理
            "clear_coordinates": self.clear_coordinates,
            "delete_coordinate": self.delete_coordinate,
            "prev_coordinate": self.prev_coordinate,
            "next_coordinate": self.next_coordinate,
            "on_model_selected": self.on_model_selected,
            "on_lot_number_save": self.on_lot_number_save,  # ロット番号保存
            "on_item_tag_change": self.on_item_tag_change,  # 現品票切り替え
            # メニューコールバック
            "new_project": self.new_project,
            "new_file": self.new_file,
            "open_file": self.open_file,
            "save_file": self.save_file,
            "exit_app": self.exit_app,
            "delete_file": self.delete_file,
            # ボタンコールバック
            "prev_board": self.prev_board,
            "next_board": self.next_board,
            "delete_board": self.delete_board,
            # 基盤管理コールバック
            "save_all_boards": self.save_all_boards,
            "load_board_session": self.load_board_session,
        }

        # コールバック設定のデバッグ情報
        print(f"[DEBUG] メインビューコールバック設定: {len(main_callbacks)}個")
        for key in main_callbacks:
            print(f"[DEBUG] コールバック '{key}': {main_callbacks[key]}")

        self.main_view.set_callbacks(main_callbacks)

        # キャンバスビューのコールバック
        canvas_callbacks = {
            "on_left_click": self.on_canvas_left_click,
            "on_right_click": self.on_canvas_right_click,
            "on_view_click": self.on_canvas_view_click,
            "on_canvas_resize": self.on_canvas_resize,
        }
        self.canvas_view.set_callbacks(canvas_callbacks)

        # サイドバービューのコールバック
        sidebar_callbacks = {
            "on_form_data_changed": self.on_form_data_changed,
            "search_coordinates": self.search_coordinates,
        }
        self.sidebar_view.set_callbacks(sidebar_callbacks)

    def _setup_canvas_events(self):
        """キャンバスのイベントバインドを設定"""
        # 初期モードに基づいてイベントを設定
        current_mode = self.main_view.get_current_mode()
        mode = "edit" if current_mode == "編集" else "view"
        self.canvas_view.bind_events(mode)

        # キーイベントをバインド（削除キー）
        self.main_view.root.bind("<Delete>", self.on_delete_key)
        self.main_view.root.bind("<BackSpace>", self.on_delete_key)

        # フォーカスを設定してキーイベントを受け取れるようにする
        self.main_view.root.focus_set()

    def _initialize_ui_elements(self):
        """UI要素を初期化"""

        # メニューフレームの設定
        self.main_view.setup_menu_frame()

        # トップコントロールを設定
        self.main_view.setup_top_controls()

        # メニューを設定
        self.main_view.setup_menu_buttons()

        # 日付表示を更新
        self.main_view.update_date_label(self.current_date.strftime("%Y-%m-%d"))

        # モデル選択肢を更新
        self._update_model_options()

        # 不良項目選択肢を更新
        defects = self.file_controller.load_defects_from_file()
        self.sidebar_view.update_defect_options(defects)

        # Undo/Redoボタンの状態を更新
        self._update_undo_redo_state()

        # CoordinateControllerに初期基盤番号を設定
        initial_board_number = self.board_controller.get_current_board_number()
        self.coordinate_controller.set_current_board_number(initial_board_number)

    def _apply_settings(self):
        """設定を適用"""
        # デフォルトモードを設定
        default_mode = self.settings_model.default_mode
        self.main_view.set_mode(default_mode)
        self.on_mode_change()

    def _update_model_options(self):
        """モデル選択肢を更新（旧コード互換機能）"""
        # CoordinateControllerのload_models_from_fileメソッドを使用
        self.model_list = self.coordinate_controller.load_models_from_file(
            self.settings_model
        )

        # MainViewのモデル選択肢を更新
        self.main_view.update_model_options(self.model_list)

        # サイドバーには従来通りモデル名のみを渡す（互換性のため）
        model_names = [list(item.keys())[0] for item in self.model_list if item]
        if not model_names:
            model_names = ["画像ディレクトリが未設定"]

        self.sidebar_view.update_model_options(model_names)

    def _update_undo_redo_state(self):
        """Undo/Redoボタンの状態を更新"""
        can_undo = self.coordinate_controller.can_undo()
        can_redo = self.coordinate_controller.can_redo()
        self.main_view.update_undo_redo_state(can_undo, can_redo)

    # イベントハンドラー
    def on_delete_key(self, event):
        """Deleteキーまたはbackspaceキーが押された時の処理"""
        # 編集モードでない場合は何もしない
        current_mode = self.main_view.get_current_mode()
        if current_mode != "編集":
            return

        # 選択中の座標を削除
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            # 座標を削除
            self.coordinate_controller.delete_coordinate(current_index)

            # 座標マーカーを再描画
            self._redraw_coordinates_for_new_scale()

            # サイドバーをクリア
            self.sidebar_view.clear_form()

            print(f"[削除] 座標 {current_index + 1} を削除しました")
        else:
            print("[削除] 削除する座標が選択されていません")

    def on_model_selected(self):
        """モデル選択時の処理"""
        selected_model = self.main_view.get_selected_model()
        if selected_model and not selected_model.startswith("画像"):
            # モデルが変更されたかチェック
            model_changed = self.previous_model != selected_model

            if model_changed and self.previous_model is not None:
                # モデルが変更された場合のみロット番号をリセット（初回選択は除く）
                self.current_lot_number = None
                self.sidebar_view.clear_lot_number()
                print(
                    f"モデルが変更されました: {self.previous_model} → {selected_model}（ロット番号をリセット）"
                )

            # 前回のモデルを記録
            self.previous_model = selected_model

            # 選択されたモデルの画像を表示
            self._load_model_image(selected_model)

            # 基盤セッションを自動読み込み（該当するものがあれば）
            current_lot = self.current_lot_number or self.sidebar_view.get_lot_number()
            if current_lot:
                self.board_controller.load_board_session(
                    self.current_date, selected_model, current_lot
                )

            # 保存名を自動設定
            current_lot = self.current_lot_number or self.sidebar_view.get_lot_number()

            if not model_changed:
                print(f"モデルを選択しました: {selected_model}")

    def _load_model_image(self, model_name: str):
        """選択されたモデルの画像を読み込み"""
        # MainViewから画像パスを取得
        image_path = self.main_view.get_model_image_path(model_name)

        if image_path and os.path.exists(image_path):
            # 画像を読み込み表示
            tk_image = self.image_model.load_image(
                image_path,
                self.canvas_view.canvas_width,
                self.canvas_view.canvas_height,
            )

            if tk_image:
                self.canvas_view.display_image(
                    tk_image,
                    self.image_model.display_size[0],
                    self.image_model.display_size[1],
                )

                # 座標をクリア
                self.coordinate_controller.clear_coordinates()

                print(f"モデル画像を読み込みました: {model_name}")
            else:
                print(f"画像の読み込みに失敗しました: {model_name}")
        else:
            print(f"画像ファイルが見つかりません: {model_name}")

    def on_canvas_left_click(self, event):
        """キャンバス左クリック（編集モード）"""
        x, y = int(event.x), int(event.y)

        # 整番
        product_number = self.sidebar_view.get_product_number()
        # ロットナンバー
        lot_number = self.sidebar_view.get_lot_number()
        # 整番・ロット取得フラグ
        is_product_lot_set = bool(product_number and lot_number)

        # 整番・ロットが設定されている場合
        if is_product_lot_set:
            # 座標を追加
            index = self.coordinate_controller.add_coordinate(x, y)

            # 新しい座標を選択状態にする
            self.coordinate_controller.set_current_coordinate(index)

            # フォームをクリアして項目番号を設定
            self.sidebar_view.clear_form()
            # 項目番号を座標詳細として設定
            detail = {"item_number": str(index + 1)}
            self.sidebar_view.set_coordinate_detail(detail)

            # リファレンス入力フィールドにフォーカス
            self.sidebar_view.focus_reference_entry()

            # Undo/Redoボタンの状態を更新
            self._update_undo_redo_state()

        else:
            # 整番・ロットが設定されていない場合はエラーメッセージを表示
            self.main_view.show_error("整番(モデル)と指図を設定してください。")

    def on_canvas_right_click(self, event):
        """キャンバス右クリック（編集モード）- 既存座標の選択"""
        x, y = int(event.x), int(event.y)

        # 最も近い座標を選択
        selected_index = self.coordinate_controller.select_coordinate(x, y)

        if selected_index is not None:
            # フォームを選択した座標の詳細情報で更新
            detail = self.coordinate_controller.get_current_coordinate_detail()
            if detail:
                detail["item_number"] = str(selected_index + 1)  # 項目番号を設定
                self.sidebar_view.set_coordinate_detail(detail)
            else:
                # 詳細情報がない場合は項目番号のみ設定
                detail = {"item_number": str(selected_index + 1)}
                self.sidebar_view.set_coordinate_detail(detail)

            print(f"座標 {selected_index + 1} を選択しました")

    def on_canvas_view_click(self, event):
        """キャンバスクリック（閲覧モード）"""
        x, y = int(event.x), int(event.y)

        # 最も近い座標を選択
        selected_index = self.coordinate_controller.select_coordinate(x, y)

        if selected_index is not None:
            # 選択した座標の詳細情報を表示
            detail = self.coordinate_controller.get_current_coordinate_detail()
            if detail:
                detail["item_number"] = str(selected_index + 1)  # 項目番号を設定
                self.sidebar_view.set_coordinate_detail(detail)
            else:
                # 詳細情報がない場合は項目番号のみ設定
                detail = {"item_number": str(selected_index + 1)}
                self.sidebar_view.set_coordinate_detail(detail)

            # 選択した座標をハイライト表示
            self.canvas_view.highlight_coordinate(selected_index)

            print(f"[閲覧モード] 座標 {selected_index + 1} を選択しました")
        else:
            # 座標が選択されていない場合はフォームをクリア
            self.coordinate_model.set_current_coordinate(-1)
            self.sidebar_view.clear_form()
            self.canvas_view.clear_highlight()
            print("[閲覧モード] 座標の選択を解除しました")

        if selected_index is not None:
            # 選択した座標の詳細情報を表示
            detail = self.coordinate_controller.get_current_coordinate_detail()
            if detail:
                self.sidebar_view.display_coordinate_info(detail, selected_index)

            print(f"[閲覧モード] 座標 {selected_index + 1} を選択しました")
        else:
            # 座標が選択されていない場合はフォームをクリア
            self.coordinate_model.set_current_coordinate(-1)
            self.sidebar_view.clear_form()
            self.canvas_view.clear_highlight()
            print("[閲覧モード] 座標の選択を解除しました")

    def on_form_data_changed(self):
        """フォームデータ変更時の処理"""
        # 現在選択中の座標があれば詳細情報を更新
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            detail = self.sidebar_view.get_coordinate_detail()
            self.coordinate_controller.update_current_coordinate_detail(detail)

    # endregion

    # region コールバック関数

    # アクション（コールバック順）
    def select_date(self):
        """日付選択ダイアログを表示"""
        dialog = self.dialogs["DateSelectDialog"](
            self.main_view.root, self.current_date
        )
        result = dialog.show()

        if result and not result["cancelled"] and result["date"]:
            self.current_date = result["date"]
            self.main_view.update_date_label(result["date"].strftime("%Y-%m-%d"))

    def on_mode_change(self):
        """モード変更時の処理"""
        current_mode = self.main_view.get_current_mode()

        if current_mode == "編集":
            # 編集モード
            self.canvas_view.bind_events("edit")
            self.sidebar_view.set_readonly_mode(False)
            print("[モード変更] 編集モードに切り替えました")
        else:
            # 閲覧モード
            self.canvas_view.bind_events("view")
            self.sidebar_view.set_readonly_mode(True)
            print("[モード変更] 閲覧モードに切り替えました")

            # 座標がある場合は概要情報を表示
            if self.coordinate_model.coordinates:
                summary = self.coordinate_controller.get_coordinate_summary()
                self.sidebar_view.display_coordinate_summary(summary)

                # 最初の座標を自動選択
                self.coordinate_controller.set_current_coordinate(0)
                detail = self.coordinate_controller.get_current_coordinate_detail()
                if detail:
                    self.sidebar_view.display_coordinate_info(detail, 0)

        # ハイライトをクリア（モード変更時は一旦リセット）
        if current_mode == "編集":
            self.canvas_view.clear_highlight()

    def open_settings(self):
        """設定ダイアログを開く"""
        dialog = self.dialogs["SettingsDialog"](
            self.main_view.root, self.settings_model, self.on_settings_changed
        )
        dialog.show()

    def undo_action(self):
        """元に戻す操作"""
        if self.coordinate_controller.undo():
            self._update_undo_redo_state()

    def redo_action(self):
        """やり直し操作"""
        if self.coordinate_controller.redo():
            self._update_undo_redo_state()

    def select_image(self):
        """画像を選択"""
        pass

    def load_json(self, file_path=None):
        """JSONファイルを読み込み"""
        pass

    def save_coordinates(self):
        """座標を保存（旧コード互換の自動保存機能付き）"""
        pass

    def on_save_button_click(self):
        """保存ボタンクリック時の処理（ロット番号処理＋座標保存）"""
        # 最初にロット番号が入力されているかチェック
        lot_number = self.main_view.get_lot_number().strip()
        if lot_number:
            # ロット番号が入力されている場合はロット番号保存処理を実行
            self.on_lot_number_save()
        else:
            # ロット番号が入力されていない場合は座標保存処理を実行
            self.save_coordinates()

    def on_settings_changed(self):
        """設定変更時のコールバック"""
        # モデル選択リストを更新
        self._update_model_options()

    def on_lot_number_save(self):
        """ロット番号保存処理"""
        import re

        # 現在のモードを取得
        mode = self.main_view.get_current_mode()

        if mode == "編集":
            # 作業者が設定されているかチェック
            if not self.current_worker_no:
                self.main_view.show_error("作業者が設定されていません。")
                return

            # ロット番号を取得
            lot_number = self.main_view.get_lot_number().strip()
            # ロット番号入力エリアを初期化
            self.main_view.clear_lot_number()
            if not lot_number:
                self.main_view.show_error("ロット番号を入力してください。")
                return

            # ロット番号の形式をチェック (7桁-2桁の形式)
            lot_pattern = r"^\d{7}-10$|^\d{7}-20$"
            if not re.match(lot_pattern, lot_number):
                self.main_view.show_error(
                    "ロット番号の形式が正しくありません。\n形式: 1234567-10 または 1234567-20 (7桁-10または7桁-20)"
                )
                return

            # ロット番号を保存
            self.current_lot_number = lot_number
            self.current_model = self.main_view.get_selected_model().split("_")[0]

            print(f"ロット番号を保存しました: {lot_number}")

            # ロット切り替え処理
            self._change_lot_number()

    def on_item_tag_change(self):
        """現品票で切り替えボタンが押された時の処理"""
        print("[DEBUG] 現品票切り替えボタンがクリックされました")
        try:
            # 現在のモードを取得
            mode = self.main_view.get_current_mode()

            # 現品票切り替えダイアログを表示
            print("[DEBUG] ダイアログを表示しようとしています...")
            result = None

            if mode == "編集":
                # 編集モード：製番と指図を入力するダイアログ
                result = self.main_view.show_item_tag_switch_dialog()
                model_number = result[0]
                # 製番からモデル名を検索
                self.current_model = self._find_model_by_product_number(
                    model_number
                ).split("_")[0]
                self.current_lot_number = result[1]
                # ロット切り替え処理
                self._change_lot_number()
            elif mode == "閲覧":
                # 閲覧モード：指図入力のみのダイアログを表示
                result = self._show_lot_number_input_dialog()
            else:
                result = None

            print(f"[DEBUG] ダイアログの結果: {result[0]}")

        except Exception as e:
            print(f"現品票切り替えエラー: {e}")
            import traceback

            traceback.print_exc()
            self.main_view.show_error(
                f"現品票切り替え中にエラーが発生しました:\n{str(e)}"
            )

    def on_save_button_click(self):
        """保存ボタンクリック時の処理（ロット番号処理＋座標保存）"""
        # 最初にロット番号が入力されているかチェック
        lot_number = self.main_view.get_lot_number().strip()
        if lot_number:
            # ロット番号が入力されている場合はロット番号保存処理を実行
            self.on_lot_number_save()
        else:
            # ロット番号が入力されていない場合は座標保存処理を実行
            self.save_coordinates()

    def clear_coordinates(self):
        """座標をクリア"""
        print("[DEBUG] 座標をクリアします")
        self.coordinate_controller.clear_coordinates()
        self.sidebar_view.clear_form()
        self._update_undo_redo_state()

    def delete_coordinate(self):
        """現在選択中の座標を削除する"""
        print("[DEBUG] delete_coordinate() called")
        # CoordinateControllerに削除機能があるかチェック
        if hasattr(self.coordinate_controller, "delete_selected_coordinate"):
            self.coordinate_controller.delete_selected_coordinate()
        else:
            print(
                "[DEBUG] CoordinateController.delete_selected_coordinate method not found"
            )

        # フォームをクリア
        self.sidebar_view.clear_form()
        self._update_undo_redo_state()

    def prev_coordinate(self):
        """前の座標に移動する"""
        print("[DEBUG] prev_coordinate() called")
        # CoordinateControllerに前の座標機能があるかチェック
        if hasattr(self.coordinate_controller, "select_previous_coordinate"):
            self.coordinate_controller.select_previous_coordinate()
        else:
            print(
                "[DEBUG] CoordinateController.select_previous_coordinate method not found"
            )

    def next_coordinate(self):
        """次の座標に移動する"""
        print("[DEBUG] next_coordinate() called")
        # CoordinateControllerに次の座標機能があるかチェック
        if hasattr(self.coordinate_controller, "select_next_coordinate"):
            self.coordinate_controller.select_next_coordinate()
        else:
            print(
                "[DEBUG] CoordinateController.select_next_coordinate method not found"
            )

    def search_coordinates(self):
        """座標検索機能（閲覧モード用）"""
        # TODO: 座標検索機能を実装
        print("検索機能は今後実装予定です。")

    def on_canvas_resize(self, new_width: int, new_height: int):
        """キャンバスサイズ変更時の処理"""
        print(f"[DEBUG] キャンバスサイズ変更コールバック: {new_width}x{new_height}")

        try:
            # 現在画像が表示されている場合は再読み込み
            if self.image_model._current_image_path and os.path.exists(
                self.image_model._current_image_path
            ):
                print(f"[DEBUG] 画像を新しいキャンバスサイズで再読み込み中...")

                # 新しいキャンバスサイズで画像を再読み込み
                tk_image = self.image_model.reload_image_for_canvas_size(
                    new_width, new_height
                )

                if tk_image:
                    # キャンバスに再表示
                    self.canvas_view.display_image(tk_image)

                    # 座標マーカーを再描画（座標変換が必要な場合）
                    self._redraw_coordinates_for_new_scale()

                    print(f"[DEBUG] 画像とマーカーの再描画完了")

        except Exception as e:
            print(f"キャンバスリサイズエラー: {e}")
            import traceback

            traceback.print_exc()

    def _redraw_coordinates_for_new_scale(self):
        """新しいスケールに合わせて座標マーカーを再描画"""
        try:
            # 元画像座標を表示座標に変換して再描画
            display_coordinates = []
            for orig_x, orig_y in self.coordinate_model.coordinates:
                display_x, display_y = (
                    self.image_model.convert_original_to_display_coords(orig_x, orig_y)
                )
                display_coordinates.append((display_x, display_y))

            if display_coordinates:
                self.canvas_view.redraw_coordinate_markers(display_coordinates)

                # 現在選択中の座標をハイライト
                current_index = self.coordinate_model.current_index
                if current_index >= 0:
                    self.canvas_view.highlight_coordinate(current_index)

        except Exception as e:
            print(f"座標再描画エラー: {e}")

    def _update_board_display(self) -> None:
        """基盤表示を更新"""
        try:
            # BoardControllerの_update_board_display()メソッドを呼び出し
            if hasattr(self.board_controller, "_update_board_display"):
                self.board_controller._update_board_display()
            else:
                print(
                    "[DEBUG] BoardController._update_board_displayメソッドが見つかりません"
                )
        except Exception as e:
            print(f"基盤表示更新エラー: {e}")
            import traceback

            traceback.print_exc()

    def _show_lot_number_input_dialog(self):
        """閲覧モード用の指図入力ダイアログを表示"""
        import re
        import tkinter as tk
        from tkinter import ttk

        class LotNumberInputDialog:
            def __init__(self, parent):
                self.result = None
                self.dialog = tk.Toplevel(parent)
                self.dialog.title("指図番号入力")
                self.dialog.geometry("350x200")
                self.dialog.resizable(False, False)
                self.dialog.transient(parent)
                self.dialog.grab_set()

                # ダイアログを中央に配置
                self.dialog.update_idletasks()
                x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_width()) // 2
                y = (self.dialog.winfo_screenheight() - self.dialog.winfo_height()) // 2
                self.dialog.geometry(f"+{x}+{y}")

                self._create_widgets()

                # Enterキーでの確定
                self.dialog.bind("<Return>", lambda e: self._on_ok())

                # 初期フォーカス
                self.lot_number_entry.focus_set()

            def _create_widgets(self):
                # メインフレーム
                main_frame = ttk.Frame(self.dialog, padding="20")
                main_frame.pack(fill=tk.BOTH, expand=True)

                # タイトルラベル
                title_label = ttk.Label(
                    main_frame, text="指図番号を入力してください", font=("", 12, "bold")
                )
                title_label.pack(pady=(0, 20))

                # 指図入力フレーム
                lot_frame = ttk.LabelFrame(main_frame, text="指図番号", padding="10")
                lot_frame.pack(fill=tk.X, pady=(0, 20))

                self.lot_number_entry = ttk.Entry(lot_frame, font=("", 11), width=30)
                self.lot_number_entry.pack(fill=tk.X)

                # 形式説明ラベル
                format_label = ttk.Label(
                    lot_frame,
                    text="形式: 1234567-10 または 1234567-20",
                    font=("", 9),
                    foreground="gray",
                )
                format_label.pack(pady=(5, 0))

                # ボタンフレーム
                button_frame = ttk.Frame(main_frame)
                button_frame.pack(fill=tk.X)

                # OKボタン
                ok_button = ttk.Button(
                    button_frame, text="OK", command=self._on_ok, width=10
                )
                ok_button.pack(side=tk.RIGHT, padx=(5, 0))

                # キャンセルボタン
                cancel_button = ttk.Button(
                    button_frame, text="キャンセル", command=self._on_cancel, width=10
                )
                cancel_button.pack(side=tk.RIGHT)

            def _on_ok(self):
                lot_number = self.lot_number_entry.get().strip()

                if not lot_number:
                    tk.messagebox.showerror(
                        "入力エラー", "指図番号を入力してください。", parent=self.dialog
                    )
                    return

                # 形式チェック
                lot_pattern = r"^\d{7}-10$|^\d{7}-20$"
                if not re.match(lot_pattern, lot_number):
                    tk.messagebox.showerror(
                        "入力エラー",
                        "指図番号の形式が正しくありません。\n形式: 1234567-10 または 1234567-20 (7桁-10または7桁-20)",
                        parent=self.dialog,
                    )
                    return

                self.result = lot_number
                self.dialog.destroy()

            def _on_cancel(self):
                self.result = None
                self.dialog.destroy()

            def show(self):
                self.dialog.wait_window()
                return self.result

        try:
            dialog = LotNumberInputDialog(self.main_view.root)
            return dialog.show()
        except Exception as e:
            print(f"指図入力ダイアログエラー: {e}")
            self.main_view.show_error(
                f"指図入力ダイアログでエラーが発生しました:\n{str(e)}"
            )
            return None

    def _switch_model_by_product_number(self, product_number: str):
        """製番に基づいてモデルを切り替え"""
        try:
            # 現在のモデル選択肢から製番に一致するモデルを検索
            model_values = self.main_view.get_model_values()
            print(f"[DEBUG] 利用可能なモデル: {model_values}")

            # 製番を含むモデルを検索（部分一致）
            matching_models = [
                model for model in model_values if product_number in model
            ]
            print(
                f"[DEBUG] 製番 '{product_number}' に一致するモデル: {matching_models}"
            )

            if matching_models:
                # 最初にマッチしたモデルを選択
                selected_model = matching_models[0]

                # 前回選択されたモデルを記録
                self.previous_model = self.main_view.get_selected_model()

                # モデルコンボボックスで選択
                self.main_view.set_model(selected_model)

                # モデル選択イベントをトリガー（画像切り替えのため）
                self.on_model_selected()

                # キャンバス画像を強制的に更新
                self._load_model_image(selected_model)

                print(
                    f"[モデル切り替え] 製番 '{product_number}' に基づいて '{selected_model}' を選択し、画像を切り替えました"
                )
            else:
                print(
                    f"[モデル切り替え] 製番 '{product_number}' に一致するモデルが見つかりませんでした"
                )
                self.main_view.show_warning(
                    f"製番 '{product_number}' に一致するモデルが見つかりませんでした。\n手動でモデルを選択してください。",
                    "モデル未発見",
                )

        except Exception as e:
            print(f"モデル切り替えエラー: {e}")

    def _find_model_by_product_number(self, product_number: str) -> Optional[str]:
        """製番からモデル名を検索する

        Args:
            product_number: 製番（例: "12345"）

        Returns:
            マッチしたモデル名、見つからない場合はNone
        """
        if not product_number or not self.model_list:
            return None

        model_regex = rf"^{product_number}.*$"

        # モデルリストから製番に一致するモデル名を検索
        for item in self.model_list:
            if not item:
                continue
            model_name = list(item.keys())[0]
            if re.match(model_regex, model_name):
                print(
                    f"[製番検索] 製番 '{product_number}' → モデル '{model_name}' が見つかりました"
                )
                return model_name

        print(
            f"[製番検索] 製番 '{product_number}' に一致するモデルが見つかりませんでした"
        )
        return None

    # メニューコールバック関数
    def new_project(self):
        """新しいプロジェクトを作成"""
        print("[メニュー] 新しいプロジェクトが選択されました")
        messagebox.showinfo(
            "新しいプロジェクト", "新しいプロジェクトの作成機能は実装中です。"
        )

    def new_file(self):
        """新しいファイルを作成"""
        print("[メニュー] 新しいファイルが選択されました")
        messagebox.showinfo("新しいファイル", "新しいファイルの作成機能は実装中です。")

    def open_file(self):
        """ファイルを開く"""
        print("[メニュー] ファイルを開くが選択されました")
        self.load_json()

    def save_file(self):
        """ファイルを保存"""
        print("[メニュー] ファイルを保存が選択されました")
        self.save_coordinates()

    def exit_app(self):
        """アプリケーションを終了"""
        print("[メニュー] 終了が選択されました")
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            self.main_view.root.quit()

    def prev_board(self):
        """前の基板を選択"""
        print("[ボタン] 前の基板が選択されました")

        try:
            # 現在のモデル、ロット番号、作業者情報を取得
            selected_model = self.main_view.get_selected_model()
            lot_number = self.current_lot_number or self.sidebar_view.get_lot_number()

            if (
                not selected_model
                or selected_model.startswith("画像")
                or not lot_number
            ):
                messagebox.showwarning(
                    "基盤切り替えエラー",
                    "モデルとロット番号が設定されていません。\n基盤切り替えにはモデルとロット番号が必要です。",
                )
                return

            # 前の基盤に切り替え
            success = self.board_controller.switch_to_previous_board(
                self.current_date, selected_model, lot_number, self.current_worker_no
            )

            if success:
                board_number = self.board_controller.get_current_board_number()

                # 既存のJSONファイルがあるかチェックして読み込み
                self._load_existing_json_for_board(
                    selected_model, lot_number, board_number
                )

                # 座標表示を更新
                self._redraw_coordinates_for_new_scale()

                next_board = board_number + 1

                # CoordinateControllerに新しい基盤番号を通知
                self.coordinate_controller.set_current_board_number(board_number)

                # Undo/Redoボタンの状態を更新
                self._update_undo_redo_state()
            else:
                messagebox.showinfo("基盤切り替え", "これが最初の基盤です。")

        except Exception as e:
            print(f"前の基盤切り替えエラー: {e}")
            messagebox.showerror(
                "エラー", f"前の基盤への切り替え中にエラーが発生しました:\n{str(e)}"
            )

    def next_board(self):
        """次の基板を選択"""
        pass

    def delete_board(self):
        """現在の基板を削除"""
        print("[DEBUG] delete_board() called")

        # 削除確認ダイアログを表示
        result = messagebox.askyesno(
            "基板削除確認",
            "現在の基板を削除しますか？\n\n注意: この操作は元に戻せません。",
            icon="warning",
        )

        if result:
            try:
                print("[DEBUG] 基板削除処理を開始")

                # 現在のモデル、ロット番号を取得
                selected_model = self.main_view.get_selected_model()
                lot_number = (
                    self.current_lot_number or self.sidebar_view.get_lot_number()
                )

                if (
                    not selected_model
                    or selected_model.startswith("画像")
                    or not lot_number
                ):
                    messagebox.showwarning(
                        "基盤削除エラー", "モデルとロット番号が設定されていません。"
                    )
                    return

                # 基盤を削除
                success = self.board_controller.delete_current_board(
                    self.current_date, selected_model, lot_number
                )

                if success:
                    # 座標表示を更新
                    self._redraw_coordinates_for_new_scale()

                    # アンドゥ/リドゥの状態を更新
                    self._update_undo_redo_state()

                    board_number = self.board_controller.get_current_board_number()
                    messagebox.showinfo(
                        "基板削除", f"基板を削除しました。現在の基板: {board_number}"
                    )

                else:
                    messagebox.showerror("エラー", "基板削除に失敗しました。")

            except Exception as e:
                print(f"[DEBUG] 基板削除エラー: {e}")
                messagebox.showerror(
                    "エラー", f"基板削除中にエラーが発生しました:\n{str(e)}"
                )
        else:
            print("[DEBUG] 基板削除をキャンセル")

    def save_all_boards(self):
        """全基盤をJSONファイルに保存"""
        print("[基盤管理] 全基盤保存が選択されました")

        try:
            # 現在のモデル、ロット番号、作業者情報を取得
            selected_model = self.main_view.get_selected_model()
            lot_number = self.current_lot_number or self.sidebar_view.get_lot_number()

            if (
                not selected_model
                or selected_model.startswith("画像")
                or not lot_number
            ):
                messagebox.showwarning(
                    "保存エラー",
                    "モデルとロット番号が設定されていません。\n全基盤保存にはモデルとロット番号が必要です。",
                )
                return

            # 全基盤を保存
            success = self.board_controller.save_all_boards_to_json(
                self.current_date, selected_model, lot_number, self.current_worker_no
            )

            if success:
                board_summary = self.board_controller.get_board_summary()
                messagebox.showinfo(
                    "保存完了",
                    f"全 {board_summary['total_boards']} 基盤をJSONファイルに保存しました。",
                )
            else:
                messagebox.showerror("エラー", "全基盤の保存に失敗しました。")

        except Exception as e:
            print(f"全基盤保存エラー: {e}")
            messagebox.showerror(
                "エラー", f"全基盤保存中にエラーが発生しました:\n{str(e)}"
            )

    def load_board_session(self):
        """基盤セッションを読み込み"""
        print("[基盤管理] 基盤セッション読み込みが選択されました")

        try:
            # 現在のモデル、ロット番号を取得
            selected_model = self.main_view.get_selected_model()
            lot_number = self.current_lot_number or self.sidebar_view.get_lot_number()

            if (
                not selected_model
                or selected_model.startswith("画像")
                or not lot_number
            ):
                messagebox.showwarning(
                    "読み込みエラー",
                    "モデルとロット番号が設定されていません。\n基盤セッション読み込みにはモデルとロット番号が必要です。",
                )
                return

            # 基盤セッションを読み込み
            success = self.board_controller.load_board_session(
                self.current_date, selected_model, lot_number
            )

            if success:
                # 座標表示を更新
                self._redraw_coordinates_for_new_scale()

                board_summary = self.board_controller.get_board_summary()
                board_number = self.board_controller.get_current_board_number()
                messagebox.showinfo(
                    "読み込み完了",
                    f"基盤セッションを読み込みました。\n現在の基盤: {board_number}\n保存済み基盤数: {board_summary['total_boards']}",
                )
            else:
                messagebox.showinfo(
                    "読み込み", "該当する基盤セッションが見つかりませんでした。"
                )

        except Exception as e:
            print(f"基盤セッション読み込みエラー: {e}")
            messagebox.showerror(
                "エラー", f"基盤セッション読み込み中にエラーが発生しました:\n{str(e)}"
            )

    # endregion

    # region 内部関数

    def _switch_to_next_board_with_validation(
        self,
        selected_model: str = None,
        lot_number: str = None,
        worker_no: str = None,
        current_date=None,
    ):
        """次の基板への切り替えを実行（バリデーション付き）

        Args:
            selected_model: 選択されたモデル名（Noneの場合は現在のモデルを使用）
            lot_number: ロット番号（Noneの場合は現在のロット番号を使用）
            worker_no: 作業者番号（Noneの場合は現在の作業者番号を使用）
            current_date: 現在の日付（Noneの場合は現在の日付を使用）
        """
        # 引数が指定されていない場合は現在の値を使用
        if selected_model is None:
            selected_model = self.main_view.get_selected_model()
        if lot_number is None:
            lot_number = self.current_lot_number or self.sidebar_view.get_lot_number()
        if worker_no is None:
            worker_no = self.current_worker_no
        if current_date is None:
            current_date = self.current_date

        if not selected_model or selected_model.startswith("画像") or not lot_number:
            messagebox.showwarning(
                "基盤切り替えエラー",
                "モデルとロット番号が設定されていません。\n基盤切り替えにはモデルとロット番号が必要です。",
            )
            return

        # 次の基盤に切り替え
        success = self.board_controller.switch_to_next_board(
            current_date, selected_model, lot_number, worker_no
        )

        if success:
            # 座標表示をクリア
            self.coordinate_controller.clear_coordinates()

            # 現在の基板番号を取得
            board_number = self.board_controller.get_current_board_number()

            # 既存のJSONファイルがあるかチェックして読み込み
            if not self._load_existing_json_for_board(
                selected_model, lot_number, board_number
            ):
                self._check_and_load_latest_json(
                    self.lot_model.model, self.lot_model.lot_no
                )
            # 保存された基盤のメッセージを表示
            prev_board = board_number - 1 if board_number > 1 else 1

            # CoordinateControllerに新しい基盤番号を通知
            self.coordinate_controller.set_current_board_number(board_number)

            # Undo/Redoボタンの状態を更新
            self._update_undo_redo_state()

    def _save_current_board_to_session_and_json(
        self,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
    ):
        """現在の基盤データをセッションとJSONファイルの両方に保存"""
        try:
            selected_model = self.main_view.get_selected_model()
            if selected_model and not selected_model.startswith("画像"):
                image_path = self.image_model.current_image_path or ""

                # 基盤セッションデータを保存
                self.board_model.save_board_data(
                    self.board_model.current_board_number,
                    coordinates,
                    coordinate_details,
                    lot_number,
                    self.current_worker_no or "",
                    image_path,
                    selected_model,
                )

                # 基盤情報をファイルに保存
                date_str = self.current_date.strftime("%Y-%m-%d")
                self.board_model.save_board_info_to_file(
                    date_str, selected_model, lot_number
                )

                # 基盤を個別のJSONファイルにも保存
                json_success = self.board_controller._save_current_board_to_json(
                    self.current_date,
                    selected_model,
                    lot_number,
                    self.current_worker_no or "",
                    coordinates,
                    coordinate_details,
                )

                if json_success:
                    print(
                        f"基盤 {self.board_model.current_board_number} をセッションとJSONファイルに保存しました"
                    )
                else:
                    print(
                        f"基盤 {self.board_model.current_board_number} をセッションに保存しました（JSONファイル保存は失敗）"
                    )

        except Exception as e:
            print(f"基盤セッション・JSONファイル保存エラー: {e}")

    def _save_current_board_to_session(
        self,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
    ):
        """現在の基盤データをセッションに保存（旧メソッド - 互換性のため残す）"""
        self._save_current_board_to_session_and_json(
            coordinates, coordinate_details, lot_number
        )

    def _load_existing_json_for_board(
        self, model_name: str, lot_number: str, board_number: int
    ):
        """指定された基盤のJSONファイルが存在する場合に読み込み"""
        pass

    def _check_and_load_latest_json(self, model_name: str, lot_number: str):
        """対象ディレクトリの最新のJSONファイルを検索して自動読み込み、次のインデックスを設定"""

        pass

    def _find_json_directory_by_lot_number(self, lot_number: str) -> Optional[str]:
        """ロット番号に基づいてJSONディレクトリを検索"""
        try:
            # lot_number_info.jsonを読み込む
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            info_file = os.path.join(project_root, "lot_number_info.json")
            with open(info_file, "r", encoding="utf-8-sig") as f:
                info_data = json.load(f)
            return info_data.get(lot_number)
        except Exception as e:
            print(f"[find_json_dir] ディレクトリ検索エラー: {e}")
            return None

    def delete_file(self):
        """
        現在のファイルを削除（履歴フォルダに移動）
        確認ダイアログ付き、検査担当者権限が必要
        """
        pass

    def _change_lot_number(self):
        """ロット番号を変更する処理"""

        # ロックファイルが存在するかチェック
        if self.file_controller.is_lock_file_exists():
            # ロックファイルが存在する場合はエラーメッセージを表示
            self.main_view.show_error(
                "ロット番号の変更中にエラーが発生しました。\n別のプロセスでロット番号が使用中です。"
            )
            return

        # ディレクトリ作成
        self.file_controller.init_lot_number_directory(self.current_lot_number)
        # ロックファイル作成
        self.file_controller.create_lot_number_dir_lock_file()
        # ディレクトリ内のJSONファイル名を取得
        json_files = self.file_controller.get_lot_dir_json_list()
        # 最大インデックスを取得
        max_index = self.file_controller.get_max_json_index(json_files)
        # インデックス用のJSONファイルを作成
        self.file_controller.create_index_json_file(max_index)
        # main_viewの基盤選択ラベルを更新
        self.main_view.set_board_index_text(max_index + 1, max_index + 1)

    # endregion
