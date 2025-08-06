"""
Coordinate Controller
座標関連の操作を制御するコントローラー
"""

from typing import List, Tuple, Dict, Any, Callable, Optional
from ..models.coordinate_model import CoordinateModel
from ..models.image_model import ImageModel


class CoordinateController:
    """座標コントローラークラス"""
    
    def __init__(self, coordinate_model: CoordinateModel, image_model: ImageModel):
        self.coordinate_model = coordinate_model
        self.image_model = image_model
        self._callbacks: Dict[str, Callable] = {}
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self._callbacks.update(callbacks)
    
    def add_coordinate(self, x: int, y: int, detail: Dict[str, Any] = None) -> int:
        """座標を追加"""
        index = self.coordinate_model.add_coordinate(x, y, detail)
        
        # コールバックを呼び出し
        callback = self._callbacks.get('on_coordinate_added')
        if callback:
            callback((x, y), index)
        
        return index
    
    def select_coordinate(self, index: int) -> bool:
        """座標を選択"""
        if self.coordinate_model.set_current_coordinate(index):
            coordinates = self.coordinate_model.get_coordinates()
            if 0 <= index < len(coordinates):
                coordinate = coordinates[index]
                
                # コールバックを呼び出し
                callback = self._callbacks.get('on_coordinate_selected')
                if callback:
                    callback(index, coordinate)
                
                return True
        return False
    
    def find_nearest_coordinate(self, x: int, y: int, max_distance: float = 20) -> int:
        """指定座標に最も近い座標を検索"""
        return self.coordinate_model.find_nearest_coordinate(x, y, max_distance)
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """全座標を取得"""
        return self.coordinate_model.get_coordinates()
    
    def get_coordinate_details(self) -> List[Dict[str, Any]]:
        """全座標の詳細情報を取得"""
        return self.coordinate_model.get_coordinate_details()
    
    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在の座標の詳細情報を取得"""
        return self.coordinate_model.get_current_coordinate_detail()
    
    def update_current_coordinate_detail(self, detail: Dict[str, Any]) -> bool:
        """現在の座標の詳細情報を更新"""
        return self.coordinate_model.update_current_coordinate_detail(detail)
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if self.coordinate_model.remove_coordinate(index):
            # コールバックを呼び出し
            callback = self._callbacks.get('on_coordinates_updated')
            if callback:
                callback(self.coordinate_model.get_coordinates())
            return True
        return False
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self.coordinate_model.clear_coordinates()
        
        # コールバックを呼び出し
        callback = self._callbacks.get('on_coordinates_updated')
        if callback:
            callback([])
    
    def undo(self) -> bool:
        """元に戻す"""
        if self.coordinate_model.undo():
            # コールバックを呼び出し
            callback = self._callbacks.get('on_coordinates_updated')
            if callback:
                callback(self.coordinate_model.get_coordinates())
            return True
        return False
    
    def redo(self) -> bool:
        """やり直し"""
        if self.coordinate_model.redo():
            # コールバックを呼び出し
            callback = self._callbacks.get('on_coordinates_updated')
            if callback:
                callback(self.coordinate_model.get_coordinates())
            return True
        return False
    
    def get_coordinate_summary(self) -> Dict[str, Any]:
        """座標の概要情報を取得"""
        return self.coordinate_model.get_coordinate_summary()
    
    def set_coordinates_with_details(self, coordinates: List[Tuple[int, int]], 
                                   details: List[Dict[str, Any]]):
        """座標と詳細情報を一括設定"""
        self.coordinate_model.set_coordinates_with_details(coordinates, details)
        
        # コールバックを呼び出し
        callback = self._callbacks.get('on_coordinates_updated')
        if callback:
            callback(coordinates)
    
    def get_current_coordinate_index(self) -> int:
        """現在の座標インデックスを取得"""
        return self.coordinate_model.get_current_coordinate_index()
    
    def get_coordinate_count(self) -> int:
        """座標数を取得"""
        return self.coordinate_model.get_coordinate_count()
    
    def set_image_info(self, image_info: Dict[str, Any]):
        """画像情報を設定"""
        self.coordinate_model.set_image_info(image_info)
    
    def get_current_image_path(self) -> Optional[str]:
        """現在の画像パスを取得"""
        return self.coordinate_model.get_current_image_path()
    
    def validate_coordinate_position(self, x: int, y: int) -> bool:
        """座標位置が有効かチェック"""
        # 画像内にあるかチェック
        return self.image_model.is_point_in_image(x, y)
    
    def convert_display_to_original_coordinates(self, display_x: int, display_y: int) -> Optional[Tuple[int, int]]:
        """表示座標を元画像座標に変換"""
        return self.image_model.convert_display_to_original_coordinates(display_x, display_y)
    
    def convert_original_to_display_coordinates(self, original_x: int, original_y: int) -> Optional[Tuple[int, int]]:
        """元画像座標を表示座標に変換"""
        return self.image_model.convert_original_to_display_coordinates(original_x, original_y)
    
    def export_coordinates_data(self) -> Dict[str, Any]:
        """座標データをエクスポート用形式で取得"""
        return {
            'coordinates': self.coordinate_model.get_coordinates(),
            'coordinate_details': self.coordinate_model.get_coordinate_details(),
            'image_info': self.coordinate_model.get_image_info(),
            'summary': self.coordinate_model.get_coordinate_summary()
        }
    
    def import_coordinates_data(self, data: Dict[str, Any]):
        """座標データをインポート"""
        coordinates = data.get('coordinates', [])
        details = data.get('coordinate_details', [])
        image_info = data.get('image_info')
        
        self.coordinate_model.set_coordinates_with_details(coordinates, details)
        
        if image_info:
            self.coordinate_model.set_image_info(image_info)
        
        # コールバックを呼び出し
        callback = self._callbacks.get('on_coordinates_updated')
        if callback:
            callback(coordinates)
