"""
Coordinate Manager Module
座標管理機能を担当するモジュール
"""

from PIL import Image, ImageTk


class CoordinateManager:
    """座標管理を担当するクラス"""
    
    def __init__(self, canvas_width=800, canvas_height=600):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.coordinates = []
        self.tk_img = None
        self.current_image_path = None
        
        # UndoRedo用の履歴管理
        self.history = []
        self.history_index = -1
        self.max_history = 50  # 最大履歴数
        
        # 初期状態を履歴に追加
        self._save_state()
        
    def _save_state(self):
        """現在の状態を履歴に保存"""
        # 現在のインデックス以降の履歴を削除
        self.history = self.history[:self.history_index + 1]
        
        # 新しい状態を追加
        current_state = self.coordinates.copy()
        self.history.append(current_state)
        
        # 履歴数制限
        if len(self.history) > self.max_history:
            self.history.pop(0)
        else:
            self.history_index += 1
    
    def can_undo(self):
        """Undoが可能かチェック"""
        return self.history_index > 0
    
    def can_redo(self):
        """Redoが可能かチェック"""
        return self.history_index < len(self.history) - 1
    
    def undo(self):
        """前の状態に戻す"""
        if self.can_undo():
            self.history_index -= 1
            self.coordinates = self.history[self.history_index].copy()
            return True
        return False
    
    def redo(self):
        """次の状態に進む"""
        if self.can_redo():
            self.history_index += 1
            self.coordinates = self.history[self.history_index].copy()
            return True
        return False
        
    def add_coordinate(self, x, y):
        """座標を追加"""
        self.coordinates.append((x, y))
        self._save_state()  # 状態を履歴に保存
        
    def remove_coordinate(self, index):
        """指定インデックスの座標を削除"""
        if 0 <= index < len(self.coordinates):
            return self.coordinates.pop(index)
        return None
        
    def clear_coordinates(self):
        """全座標をクリア"""
        self.coordinates.clear()
        self._save_state()  # 状態を履歴に保存
        
    def get_coordinates(self):
        """座標リストを取得"""
        return self.coordinates.copy()
        
    def set_coordinates(self, coordinates):
        """座標リストを設定"""
        self.coordinates = coordinates.copy()
        
    def load_image(self, image_path):
        """画像を読み込み"""
        try:
            img = Image.open(image_path)
            img = self._resize_image(img)
            self.tk_img = ImageTk.PhotoImage(img)
            self.current_image_path = image_path
            return self.tk_img
        except Exception as e:
            raise Exception(f"画像を開けませんでした: {e}")
            
    def _resize_image(self, img):
        """画像をキャンバスサイズに合わせてリサイズ"""
        img_ratio = img.width / img.height
        canvas_ratio = self.canvas_width / self.canvas_height

        if img_ratio > canvas_ratio:
            new_width = self.canvas_width
            new_height = int(self.canvas_width / img_ratio)
        else:
            new_height = self.canvas_height
            new_width = int(self.canvas_height * img_ratio)
            
        return img.resize((new_width, new_height), Image.LANCZOS)
        
    def draw_coordinate_marker(self, canvas, x, y, size=6):
        """座標マーカーを描画"""
        # X印を描画
        canvas.create_line(
            x - size, y - size, x + size, y + size, fill="white", width=3
        )
        canvas.create_line(
            x + size, y - size, x - size, y + size, fill="white", width=3
        )
        
    def redraw_all_markers(self, canvas):
        """すべての座標マーカーを再描画"""
        canvas.delete("all")
        
        # 画像を再描画
        if self.tk_img:
            canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            
        # 座標マーカーを再描画
        for x, y in self.coordinates:
            self.draw_coordinate_marker(canvas, x, y)
            
    def get_current_image(self):
        """現在の画像を取得"""
        return self.tk_img
        
    def get_current_image_path(self):
        """現在の画像パスを取得"""
        return self.current_image_path
