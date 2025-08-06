"""
Coordinate Model
座標データとその詳細情報を管理するモデル
"""

from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import json


class CoordinateModel:
    """座標データモデル"""
    
    def __init__(self):
        self._coordinates: List[Tuple[int, int]] = []
        self._coordinate_details: List[Dict[str, Any]] = []
        self._current_index: int = -1
        self._history: List[List[Tuple[int, int]]] = []
        self._history_index: int = -1
        self._image_info: Optional[Dict[str, Any]] = None
        
    def add_coordinate(self, x: int, y: int, detail: Dict[str, Any] = None) -> int:
        """座標を追加"""
        self._coordinates.append((x, y))
        
        # デフォルトの詳細情報を作成
        if detail is None:
            detail = {
                'item_number': str(len(self._coordinates)),
                'reference': '',
                'defect': '',
                'comment': '',
                'repaired': 'いいえ',
                'timestamp': datetime.now().isoformat()
            }
        
        self._coordinate_details.append(detail)
        
        # 履歴に追加
        self._save_to_history()
        
        return len(self._coordinates) - 1
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if 0 <= index < len(self._coordinates):
            self._coordinates.pop(index)
            self._coordinate_details.pop(index)
            
            # アイテム番号を再計算
            for i, detail in enumerate(self._coordinate_details):
                detail['item_number'] = str(i + 1)
            
            # 現在のインデックスを調整
            if self._current_index >= index:
                self._current_index = max(-1, self._current_index - 1)
            
            self._save_to_history()
            return True
        return False
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """全座標を取得"""
        return self._coordinates.copy()
    
    def get_coordinate_details(self) -> List[Dict[str, Any]]:
        """全座標の詳細情報を取得"""
        return self._coordinate_details.copy()
    
    def get_coordinate_count(self) -> int:
        """座標数を取得"""
        return len(self._coordinates)
    
    def set_current_coordinate(self, index: int) -> bool:
        """現在の座標を設定"""
        if 0 <= index < len(self._coordinates):
            self._current_index = index
            return True
        self._current_index = -1
        return False
    
    def get_current_coordinate_index(self) -> int:
        """現在の座標インデックスを取得"""
        return self._current_index
    
    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在の座標の詳細情報を取得"""
        if 0 <= self._current_index < len(self._coordinate_details):
            return self._coordinate_details[self._current_index].copy()
        return None
    
    def update_current_coordinate_detail(self, detail: Dict[str, Any]) -> bool:
        """現在の座標の詳細情報を更新"""
        if 0 <= self._current_index < len(self._coordinate_details):
            # タイムスタンプを更新
            detail['timestamp'] = datetime.now().isoformat()
            self._coordinate_details[self._current_index].update(detail)
            return True
        return False
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self._coordinates.clear()
        self._coordinate_details.clear()
        self._current_index = -1
        self._save_to_history()
    
    def set_coordinates_with_details(self, coordinates: List[Tuple[int, int]], 
                                   details: List[Dict[str, Any]]):
        """座標と詳細情報を一括設定"""
        self._coordinates = coordinates.copy()
        self._coordinate_details = details.copy()
        
        # 詳細情報が不足している場合は補完
        while len(self._coordinate_details) < len(self._coordinates):
            self._coordinate_details.append({
                'item_number': str(len(self._coordinate_details) + 1),
                'reference': '',
                'defect': '',
                'comment': '',
                'repaired': 'いいえ',
                'timestamp': datetime.now().isoformat()
            })
        
        self._current_index = -1
        self._save_to_history()
    
    def find_nearest_coordinate(self, x: int, y: int, max_distance: float = 20) -> int:
        """指定座標に最も近い座標のインデックスを取得"""
        min_distance = float('inf')
        nearest_index = -1
        
        for i, (coord_x, coord_y) in enumerate(self._coordinates):
            distance = ((x - coord_x) ** 2 + (y - coord_y) ** 2) ** 0.5
            if distance < max_distance and distance < min_distance:
                min_distance = distance
                nearest_index = i
        
        return nearest_index
    
    def get_coordinate_summary(self) -> Dict[str, Any]:
        """座標の概要情報を取得"""
        total_count = len(self._coordinates)
        repaired_count = sum(1 for detail in self._coordinate_details 
                           if detail.get('repaired') == 'はい')
        unrepaired_count = total_count - repaired_count
        
        # 不良種別の集計
        defect_counts = {}
        for detail in self._coordinate_details:
            defect = detail.get('defect', '')
            if defect:
                defect_counts[defect] = defect_counts.get(defect, 0) + 1
        
        return {
            'total_count': total_count,
            'repaired_count': repaired_count,
            'unrepaired_count': unrepaired_count,
            'defect_counts': defect_counts
        }
    
    def set_image_info(self, image_info: Dict[str, Any]):
        """画像情報を設定"""
        self._image_info = image_info.copy()
    
    def get_image_info(self) -> Optional[Dict[str, Any]]:
        """画像情報を取得"""
        return self._image_info.copy() if self._image_info else None
    
    def get_current_image_path(self) -> Optional[str]:
        """現在の画像パスを取得"""
        return self._image_info.get('image_path') if self._image_info else None
    
    def _save_to_history(self):
        """現在の状態を履歴に保存"""
        # 現在位置より後の履歴を削除
        self._history = self._history[:self._history_index + 1]
        
        # 新しい状態を追加
        self._history.append(self._coordinates.copy())
        self._history_index += 1
        
        # 履歴のサイズ制限（最大50回）
        if len(self._history) > 50:
            self._history.pop(0)
            self._history_index -= 1
    
    def undo(self) -> bool:
        """元に戻す"""
        if self._history_index > 0:
            self._history_index -= 1
            self._coordinates = self._history[self._history_index].copy()
            
            # 詳細情報のサイズを調整
            while len(self._coordinate_details) > len(self._coordinates):
                self._coordinate_details.pop()
            while len(self._coordinate_details) < len(self._coordinates):
                self._coordinate_details.append({
                    'item_number': str(len(self._coordinate_details) + 1),
                    'reference': '',
                    'defect': '',
                    'comment': '',
                    'repaired': 'いいえ',
                    'timestamp': datetime.now().isoformat()
                })
            
            self._current_index = -1
            return True
        return False
    
    def redo(self) -> bool:
        """やり直し"""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._coordinates = self._history[self._history_index].copy()
            
            # 詳細情報のサイズを調整
            while len(self._coordinate_details) > len(self._coordinates):
                self._coordinate_details.pop()
            while len(self._coordinate_details) < len(self._coordinates):
                self._coordinate_details.append({
                    'item_number': str(len(self._coordinate_details) + 1),
                    'reference': '',
                    'defect': '',
                    'comment': '',
                    'repaired': 'いいえ',
                    'timestamp': datetime.now().isoformat()
                })
            
            self._current_index = -1
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式でデータを取得"""
        return {
            'coordinates': self._coordinates,
            'coordinate_details': self._coordinate_details,
            'current_index': self._current_index,
            'image_info': self._image_info
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """辞書からデータを復元"""
        self._coordinates = data.get('coordinates', [])
        self._coordinate_details = data.get('coordinate_details', [])
        self._current_index = data.get('current_index', -1)
        self._image_info = data.get('image_info')
        self._save_to_history()
