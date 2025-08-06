"""
座標コントローラー
座標の管理と操作を制御
"""
from typing import Tuple, Optional, List, Dict, Any


class CoordinateController:
    """座標操作を管理するコントローラー"""
    
    def __init__(self, coordinate_model, image_model):
        self.coordinate_model = coordinate_model
        self.image_model = image_model
        
        # ビューへの参照（後で設定）
        self.canvas_view = None
    
    def set_canvas_view(self, canvas_view):
        """キャンバスビューを設定"""
        self.canvas_view = canvas_view
    
    def add_coordinate(self, display_x: int, display_y: int) -> int:
        """座標を追加（表示座標から元座標に変換して保存）"""
        # 表示座標を元画像座標に変換
        orig_x, orig_y = self.image_model.convert_display_to_original_coords(display_x, display_y)
        
        # モデルに座標を追加
        index = self.coordinate_model.add_coordinate(orig_x, orig_y)
        
        # ビューにマーカーを追加
        if self.canvas_view:
            self.canvas_view.add_coordinate_marker(display_x, display_y, index + 1)
        
        return index
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if self.coordinate_model.remove_coordinate(index):
            # ビューのマーカーを再描画
            self._redraw_all_markers()
            return True
        return False
    
    def update_coordinate(self, index: int, display_x: int, display_y: int) -> bool:
        """座標を更新"""
        # 表示座標を元画像座標に変換
        orig_x, orig_y = self.image_model.convert_display_to_original_coords(display_x, display_y)
        
        if self.coordinate_model.update_coordinate(index, orig_x, orig_y):
            # ビューのマーカーを再描画
            self._redraw_all_markers()
            return True
        return False
    
    def select_coordinate(self, display_x: int, display_y: int, max_distance: int = 20) -> Optional[int]:
        """指定位置に最も近い座標を選択"""
        if not self.canvas_view:
            return None
        
        # 最寄りの座標を検索
        nearest_index = self.canvas_view.find_nearest_coordinate(display_x, display_y, max_distance)
        
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
            return True
        return False
    
    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在選択中の座標の詳細情報を取得"""
        return self.coordinate_model.get_current_coordinate_detail()
    
    def update_current_coordinate_detail(self, detail: Dict[str, Any]) -> bool:
        """現在選択中の座標の詳細情報を更新"""
        current_index = self.coordinate_model.current_index
        if current_index >= 0:
            return self.coordinate_model.set_coordinate_detail(current_index, detail)
        return False
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self.coordinate_model.clear_coordinates()
        if self.canvas_view:
            self.canvas_view.clear_coordinate_markers()
            self.canvas_view.clear_highlight()
    
    def undo(self) -> bool:
        """元に戻す"""
        if self.coordinate_model.undo():
            self._redraw_all_markers()
            return True
        return False
    
    def redo(self) -> bool:
        """やり直し"""
        if self.coordinate_model.redo():
            self._redraw_all_markers()
            return True
        return False
    
    def can_undo(self) -> bool:
        """アンドゥ可能かどうか"""
        return self.coordinate_model.can_undo()
    
    def can_redo(self) -> bool:
        """リドゥ可能かどうか"""
        return self.coordinate_model.can_redo()
    
    def load_coordinates_from_data(self, coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]]):
        """座標データを読み込み"""
        # モデルに設定
        self.coordinate_model.set_coordinates_with_details(coordinates, details)
        
        # ビューのマーカーを再描画
        self._redraw_all_markers()
    
    def _redraw_all_markers(self):
        """全マーカーを再描画"""
        if not self.canvas_view:
            return
        
        # 元画像座標を表示座標に変換して描画
        display_coordinates = []
        for orig_x, orig_y in self.coordinate_model.coordinates:
            display_x, display_y = self.image_model.convert_original_to_display_coords(orig_x, orig_y)
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
        for orig_x, orig_y in summary['coordinates']:
            display_x, display_y = self.image_model.convert_original_to_display_coords(orig_x, orig_y)
            display_coordinates.append((display_x, display_y))
        
        summary['display_coordinates'] = display_coordinates
        return summary
    
    def get_all_coordinates(self) -> List[Tuple[int, int]]:
        """全座標を取得（元画像座標）"""
        return self.coordinate_model.coordinates
    
    def get_all_coordinate_details(self) -> List[Dict[str, Any]]:
        """全座標詳細を取得"""
        return self.coordinate_model.coordinate_details
