"""
基盤コントローラー
基盤の切り替えと管理を制御
"""

import os
from datetime import date
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ..controllers.file_controller import FileController
    from ..models.board_model import BoardModel
    from ..models.coordinate_model import CoordinateModel
    from ..models.image_model import ImageModel
    from ..views.sidebar_view import SidebarView
    from ..views.main_view import MainView


class BoardController:
    """基盤管理を行うコントローラー"""

    def __init__(
        self,
        board_model: "BoardModel",
        coordinate_model: "CoordinateModel",
        image_model: "ImageModel",
        file_controller: "FileController",
    ):
        self.board_model = board_model
        self.coordinate_model = coordinate_model
        self.image_model = image_model
        self.file_controller = file_controller

        # ビューへの参照（後で設定）
        self.sidebar_view: Optional["SidebarView"] = None
        self.main_view: Optional["MainView"] = None

    def set_sidebar_view(self, sidebar_view: "SidebarView") -> None:
        """サイドバービューを設定"""
        self.sidebar_view = sidebar_view

    def set_main_view(self, main_view: "MainView") -> None:
        """メインビューを設定"""
        self.main_view = main_view

    def set_board_model(self, board_model: "BoardModel") -> None:
        """基盤モデルを設定"""
        self.board_model = board_model

    def set_coordinate_model(self, coordinate_model: "CoordinateModel") -> None:
        """座標モデルを設定"""
        self.coordinate_model = coordinate_model

    def set_image_model(self, image_model: "ImageModel") -> None:
        """画像モデルを設定"""
        self.image_model = image_model

    def set_file_controller(self, file_controller: "FileController") -> None:
        """ファイルコントローラーを設定"""
        self.file_controller = file_controller

    def set_current_board_number(self, board_number: int) -> None:
        """現在の基盤番号を設定"""
        if board_number > 0:
            self.board_model.set_current_board(board_number)
            if self.sidebar_view:
                self.sidebar_view.update_board_display(board_number)
                
            # メインビューの基盤表示を更新
            self._update_board_display(board_number)
                
            print(f"現在の基盤番号を {board_number} に設定しました")
        else:
            raise ValueError("基盤番号は1以上の値を設定してください")

    def get_current_board_number(self) -> int:
        """現在の基盤番号を取得"""
        return self.board_model.current_board_number

    def get_board_max_number(self, mode: str, is_delete: bool) -> int:
        """現在のデータディレクトリに存在するJSONファイルの数を返却します"""

        json_files = self.file_controller.get_json_lists()
        if len(json_files) == 0:
            return 0
        if is_delete:
            return len(json_files)
        if mode == "編集":
            return len(json_files) + 1
        else:
            return len(json_files) 

    def switch_to_next_board(
        self, current_date: date, model_name: str, lot_number: str, worker_no: str
    ) -> bool:
        """次の基盤に切り替え"""
        try:
            # 現在の座標データを取得
            current_coordinates = self.coordinate_model.coordinates
            current_details = self.coordinate_model.coordinate_details

            # 現在の基盤にデータがある場合は保存
            if current_coordinates:
                # 基盤セッションデータを保存
                success = self._save_current_board_data(
                    current_date, model_name, lot_number, worker_no
                )
                if not success:
                    print("現在の基盤データの保存に失敗しました")
                    return False

                # JSONファイルにも保存
                json_success = self._save_current_board_to_json(
                    current_date,
                    model_name,
                    lot_number,
                    worker_no,
                    current_coordinates,
                    current_details,
                )
                if not json_success:
                    print("現在の基盤のJSONファイル保存に失敗しました")
                    # JSON保存に失敗してもセッション保存は成功しているので継続

            # 次の基盤番号を取得
            next_board_number = self.board_model.get_next_board_number()

            # 基盤を切り替え
            self.board_model.set_current_board(next_board_number)

            # 座標データをクリア
            self.coordinate_model.clear_coordinates()

            # サイドバーの表示を更新
            if self.sidebar_view:
                self.sidebar_view.clear_form()
                self.sidebar_view.update_board_display(next_board_number)

            # メインビューの基盤表示を更新
            self._update_board_display(next_board_number)

            # 基盤情報をファイルに保存
            date_str = current_date.strftime("%Y-%m-%d")
            self.board_model.save_board_info_to_file(date_str, model_name, lot_number)

            print(f"基盤 {next_board_number} に切り替えました")
            return True

        except Exception as e:
            print(f"基盤切り替えエラー: {e}")
            return False

    def switch_to_previous_board(
        self, current_date: date, model_name: str, lot_number: str, worker_no: str
    ) -> bool:
        """前の基盤に切り替え"""
        try:
            previous_board_number = self.board_model.get_previous_board_number()

            if previous_board_number is None:
                print("これが最初の基盤です")
                return False

            # 現在の座標データを取得
            current_coordinates = self.coordinate_model.coordinates
            current_details = self.coordinate_model.coordinate_details

            # 現在の基盤にデータがある場合は保存
            if current_coordinates:
                # 基盤セッションデータを保存
                success = self._save_current_board_data(
                    current_date, model_name, lot_number, worker_no
                )
                if not success:
                    print("現在の基盤データの保存に失敗しました")
                    return False

                # JSONファイルにも保存
                json_success = self._save_current_board_to_json(
                    current_date,
                    model_name,
                    lot_number,
                    worker_no,
                    current_coordinates,
                    current_details,
                )
                if not json_success:
                    print("現在の基盤のJSONファイル保存に失敗しました")
                    # JSON保存に失敗してもセッション保存は成功しているので継続

            # 基盤を切り替え
            self.board_model.set_current_board(previous_board_number)

            # 前の基盤のデータを読み込み
            self._load_board_data(previous_board_number)

            # サイドバーの表示を更新
            if self.sidebar_view:
                self.sidebar_view.update_board_display(previous_board_number)

            # メインビューの基盤表示を更新
            self._update_board_display(previous_board_number)

            # 基盤情報をファイルに保存
            date_str = current_date.strftime("%Y-%m-%d")
            self.board_model.save_board_info_to_file(date_str, model_name, lot_number)

            print(f"基盤 {previous_board_number} に切り替えました")
            return True

        except Exception as e:
            print(f"前の基盤への切り替えエラー: {e}")
            return False

    def delete_current_board(
        self, current_date: date, model_name: str, lot_number: str
    ) -> bool:
        """現在の基盤を削除"""
        try:
            current_board_number = self.board_model.current_board_number
            
            # 現在のJSONパスを取得
            json_path = self.file_controller.get_current_json_path()

            # JSONファイルを削除
            if json_path:
                if os.path.exists(json_path):
                    os.remove(json_path)

            # 基盤データを削除
            self.board_model.delete_board_data(current_board_number)

            # 座標データをクリア
            self.coordinate_model.clear_coordinates()

            # 削除後の基盤番号を決定
            board_list = self.file_controller.get_json_lists()

            if board_list:
                # 残っている基盤がある場合は最後の基盤に切り替え
                board_count = len(board_list)
                self.board_model.set_current_board(board_count)
                self._load_board_data(board_count)
                new_board_number = board_count
            else:
                # 基盤が全て削除された場合は基盤1に戻る
                self.board_model.set_current_board(1)
                new_board_number = 1

            # サイドバーの表示を更新
            if self.sidebar_view:
                self.sidebar_view.clear_form()
                self.sidebar_view.update_board_display(new_board_number)

            # メインビューの基盤表示を更新
            self._update_board_display(new_board_number,True)

            # 基盤情報をファイルに保存
            date_str = current_date.strftime("%Y-%m-%d")
            self.board_model.save_board_info_to_file(date_str, model_name, lot_number)

            print(f"基盤 {current_board_number} を削除しました")
            return True

        except Exception as e:
            print(f"基盤削除エラー: {e}")
            return False

    def save_all_boards_to_json(
        self, current_date: date, model_name: str, lot_number: str, worker_no: str
    ) -> bool:
        """全基盤をJSONファイルに保存"""
        try:
            # 現在の座標データを取得
            current_coordinates = self.coordinate_model.coordinates
            current_details = self.coordinate_model.coordinate_details

            # 現在の基盤にデータがある場合は保存
            if current_coordinates:
                success = self._save_current_board_data(
                    current_date, model_name, lot_number, worker_no
                )
                if not success:
                    print("現在の基盤データの保存に失敗しました")

            # 保存ディレクトリを取得
            date_str = current_date.strftime("%Y-%m-%d")
            save_dir = self.file_controller.setup_json_save_dir(
                current_date, model_name, lot_number
            )

            if not save_dir:
                print("保存ディレクトリの作成に失敗しました")
                return False

            # 全基盤データを保存
            boards_data = self.board_model.boards_data
            saved_count = 0

            for board_number, board_data in boards_data.items():
                # ファイル名を基盤番号で設定（4桁ゼロパディング）
                filename = f"{board_number:04d}.json"
                file_path = os.path.join(save_dir, filename)

                # JSONデータを作成
                save_data = self.file_controller.create_save_data(
                    board_data.get("model", model_name),
                    board_data["coordinates"],
                    board_data["image_path"],
                    board_data["coordinate_details"],
                    board_data["lot_number"],
                    board_data["worker_no"],
                )

                # 基盤番号を追加
                save_data["board_number"] = board_number

                # JSONファイルに保存
                if self.file_controller.save_json_data(file_path, save_data):
                    saved_count += 1
                    print(f"基盤 {board_number} を保存しました: {filename}")

            print(f"全 {saved_count} 基盤をJSONファイルに保存しました")
            return saved_count > 0

        except Exception as e:
            print(f"全基盤JSON保存エラー: {e}")
            return False

    def load_board_session(
        self, current_date: date, model_name: str, lot_number: str
    ) -> bool:
        """基盤セッションを読み込み"""
        try:
            date_str = current_date.strftime("%Y-%m-%d")

            # 基盤情報をファイルから読み込み
            success = self.board_model.load_board_info_from_file(
                date_str, model_name, lot_number
            )

            if success:
                # 現在の基盤データを読み込み
                current_board_number = self.board_model.current_board_number
                self._load_board_data(current_board_number)

                # サイドバーの表示を更新
                if self.sidebar_view:
                    self.sidebar_view.update_board_display(current_board_number)

                # メインビューの基盤表示を更新
                self._update_board_display(current_board_number)

                print(
                    f"基盤セッションを読み込みました（現在の基盤: {current_board_number}）"
                )
                return True

            return False

        except Exception as e:
            print(f"基盤セッション読み込みエラー: {e}")
            return False

    def get_board_summary(self) -> Dict[str, Any]:
        """基盤管理の概要を取得"""
        return self.board_model.get_summary()

    def set_board_data(
        self,
        board_number: int,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
        worker_no: str,
        image_path: str = "",
        model_name: str = "",
    ) -> bool:
        """指定された基盤にデータを設定"""
        try:
            success = self.board_model.save_board_data(
                board_number,
                coordinates,
                coordinate_details,
                lot_number,
                worker_no,
                image_path,
                model_name,
            )

            if success:
                print(
                    f"基盤 {board_number} にデータを設定しました（座標数: {len(coordinates)}）"
                )

            return success

        except Exception as e:
            print(f"基盤データ設定エラー: {e}")
            return False

    def set_coordinates_for_current_board(
        self,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]] = None,
    ) -> None:
        """現在の基盤に座標データを設定"""
        if coordinate_details is None:
            coordinate_details = []

        self.coordinate_model.set_coordinates_with_details(
            coordinates, coordinate_details
        )

        print(
            f"現在の基盤（{self.board_model.current_board_number}）に座標データを設定しました（座標数: {len(coordinates)}）"
        )

    def has_unsaved_changes(self) -> bool:
        """現在の基盤に未保存の変更があるかチェック"""
        current_coordinates = self.coordinate_model.coordinates
        current_details = self.coordinate_model.coordinate_details
        return self.board_model.has_unsaved_changes(
            current_coordinates, current_details
        )

    def _save_current_board_data(
        self, current_date: date, model_name: str, lot_number: str, worker_no: str
    ) -> bool:
        """現在の基盤データを保存"""
        try:
            current_board_number = self.board_model.current_board_number
            current_coordinates = self.coordinate_model.coordinates
            current_details = self.coordinate_model.coordinate_details
            image_path = self.image_model.current_image_path

            return self.board_model.save_board_data(
                current_board_number,
                current_coordinates,
                current_details,
                lot_number,
                worker_no,
                image_path,
                model_name,
            )

        except Exception as e:
            print(f"現在の基盤データ保存エラー: {e}")
            return False

    def _load_board_data(self, board_number: int) -> bool:
        """指定された基盤のデータを読み込み"""
        try:
            board_data = self.board_model.get_board_data(board_number)

            if board_data:
                # 座標データを設定
                coordinates = board_data.get("coordinates", [])
                coordinate_details = board_data.get("coordinate_details", [])

                self.coordinate_model.set_coordinates_with_details(
                    coordinates, coordinate_details
                )

                print(
                    f"基盤 {board_number} のデータを読み込みました（座標数: {len(coordinates)}）"
                )
                return True
            else:
                # データがない場合は空の状態
                self.coordinate_model.clear_coordinates()
                print(f"基盤 {board_number} には保存されたデータがありません")
                return True

        except Exception as e:
            print(f"基盤データ読み込みエラー: {e}")
            return False

    def _save_current_board_to_json(
        self,
        current_date: date,
        model_name: str,
        lot_number: str,
        worker_no: str,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
    ) -> bool:
        """現在の基盤をJSONファイルに保存"""
        try:
            # 保存ディレクトリを取得
            save_dir = self.file_controller.setup_json_save_dir(
                current_date, model_name, lot_number
            )

            if not save_dir:
                print("JSONファイル保存ディレクトリの作成に失敗しました")
                return False

            # 現在の基盤番号でファイル名を生成（4桁ゼロパディング）
            current_board_number = self.board_model.current_board_number
            filename = f"{current_board_number:04d}.json"
            file_path = os.path.join(save_dir, filename)

            # 画像パスを取得
            image_path = self.image_model.current_image_path or ""

            # 保存データを作成
            save_data = self.file_controller.create_save_data(
                model_name, coordinates, image_path, coordinate_details, lot_number, worker_no
            )

            # 基盤番号を追加
            save_data["board_number"] = current_board_number

            # JSONファイルに保存
            success = self.file_controller.save_json_data(file_path, save_data)

            if success:
                print(
                    f"基盤 {current_board_number} をJSONファイルに保存しました: {filename}"
                )

            return success

        except Exception as e:
            print(f"基盤JSONファイル保存エラー: {e}")
            return False

    def reset_board_session(self):
        """基盤セッションをリセット"""
        try:
            self.board_model.reset()
            self.coordinate_model.clear_coordinates()

            if self.sidebar_view:
                self.sidebar_view.clear_form()
                self.sidebar_view.update_board_display(1)

            print("基盤セッションをリセットしました")

        except Exception as e:
            print(f"基盤セッションリセットエラー: {e}")

    def _update_board_display(self, board_number: int,is_delete:bool = False) -> None:
        """メインビューの基盤表示を更新"""
        if not self.main_view:
            return
            
        try:
            # 現在のモードを取得
            mode = self.main_view.get_current_mode()
            # 作成済み基盤の最大番号を取得
            max_number = self.get_board_max_number(mode,is_delete)
            # 現在の基盤番号を更新
            self.main_view.set_board_index_text(board_number, max_number)
            # 現在のJSONファイルのパスを設定する
            self.file_controller.set_current_json_path(board_number)
        except Exception as e:
            print(f"[ERROR] 基盤表示更新エラー: {e}")
            import traceback
            traceback.print_exc()
