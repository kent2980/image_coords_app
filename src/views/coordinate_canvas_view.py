"""
Coordinate Canvas View
座標表示用キャンバスビュー
"""

import tkinter as tk
from typing import List, Tuple, Optional, Callable, Dict, Any
from PIL import ImageTk


class CoordinateCanvasView:
    """座標キャンバスビュークラス"""
    
    def __init__(self, parent_frame: tk.Frame, width: int = 800, height: int = 600):
        self.parent_frame = parent_frame
        self.width = width
        self.height = height
        
        # キャンバスを作成
        self.canvas = tk.Canvas(
            self.parent_frame,
            width=self.width,
            height=self.height,
            bg='white'
        )
        self.canvas.pack()
        
        # 現在の画像
        self._current_image: Optional[ImageTk.PhotoImage] = None
        self._image_item_id: Optional[int] = None
        
        # マーカー管理
        self._coordinate_markers: List[int] = []  # キャンバスアイテムIDのリスト
        self._highlight_marker: Optional[int] = None
        
        # イベントコールバック
        self._callbacks: Dict[str, Callable] = {}
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self._callbacks.update(callbacks)
    
    def bind_events(self, mode: str = "編集"):
        """モードに応じてイベントをバインド"""
        # 既存のバインドをクリア
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        
        if mode == "編集":
            # 編集モード: 左クリックで座標追加、右クリックで座標選択
            self.canvas.bind("<Button-1>", self._callbacks.get('on_canvas_click'))
            self.canvas.bind("<Button-3>", self._callbacks.get('on_canvas_right_click'))
        else:
            # 閲覧モード: 左クリックで座標選択のみ
            self.canvas.bind("<Button-1>", self._callbacks.get('on_canvas_view_click'))
    
    def display_image(self, tk_image: ImageTk.PhotoImage, x: int = 0, y: int = 0):
        """画像を表示"""
        self.clear_image()
        self._current_image = tk_image
        self._image_item_id = self.canvas.create_image(x, y, anchor=tk.NW, image=tk_image)
    
    def clear_image(self):
        """画像をクリア"""
        if self._image_item_id:
            self.canvas.delete(self._image_item_id)
            self._image_item_id = None
        self._current_image = None
    
    def clear_all(self):
        """キャンバス全体をクリア"""
        self.canvas.delete("all")
        self._current_image = None
        self._image_item_id = None
        self._coordinate_markers.clear()
        self._highlight_marker = None
    
    def draw_coordinate_marker(self, x: int, y: int, number: int, color: str = 'red') -> int:
        """座標マーカーを描画"""
        # 円を描画
        marker_size = 5
        circle_id = self.canvas.create_oval(
            x - marker_size, y - marker_size,
            x + marker_size, y + marker_size,
            fill=color, outline='darkred', width=2
        )
        
        # 番号テキストを描画
        text_id = self.canvas.create_text(
            x, y - 15,
            text=str(number),
            fill=color,
            font=("Arial", 10, "bold")
        )
        
        # マーカーIDを記録
        self._coordinate_markers.extend([circle_id, text_id])
        
        return circle_id
    
    def redraw_all_markers(self, coordinates: List[Tuple[int, int]]):
        """全マーカーを再描画"""
        self.clear_markers()
        
        for i, (x, y) in enumerate(coordinates):
            self.draw_coordinate_marker(x, y, i + 1)
    
    def clear_markers(self):
        """全マーカーをクリア"""
        for marker_id in self._coordinate_markers:
            self.canvas.delete(marker_id)
        self._coordinate_markers.clear()
        self.clear_highlight()
    
    def highlight_coordinate(self, index: int, coordinates: List[Tuple[int, int]]):
        """指定された座標をハイライト表示"""
        self.clear_highlight()
        
        if 0 <= index < len(coordinates):
            x, y = coordinates[index]
            
            # ハイライト用の大きな円を描画
            highlight_size = 10
            self._highlight_marker = self.canvas.create_oval(
                x - highlight_size, y - highlight_size,
                x + highlight_size, y + highlight_size,
                fill='', outline='blue', width=3
            )
    
    def clear_highlight(self):
        """ハイライトをクリア"""
        if self._highlight_marker:
            self.canvas.delete(self._highlight_marker)
            self._highlight_marker = None
    
    def get_canvas(self) -> tk.Canvas:
        """キャンバスオブジェクトを取得"""
        return self.canvas
    
    def resize_canvas(self, width: int, height: int):
        """キャンバスサイズを変更"""
        self.width = width
        self.height = height
        self.canvas.config(width=width, height=height)
    
    def get_canvas_size(self) -> Tuple[int, int]:
        """キャンバスサイズを取得"""
        return (self.width, self.height)
    
    def is_point_in_canvas(self, x: int, y: int) -> bool:
        """指定された座標がキャンバス内にあるかチェック"""
        return 0 <= x <= self.width and 0 <= y <= self.height
    
    def save_canvas_as_image(self, file_path: str):
        """キャンバスを画像として保存"""
        try:
            # PostScriptとして出力
            ps_file = file_path.replace('.png', '.ps')
            self.canvas.postscript(file=ps_file)
            
            # PIL/Pillowを使ってPNGに変換
            from PIL import Image
            img = Image.open(ps_file)
            img.save(file_path, 'PNG')
            
            # 一時ファイルを削除
            import os
            os.remove(ps_file)
            
            return True
        except Exception as e:
            print(f"キャンバス保存エラー: {e}")
            return False
