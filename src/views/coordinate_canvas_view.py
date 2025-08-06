"""
座標キャンバスビュー
画像表示と座標マーキングを管理
"""
import tkinter as tk
from PIL import ImageTk
from typing import Callable, Optional, List, Tuple, Dict, Any


class CoordinateCanvasView:
    """座標キャンバスを管理するビュー"""
    
    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        self.canvas_width = 800
        self.canvas_height = 600
        
        # キャンバス
        self.canvas = tk.Canvas(
            parent_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=2
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # スクロールバー
        self.setup_scrollbars()
        
        # イベントコールバック
        self.callbacks: Dict[str, Callable] = {}
        
        # 表示中の画像と座標
        self.current_image = None
        self.coordinate_markers = []
        self.highlight_marker = None
    
    def setup_scrollbars(self):
        """スクロールバーを設定"""
        # 垂直スクロールバー
        v_scrollbar = tk.Scrollbar(self.parent_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # 水平スクロールバー
        h_scrollbar = tk.Scrollbar(self.parent_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
    
    def bind_events(self, mode: str = "edit"):
        """イベントをバインド"""
        # 既存のバインドをクリア
        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-3>")
        
        if mode == "edit":
            # 編集モード: 左クリックで座標追加、右クリックで座標選択
            self.canvas.bind("<Button-1>", self._on_left_click)
            self.canvas.bind("<Button-3>", self._on_right_click)
        elif mode == "view":
            # 閲覧モード: 左クリックで座標選択のみ
            self.canvas.bind("<Button-1>", self._on_view_click)
    
    def _on_left_click(self, event):
        """左クリックイベント（編集モード）"""
        if 'on_left_click' in self.callbacks:
            self.callbacks['on_left_click'](event)
    
    def _on_right_click(self, event):
        """右クリックイベント（編集モード）"""
        if 'on_right_click' in self.callbacks:
            self.callbacks['on_right_click'](event)
    
    def _on_view_click(self, event):
        """クリックイベント（閲覧モード）"""
        if 'on_view_click' in self.callbacks:
            self.callbacks['on_view_click'](event)
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self.callbacks.update(callbacks)
    
    def display_image(self, tk_image: ImageTk.PhotoImage, width: int = None, height: int = None):
        """画像を表示"""
        self.clear_canvas()
        
        # 画像のサイズを取得
        if width and height:
            # 指定されたサイズでキャンバスを設定
            self.canvas.config(width=width, height=height)
            # スクロール領域を設定
            self.canvas.configure(scrollregion=(0, 0, width, height))
        
        # 画像を描画
        self.current_image = self.canvas.create_image(0, 0, anchor="nw", image=tk_image)
        
        # 画像参照を保持（ガベージコレクション防止）
        self.canvas.image = tk_image
    
    def add_coordinate_marker(self, x: int, y: int, number: int, color: str = "red") -> int:
        """座標マーカーを追加"""
        # 円マーカー
        circle = self.canvas.create_oval(
            x-5, y-5, x+5, y+5,
            fill=color, outline="black", width=2
        )
        
        # 番号テキスト
        text = self.canvas.create_text(
            x, y-15, text=str(number),
            fill="black", font=("Arial", 12, "bold")
        )
        
        marker_id = len(self.coordinate_markers)
        self.coordinate_markers.append({
            'id': marker_id,
            'circle': circle,
            'text': text,
            'x': x,
            'y': y,
            'number': number
        })
        
        return marker_id
    
    def remove_coordinate_marker(self, marker_id: int) -> bool:
        """座標マーカーを削除"""
        if 0 <= marker_id < len(self.coordinate_markers):
            marker = self.coordinate_markers[marker_id]
            self.canvas.delete(marker['circle'])
            self.canvas.delete(marker['text'])
            return True
        return False
    
    def clear_coordinate_markers(self):
        """全座標マーカーをクリア"""
        for marker in self.coordinate_markers:
            self.canvas.delete(marker['circle'])
            self.canvas.delete(marker['text'])
        self.coordinate_markers.clear()
    
    def redraw_coordinate_markers(self, coordinates: List[Tuple[int, int]]):
        """座標マーカーを再描画"""
        self.clear_coordinate_markers()
        
        for i, (x, y) in enumerate(coordinates):
            self.add_coordinate_marker(x, y, i + 1)
    
    def highlight_coordinate(self, index: int):
        """指定した座標をハイライト"""
        self.clear_highlight()
        
        if 0 <= index < len(self.coordinate_markers):
            marker = self.coordinate_markers[index]
            x, y = marker['x'], marker['y']
            
            # ハイライト用の大きな円を描画
            self.highlight_marker = self.canvas.create_oval(
                x-10, y-10, x+10, y+10,
                fill="", outline="yellow", width=3
            )
    
    def clear_highlight(self):
        """ハイライトをクリア"""
        if self.highlight_marker:
            self.canvas.delete(self.highlight_marker)
            self.highlight_marker = None
    
    def clear_canvas(self):
        """キャンバスをクリア"""
        self.canvas.delete("all")
        self.coordinate_markers.clear()
        self.highlight_marker = None
        self.current_image = None
    
    def get_canvas_coordinates(self, event) -> Tuple[int, int]:
        """イベントからキャンバス座標を取得"""
        return self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
    
    def find_nearest_coordinate(self, x: int, y: int, max_distance: int = 20) -> Optional[int]:
        """最寄りの座標インデックスを検索"""
        min_distance = float('inf')
        nearest_index = None
        
        for i, marker in enumerate(self.coordinate_markers):
            marker_x, marker_y = marker['x'], marker['y']
            distance = ((x - marker_x) ** 2 + (y - marker_y) ** 2) ** 0.5
            
            if distance <= max_distance and distance < min_distance:
                min_distance = distance
                nearest_index = i
        
        return nearest_index
    
    def update_canvas_size(self, width: int, height: int):
        """キャンバスサイズを更新"""
        self.canvas_width = width
        self.canvas_height = height
        self.canvas.config(width=width, height=height)
        self.canvas.configure(scrollregion=(0, 0, width, height))
