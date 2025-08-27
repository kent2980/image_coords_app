"""
座標データモデル
座標とその詳細情報を管理
"""
from typing import List, Dict, Any, Optional, Tuple


class CoordinateItem:
    """座標アイテム（座標と詳細情報を統合）"""
    
    def __init__(self, x: int, y: int, detail: Optional[Dict[str, Any]] = None):
        self.x = x
        self.y = y
        self.detail = detail or {}
    
    @property
    def coordinate(self) -> Tuple[int, int]:
        """座標タプルを取得"""
        return (self.x, self.y)
    
    def update_coordinate(self, x: int, y: int):
        """座標を更新"""
        self.x = x
        self.y = y
    
    def update_detail(self, detail: Dict[str, Any]):
        """詳細情報を更新"""
        self.detail = detail.copy()
    
    def get_detail(self) -> Dict[str, Any]:
        """詳細情報を取得"""
        return self.detail.copy()
    
    def copy(self) -> 'CoordinateItem':
        """コピーを作成"""
        return CoordinateItem(self.x, self.y, self.detail.copy())


class CoordinateModel:
    """座標データを管理するモデル"""
    
    def __init__(self):
        self._coordinate_items: List[CoordinateItem] = []
        self._current_index: int = -1
        self._image_path: str = ""
        self._undo_stack: List[List[CoordinateItem]] = []
        self._redo_stack: List[List[CoordinateItem]] = []
        
    @property
    def coordinates(self) -> List[Tuple[int, int]]:
        """座標リストを取得（互換性のため）"""
        return [item.coordinate for item in self._coordinate_items]
    
    @property
    def coordinate_details(self) -> List[Dict[str, Any]]:
        """座標詳細リストを取得（互換性のため）"""
        return [item.get_detail() for item in self._coordinate_items]
    
    @property
    def coordinate_items(self) -> List[CoordinateItem]:
        """座標アイテムリストを取得"""
        return [item.copy() for item in self._coordinate_items]
    
    @property
    def current_index(self) -> int:
        """現在選択中の座標インデックス"""
        return self._current_index
    
    @property
    def image_path(self) -> str:
        """画像パス"""
        return self._image_path
        
    def add_coordinate(self, x: int, y: int, detail: Optional[Dict[str, Any]] = None) -> int:
        """座標を追加"""
        # アンドゥスタックに現在の状態を保存
        self._save_state_to_undo()
        
        # 新しい座標アイテムを作成して追加
        coordinate_item = CoordinateItem(x, y, detail)
        self._coordinate_items.append(coordinate_item)
        
        # 新しい座標のインデックスを返す
        return len(self._coordinate_items) - 1
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if 0 <= index < len(self._coordinate_items):
            self._save_state_to_undo()
            
            self._coordinate_items.pop(index)
            
            # 現在のインデックスを調整
            if self._current_index >= index:
                self._current_index = max(-1, self._current_index - 1)
                
            return True
        return False
    
    def update_coordinate(self, index: int, x: int, y: int) -> bool:
        """座標を更新"""
        if 0 <= index < len(self._coordinate_items):
            self._save_state_to_undo()
            self._coordinate_items[index].update_coordinate(x, y)
            return True
        return False
    
    def set_coordinate_detail(self, index: int, detail: Dict[str, Any]) -> bool:
        """座標の詳細情報を設定"""
        if 0 <= index < len(self._coordinate_items):
            self._coordinate_items[index].update_detail(detail)
            return True
        return False
    
    def get_coordinate_detail(self, index: int) -> Optional[Dict[str, Any]]:
        """座標の詳細情報を取得"""
        if 0 <= index < len(self._coordinate_items):
            return self._coordinate_items[index].get_detail()
        return None
    
    def set_current_coordinate(self, index: int) -> bool:
        """現在の座標を設定"""
        if -1 <= index < len(self._coordinate_items):
            self._current_index = index
            return True
        return False
    
    def get_current_coordinate(self) -> Optional[Tuple[int, int]]:
        """現在選択中の座標を取得"""
        if 0 <= self._current_index < len(self._coordinate_items):
            return self._coordinate_items[self._current_index].coordinate
        return None
    
    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在選択中の座標の詳細情報を取得"""
        if 0 <= self._current_index < len(self._coordinate_items):
            return self._coordinate_items[self._current_index].get_detail()
        return None
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self._save_state_to_undo()
        self._coordinate_items.clear()
        self._current_index = -1
    
    def set_coordinates_with_details(self, coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]]):
        """座標と詳細情報を一括設定"""
        self._save_state_to_undo()
        self._coordinate_items.clear()
        
        # 座標と詳細情報を統合してCoordinateItemを作成
        for i, (x, y) in enumerate(coordinates):
            detail = details[i] if i < len(details) else {}
            self._coordinate_items.append(CoordinateItem(x, y, detail))
    
    def set_image_path(self, path: str):
        """画像パスを設定"""
        self._image_path = path
    
    def _save_state_to_undo(self):
        """現在の状態をアンドゥスタックに保存"""
        current_state = [item.copy() for item in self._coordinate_items]
        self._undo_stack.append(current_state)
        # リドゥスタックをクリア
        self._redo_stack.clear()
        
        # スタックサイズを制限（メモリ使用量を制御）
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
    
    def undo(self) -> bool:
        """元に戻す"""
        if self._undo_stack:
            # 現在の状態をリドゥスタックに保存
            current_state = [item.copy() for item in self._coordinate_items]
            self._redo_stack.append(current_state)
            
            # 前の状態を復元
            previous_state = self._undo_stack.pop()
            self._coordinate_items = [item.copy() for item in previous_state]
            
            # 現在のインデックスを調整
            if self._current_index >= len(self._coordinate_items):
                self._current_index = -1
            
            return True
        return False
    
    def redo(self) -> bool:
        """やり直し"""
        if self._redo_stack:
            # 現在の状態をアンドゥスタックに保存
            current_state = [item.copy() for item in self._coordinate_items]
            self._undo_stack.append(current_state)
            
            # リドゥスタックから状態を復元
            next_state = self._redo_stack.pop()
            self._coordinate_items = [item.copy() for item in next_state]
            
            # 現在のインデックスを調整
            if self._current_index >= len(self._coordinate_items):
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
            'total_count': len(self._coordinate_items),
            'coordinates': [item.coordinate for item in self._coordinate_items],
            'details': [item.get_detail() for item in self._coordinate_items],
            'current_index': self._current_index,
            'image_path': self._image_path
        }
