"""
座標データモデル
座標とその詳細情報を管理
"""
from typing import List, Dict, Any, Optional, Tuple

from src.db.schema import Detail





class CoordinateModel:
    """座標データを管理するモデル"""
    
    def __init__(self):
        self._details: List[Detail] = []
        self._current_index: int = -1
        self._image_path: str = ""
        self._undo_stack: List[List[Detail]] = []
        self._redo_stack: List[List[Detail]] = []
        
    @property
    def coordinates(self) -> List[Tuple[int, int]]:
        """座標リストを取得（互換性のため）"""
        return [(d.x, d.y) for d in self._details]

    @property
    def coordinate_details(self) -> List[Dict[str, Any]]:
        """座標詳細リストを取得（互換性のため）"""
        return [d.model_dump() for d in self._details]

    @property
    def details(self) -> List[Detail]:
        """Detail型リストを取得"""
        return [d for d in self._details]
    
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
        print(f"Adding coordinate: x={x}, y={y}, detail={detail}")
        self._save_state_to_undo()
        # Detail型で追加
        if detail is None:
            d = Detail(x=x, y=y)
        else:
            d = Detail(x=x, y=y, **detail)
        self._details.append(d)
        return len(self._details) - 1
    
    def remove_coordinate(self, index: int) -> bool:
        """座標を削除"""
        if 0 <= index < len(self._details):
            self._save_state_to_undo()
            self._details.pop(index)
            if self._current_index >= index:
                self._current_index = max(-1, self._current_index - 1)
            return True
        return False
    
    def update_coordinate(self, index: int, x: int, y: int) -> bool:
        """座標を更新"""
        if 0 <= index < len(self._details):
            self._save_state_to_undo()
            self._details[index].x = x
            self._details[index].y = y
            return True
        return False
    
    def set_coordinate_detail(self, index: int, detail: Dict[str, Any]) -> bool:
        """座標の詳細情報を設定"""
        if 0 <= index < len(self._details):
            for k, v in detail.items():
                setattr(self._details[index], k, v)
            return True
        return False
    
    def get_coordinate_detail(self, index: int) -> Optional[Dict[str, Any]]:
        """座標の詳細情報を取得"""
        if 0 <= index < len(self._details):
            return self._details[index].model_dump()
        return None
    
    def set_current_coordinate(self, index: int) -> bool:
        """現在の座標を設定"""
        if -1 <= index < len(self._details):
            self._current_index = index
            return True
        return False
    
    def get_current_coordinate(self) -> Optional[Tuple[int, int]]:
        """現在選択中の座標を取得"""
        if 0 <= self._current_index < len(self._details):
            return (self._details[self._current_index].x, self._details[self._current_index].y)
        return None

    def get_current_coordinate_detail(self) -> Optional[Dict[str, Any]]:
        """現在選択中の座標の詳細情報を取得"""
        if 0 <= self._current_index < len(self._details):
            return self._details[self._current_index].model_dump()
        return None
    
    def clear_coordinates(self):
        """全座標をクリア"""
        self._save_state_to_undo()
        self._details.clear()
        self._current_index = -1

    def set_coordinates_with_details(self, coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]]):
        """座標と詳細情報を一括設定"""
        self._save_state_to_undo()
        self._details.clear()
        for i, (x, y) in enumerate(coordinates):
            detail = details[i] if i < len(details) else {}
            d = Detail(x=x, y=y, **detail)
            self._details.append(d)
    
    def set_image_path(self, path: str):
        """画像パスを設定"""
        self._image_path = path
    
    def _save_state_to_undo(self):
        """現在の状態をアンドゥスタックに保存"""
        import copy
        current_state = [copy.deepcopy(d) for d in self._details]
        self._undo_stack.append(current_state)
        self._redo_stack.clear()
        if len(self._undo_stack) > 50:
            self._undo_stack.pop(0)
    
    def undo(self) -> bool:
        """元に戻す"""
        import copy
        if self._undo_stack:
            current_state = [copy.deepcopy(d) for d in self._details]
            self._redo_stack.append(current_state)
            previous_state = self._undo_stack.pop()
            self._details = [copy.deepcopy(d) for d in previous_state]
            if self._current_index >= len(self._details):
                self._current_index = -1
            return True
        return False

    def redo(self) -> bool:
        import copy
        if self._redo_stack:
            current_state = [copy.deepcopy(d) for d in self._details]
            self._undo_stack.append(current_state)
            next_state = self._redo_stack.pop()
            self._details = [copy.deepcopy(d) for d in next_state]
            if self._current_index >= len(self._details):
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
            'total_count': len(self._details),
            'coordinates': [(d.x, d.y) for d in self._details],
            'details': [d.model_dump() for d in self._details],
            'current_index': self._current_index,
            'image_path': self._image_path
        }
