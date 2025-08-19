"""
座標コントローラー
座標の管理と操作を制御
"""

import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from ..models.coordinate_model import CoordinateModel
    from ..models.image_model import ImageModel
    from ..views.coordinate_canvas_view import CoordinateCanvasView
    from ..views.sidebar_view import SidebarView
    from ..views.main_view import MainView


class CoordinateController:
    """座標操作を管理するコントローラー"""

    def __init__(self, coordinate_model: "CoordinateModel", image_model: "ImageModel"):
        self.coordinate_model = coordinate_model
        self.image_model = image_model

        # ビューへの参照（後で設定）
        self.canvas_view: Optional["CoordinateCanvasView"] = None
        self.sidebar_view: Optional["SidebarView"] = None
        self.main_view: Optional["MainView"] = None
        
        # ファイルコントローラーへの参照（自動保存用）
        self.file_controller = None
        
        # 現在の基盤番号（自動保存用）
        self.current_board_number = 1

    def set_canvas_view(self, canvas_view: "CoordinateCanvasView") -> None:
        """キャンバスビューを設定"""
        self.canvas_view = canvas_view

    def set_sidebar_view(self, sidebar_view: "SidebarView") -> None:
        """サイドバービューを設定"""
        self.sidebar_view = sidebar_view
    
    def set_main_view(self, main_view: "MainView") -> None:
        """メインビューを設定"""
        self.main_view = main_view
    
    def set_file_controller(self, file_controller) -> None:
        """ファイルコントローラーを設定"""
        self.file_controller = file_controller
    
    def set_current_board_number(self, board_number: int) -> None:
        """現在の基盤番号を設定"""
        self.current_board_number = board_number

    def add_coordinate(self, display_x: int, display_y: int) -> int:
        """座標を追加（表示座標から元座標に変換して保存）"""
        # 表示座標を元画像座標に変換
        orig_x, orig_y = self.image_model.convert_display_to_original_coords(
            display_x, display_y
        )

        # モデルに座標を追加
        index = self.coordinate_model.add_coordinate(orig_x, orig_y)

        # ビューにマーカーを追加
        if self.canvas_view:
            self.canvas_view.add_coordinate_marker(display_x, display_y, index + 1)

        # メインビューの座標表示を更新
        self._update_coordinate_display()
        
        # 自動保存処理
        self._auto_save_coordinates()

        return index

    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if self.coordinate_model.remove_coordinate(index):
            # ビューのマーカーを再描画
            self._redraw_all_markers()
            
            # メインビューの座標表示を更新
            self._update_coordinate_display()
            
            # 自動保存処理
            self._auto_save_coordinates()
            
            return True
        return False
    
    def clear_all_coordinates(self) -> None:
        """全座標をクリア"""
        self.coordinate_model.clear_coordinates()
        if self.canvas_view:
            self.canvas_view.clear_coordinate_markers()
            self.canvas_view.clear_highlight()

        # メインビューの座標表示を更新（クリア）
        self._update_coordinate_display()
        
        # 自動保存処理
        self._auto_save_coordinates()

    def update_coordinate(self, index: int, display_x: int, display_y: int) -> bool:
        """座標を更新"""
        # 表示座標を元画像座標に変換
        orig_x, orig_y = self.image_model.convert_display_to_original_coords(
            display_x, display_y
        )

        if self.coordinate_model.update_coordinate(index, orig_x, orig_y):
            # ビューのマーカーを再描画
            self._redraw_all_markers()
            
            # メインビューの座標表示を更新
            self._update_coordinate_display()
            
            # 自動保存処理
            self._auto_save_coordinates()
            
            return True
        return False

    def select_coordinate(
        self, display_x: int, display_y: int, max_distance: int = 20
    ) -> Optional[int]:
        """指定位置に最も近い座標を選択"""
        if not self.canvas_view:
            return None

        # 最寄りの座標を検索
        nearest_index = self.canvas_view.find_nearest_coordinate(
            display_x, display_y, max_distance
        )

        if nearest_index is not None:
            # モデルで座標を選択
            self.coordinate_model.set_current_coordinate(nearest_index)

            # ビューでハイライト
            self.canvas_view.highlight_coordinate(nearest_index)

            return nearest_index

        return None

    def set_current_coordinate(self, index: int) -> bool:
        """現在の座標を設定"""
        if self.coordinate_model.set_current_coordinate(index):
            # ビューでハイライト
            if self.canvas_view and index >= 0:
                self.canvas_view.highlight_coordinate(index)
            elif self.canvas_view:
                self.canvas_view.clear_highlight()

            # サイドバーに座標詳細を表示
            if self.sidebar_view and index >= 0:
                detail = self.coordinate_model.get_coordinate_detail(index)
                if detail:
                    # 座標詳細をサイドバーに表示
                    self.sidebar_view.set_coordinate_detail(detail)
                else:
                    # 詳細がない場合はフォームをクリア
                    self.sidebar_view.clear_form()
            elif self.sidebar_view:
                self.sidebar_view.clear_form()

            # メインビューの座標表示を更新
            self._update_coordinate_display()

            return True
        return False

    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在選択中の座標の詳細情報を取得"""
        return self.coordinate_model.get_current_coordinate_detail()

    def update_current_coordinate_detail(self, detail: Dict[str, Any]) -> bool:
        """現在選択中の座標の詳細情報を更新"""
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            result = self.coordinate_model.set_coordinate_detail(current_index, detail)
            if result:
                # 自動保存処理
                self._auto_save_coordinates()
            return result
        return False

    def clear_coordinates(self) -> None:
        """全座標をクリア"""
        self.coordinate_model.clear_coordinates()
        if self.canvas_view:
            self.canvas_view.clear_coordinate_markers()
            self.canvas_view.clear_highlight()
        
        # メインビューの座標表示を更新（クリア）
        self._update_coordinate_display()

    def undo(self) -> bool:
        """元に戻す"""
        if self.coordinate_model.undo():
            self._redraw_all_markers()
            
            # メインビューの座標表示を更新
            self._update_coordinate_display()
            
            return True
        return False

    def redo(self) -> bool:
        """やり直し"""
        if self.coordinate_model.redo():
            self._redraw_all_markers()
            
            # メインビューの座標表示を更新
            self._update_coordinate_display()
            
            return True
        return False

    def can_undo(self) -> bool:
        """アンドゥ可能かどうか"""
        return self.coordinate_model.can_undo()

    def can_redo(self) -> bool:
        """リドゥ可能かどうか"""
        return self.coordinate_model.can_redo()

    def load_coordinates_from_data(
        self, coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]]
    ) -> None:
        """座標データを読み込み"""
        # モデルに設定
        self.coordinate_model.set_coordinates_with_details(coordinates, details)

        # ビューのマーカーを再描画
        self._redraw_all_markers()
        
        # メインビューの座標表示を更新
        self._update_coordinate_display()

    def _redraw_all_markers(self) -> None:
        """全マーカーを再描画"""
        if not self.canvas_view:
            return

        # 元画像座標を表示座標に変換して描画
        display_coordinates = []
        for orig_x, orig_y in self.coordinate_model.coordinates:
            display_x, display_y = self.image_model.convert_original_to_display_coords(
                orig_x, orig_y
            )
            display_coordinates.append((display_x, display_y))

        self.canvas_view.redraw_coordinate_markers(display_coordinates)

        # 現在選択中の座標をハイライト
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            self.canvas_view.highlight_coordinate(current_index)

    def get_coordinate_summary(self) -> Dict[str, Any]:
        """座標概要を取得"""
        summary = self.coordinate_model.get_coordinate_summary()

        # 表示用に元座標を変換
        display_coordinates = []
        for orig_x, orig_y in summary["coordinates"]:
            display_x, display_y = self.image_model.convert_original_to_display_coords(
                orig_x, orig_y
            )
            display_coordinates.append((display_x, display_y))

        summary["display_coordinates"] = display_coordinates
        return summary

    def get_all_coordinates(self) -> List[Tuple[int, int]]:
        """全座標を取得（元画像座標）"""
        return self.coordinate_model.coordinates

    def get_all_coordinate_details(self) -> List[Dict[str, Any]]:
        """全座標詳細を取得"""
        return self.coordinate_model.coordinate_details

    def load_models_from_file(self, settings_model: Any) -> List[Dict[str, str]]:
        """設定で指定された画像ディレクトリから画像ファイル名を読み込み

        Args:
            settings_model: 設定モデル

        Returns:
            List[Dict[str, str]]: [{"filename": "フルパス"}, ...] 形式のリスト
        """
        try:
            image_directory = settings_model.image_directory

            if image_directory and image_directory != "未選択":
                # 画像ディレクトリから画像ファイル名とフルパスを取得
                image_files_dict = self._get_image_files_with_paths(image_directory)

                if image_files_dict:
                    return image_files_dict
                else:
                    # 画像ファイルが見つからない場合
                    return [
                        {"画像なし": f"画像なし（{os.path.basename(image_directory)}）"}
                    ]
            else:
                # 画像ディレクトリが設定されていない場合
                return [{"画像ディレクトリが未設定": "画像ディレクトリが未設定"}]

        except Exception as e:
            # エラーが発生した場合はデフォルト値を返す
            print(f"画像ファイル読み込みエラー: {e}")
            return [{"設定エラー": "設定エラー"}]

    def _get_image_files_with_paths(self, directory: str) -> List[Dict[str, str]]:
        """指定されたディレクトリから画像ファイル名とフルパスの辞書リストを取得

        Args:
            directory: 検索対象のディレクトリパス

        Returns:
            List[Dict[str, str]]: [{"filename": "フルパス"}, ...] 形式のリスト
        """
        if not directory or not os.path.exists(directory):
            return []

        # サポートする画像拡張子
        supported_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}

        image_files = []
        try:
            for filename in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, filename)):
                    # ファイルの拡張子をチェック
                    name_without_ext, ext = os.path.splitext(filename)
                    if ext.lower() in supported_extensions:
                        # フルパスを作成
                        full_path = os.path.join(directory, filename)
                        # 拡張子なしのファイル名をキーとして使用
                        image_files.append({name_without_ext: full_path})

            return image_files

        except Exception as e:
            print(f"画像ファイル取得エラー: {e}")
            return []

    def delete_coordinate(self, index: int) -> bool:
        """指定されたインデックスの座標を削除

        Args:
            index: 削除する座標のインデックス

        Returns:
            bool: 削除に成功した場合True
        """
        try:
            coordinates = self.coordinate_model.coordinates
            if 0 <= index < len(coordinates):
                total_coordinates = len(coordinates)

                # 座標を削除（remove_coordinateメソッド内でアンドゥ用状態保存も実行される）
                self.coordinate_model.remove_coordinate(index)

                # 残った座標がある場合は適切な座標を選択
                remaining_coordinates = len(self.coordinate_model.coordinates)
                if remaining_coordinates > 0:
                    # 削除したインデックスの位置に座標がまだある場合はそれを選択
                    if index < remaining_coordinates:
                        new_index = index
                    # 削除したのが最後の座標の場合は、前の座標を選択
                    else:
                        new_index = remaining_coordinates - 1

                    self.coordinate_model.set_current_coordinate(new_index)
                else:
                    # 座標が全て削除された場合
                    self.coordinate_model.set_current_coordinate(-1)

                return True
            return False

        except Exception as e:
            print(f"座標削除エラー: {e}")
            return False

    def delete_selected_coordinate(self) -> bool:
        """現在選択中の座標を削除"""
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            success = self.delete_coordinate(current_index)
            if success:
                self._redraw_all_markers()

                # 削除後に選択された座標がある場合は、その詳細をサイドバーに表示
                new_current_index = self.coordinate_model.current_index
                if self.sidebar_view:
                    if new_current_index >= 0:
                        # 新しく選択された座標の詳細を表示
                        detail = self.coordinate_model.get_coordinate_detail(
                            new_current_index
                        )
                        if detail:
                            # 項目番号を更新
                            detail_with_item = detail.copy()
                            detail_with_item["item_number"] = str(new_current_index + 1)
                            self.sidebar_view.set_coordinate_detail(detail_with_item)
                        else:
                            # 詳細がない場合は項目番号のみ設定
                            self.sidebar_view.set_coordinate_detail(
                                {"item_number": str(new_current_index + 1)}
                            )
                    else:
                        # 座標が全て削除された場合はフォームをクリア
                        self.sidebar_view.clear_form()

                # メインビューの座標表示を更新
                self._update_coordinate_display()

            return success
        return False

    def select_previous_coordinate(self) -> bool:
        """前の座標を選択"""
        current_index = self.coordinate_model.current_index
        coordinates = self.coordinate_model.coordinates

        if not coordinates:
            return False

        if current_index <= 0:
            # 最初の座標または未選択の場合、最後の座標を選択
            new_index = len(coordinates) - 1
        else:
            new_index = current_index - 1

        result = self.set_current_coordinate(new_index)
        
        # メインビューの座標表示を更新（set_current_coordinateでも呼ばれるが明示的に）
        self._update_coordinate_display()
        
        return result

    def select_next_coordinate(self) -> bool:
        """次の座標を選択"""
        current_index = self.coordinate_model.current_index
        coordinates = self.coordinate_model.coordinates

        if not coordinates:
            return False

        if current_index >= len(coordinates) - 1 or current_index < 0:
            # 最後の座標または未選択の場合、最初の座標を選択
            new_index = 0
        else:
            new_index = current_index + 1

        result = self.set_current_coordinate(new_index)
        
        # メインビューの座標表示を更新（set_current_coordinateでも呼ばれるが明示的に）
        self._update_coordinate_display()
        
        return result

    def _update_coordinate_display(self) -> None:
        """メインビューの座標表示を更新"""
        if not self.main_view:
            return
            
        try:
            # 座標データを取得
            coordinates = self.coordinate_model.coordinates
            current_index = self.coordinate_model.current_index
            
            # 座標データを辞書形式に変換（update_coordinate_display_realtimeが期待する形式）
            coordinates_data = []
            for i, (x, y) in enumerate(coordinates):
                coordinates_data.append({
                    "index": i,
                    "x": x,
                    "y": y
                })
            
            # メインビューの座標表示を更新
            self.main_view.update_coordinate_display_realtime(coordinates_data, current_index)
            
            print(f"[DEBUG] 座標表示更新: {len(coordinates_data)}個の座標, 選択インデックス: {current_index}")
            
        except Exception as e:
            print(f"[ERROR] 座標表示更新エラー: {e}")
            import traceback
            traceback.print_exc()
    
    def _auto_save_coordinates(self) -> None:
        """座標データを自動保存"""
        try:
            # FileControllerが設定されていない場合は何もしない
            if not self.file_controller:
                print("[DEBUG] FileControllerが設定されていません - 自動保存をスキップ")
                return
                
            # 座標データと詳細情報を取得
            coordinates = self.coordinate_model.coordinates
            coordinate_details = self.coordinate_model.coordinate_details
            
            # 座標がない場合もファイルを更新（空の状態で保存）
            print(f"[DEBUG] 自動保存実行: {len(coordinates)}個の座標, 基盤番号: {self.current_board_number}")
            
            # FileControllerを使用してJSONファイルを更新
            file_path = self.file_controller.create_defective_info_file(
                self.current_board_number, 
                coordinates, 
                coordinate_details
            )
            
            if file_path:
                print(f"[DEBUG] 自動保存成功: {file_path}")
            else:
                print("[WARNING] 自動保存に失敗しました")
                
        except Exception as e:
            print(f"[ERROR] 自動保存エラー: {e}")
            import traceback
            traceback.print_exc()
