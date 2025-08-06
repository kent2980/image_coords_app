"""
座標データモデル
座標とその詳細情報を管理
"""
from typing import List, Dict, Any, Optional, Tuple


class CoordinateModel:
    """座標データを管理するモデル"""
    
    def __init__(self):
        self._coordinates: List[Tuple[int, int]] = []
        self._coordinate_details: List[Dict[str, Any]] = []
        self._current_index: int = -1
        self._image_path: str = ""
        self._undo_stack: List[List[Tuple[int, int]]] = []
        self._redo_stack: List[List[Tuple[int, int]]] = []
        
    @property
    def coordinates(self) -> List[Tuple[int, int]]:
        """座標リストを取得"""
        return self._coordinates.copy()
    
    @property
    def coordinate_details(self) -> List[Dict[str, Any]]:
        """座標詳細リストを取得"""
        return self._coordinate_details.copy()
    
    @property
    def current_index(self) -> int:
        """現在選択中の座標インデックス"""
        return self._current_index
    
    @property
    def image_path(self) -> str:
        """画像パス"""
        return self._image_path
        
    def add_coordinate(self, x: int, y: int) -> int:
        """座標を追加"""
        # アンドゥスタックに現在の状態を保存
        self._save_state_to_undo()
        
        self._coordinates.append((x, y))
        # 詳細情報も空の辞書で初期化
        self._coordinate_details.append({})
        
        # 新しい座標のインデックスを返す
        return len(self._coordinates) - 1
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if 0 <= index < len(self._coordinates):
            self._save_state_to_undo()
            
            self._coordinates.pop(index)
            self._coordinate_details.pop(index)
            
            # 現在のインデックスを調整
            if self._current_index >= index:
                self._current_index = max(-1, self._current_index - 1)
                
            return True
        return False
    
    def update_coordinate(self, index: int, x: int, y: int) -> bool:
        """座標を更新"""
        if 0 <= index < len(self._coordinates):
            self._save_state_to_undo()
            self._coordinates[index] = (x, y)
            return True
        return False
    
    def set_coordinate_detail(self, index: int, detail: Dict[str, Any]) -> bool:
        """座標の詳細情報を設定"""
        if 0 <= index < len(self._coordinate_details):
            self._coordinate_details[index] = detail.copy()
            return True
        return False
    
    def get_coordinate_detail(self, index: int) -> Optional[Dict[str, Any]]:
        """座標の詳細情報を取得"""
        if 0 <= index < len(self._coordinate_details):
            return self._coordinate_details[index].copy()
        return None
    
    def set_current_coordinate(self, index: int) -> bool:
        """現在の座標を設定"""
        if -1 <= index < len(self._coordinates):
            self._current_index = index
            return True
        return False
    
    def get_current_coordinate(self) -> Optional[Tuple[int, int]]:
        """現在選択中の座標を取得"""
        if 0 <= self._current_index < len(self._coordinates):
            return self._coordinates[self._current_index]
        return None
    
    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在選択中の座標の詳細情報を取得"""
        if 0 <= self._current_index < len(self._coordinate_details):
            return self._coordinate_details[self._current_index].copy()
        return None
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self._save_state_to_undo()
        self._coordinates.clear()
        self._coordinate_details.clear()
        self._current_index = -1
    
    def set_coordinates_with_details(self, coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]]):
        """座標と詳細情報を一括設定"""
        self._save_state_to_undo()
        self._coordinates = coordinates.copy()
        self._coordinate_details = details.copy()
        
        # 詳細情報の数を座標数に合わせる
        while len(self._coordinate_details) < len(self._coordinates):
            self._coordinate_details.append({})
    
    def set_image_path(self, path: str):
        """画像パスを設定"""
        self._image_path = path
    
    def _save_state_to_undo(self):
        """現在の状態をアンドゥスタックに保存"""
        self._undo_stack.append(self._coordinates.copy())
        # リドゥスタックをクリア
        self._redo_stack.clear()
        
        # スタックサイズを制限（メモリ使用量を制御）
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
    
    def undo(self) -> bool:
        """元に戻す"""
        if self._undo_stack:
            # 現在の状態をリドゥスタックに保存
            self._redo_stack.append(self._coordinates.copy())
            
            # 前の状態を復元
            self._coordinates = self._undo_stack.pop()
            
            # 詳細情報のサイズを調整
            while len(self._coordinate_details) > len(self._coordinates):
                self._coordinate_details.pop()
            while len(self._coordinate_details) < len(self._coordinates):
                self._coordinate_details.append({})
            
            # 現在のインデックスを調整
            if self._current_index >= len(self._coordinates):
                self._current_index = -1
            
            return True
        return False
    
    def redo(self) -> bool:
        """やり直し"""
        if self._redo_stack:
            # 現在の状態をアンドゥスタックに保存
            self._undo_stack.append(self._coordinates.copy())
            
            # リドゥスタックから状態を復元
            self._coordinates = self._redo_stack.pop()
            
            # 詳細情報のサイズを調整
            while len(self._coordinate_details) > len(self._coordinates):
                self._coordinate_details.pop()
            while len(self._coordinate_details) < len(self._coordinates):
                self._coordinate_details.append({})
            
            # 現在のインデックスを調整
            if self._current_index >= len(self._coordinates):
                self._current_index = -1
            
            return True
        return False
    
    def can_undo(self) -> bool:
        """アンドゥ可能かどうか"""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """リドゥ可能かどうか"""
        return len(self._redo_stack) > 0
    
    def get_coordinate_summary(self) -> Dict[str, Any]:
        """座標の概要情報を取得"""
        return {
            'total_count': len(self._coordinates),
            'coordinates': self._coordinates.copy(),
            'details': self._coordinate_details.copy(),
            'current_index': self._current_index,
            'image_path': self._image_path
        }
