"""
座標キャンバスビュー（ttkbootstrap版）
画像表示と座標マーキングを管理
"""
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Canvas
from PIL import ImageTk
from typing import Callable, Optional, List, Tuple, Dict, Any


class CoordinateCanvasView:
    """座標キャンバスを管理するビュー（ttkbootstrap版）"""
    
    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame
        self.canvas_width = 800
        self.canvas_height = 600
        
        # キャンバスフレーム（スクロール機能付き）
        self.canvas_frame = ttk.Frame(parent_frame)
        self.canvas_frame.pack(fill=BOTH, expand=YES)
        
        # キャンバス
        self.canvas = Canvas(
            self.canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="white"
        )
        
        # スクロールバー
        self.v_scrollbar = ttk.Scrollbar(
            self.canvas_frame, 
            orient=VERTICAL, 
            command=self.canvas.yview,
            bootstyle="primary-round"
        )
        self.h_scrollbar = ttk.Scrollbar(
            self.canvas_frame, 
            orient=HORIZONTAL, 
            command=self.canvas.xview,
            bootstyle="primary-round"
        )
        
        # スクロールバーとキャンバスの連携
        self.canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # レイアウト
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        self.v_scrollbar.pack(side=RIGHT, fill=Y)
        self.h_scrollbar.pack(side=BOTTOM, fill=X)
        
        # イベントコールバック
        self.callbacks: Dict[str, Callable] = {}
        
        # 表示中の画像と座標
        self.current_image = None
        self.coordinate_markers = []
        self.highlight_marker = None
        
        # ウィンドウサイズ変更のイベントをバインド
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # マウスホイールのバインド
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
    
    def setup_scrollbars(self):
        """スクロールバーを設定 - 既に__init__で設定済み"""
        pass
    
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
    
    def _on_canvas_configure(self, event):
        """キャンバスサイズ変更時の処理"""
        # キャンバス自体のサイズ変更イベントのみ処理
        if event.widget == self.canvas:
            new_width = event.width
            new_height = event.height
            
            # サイズが実際に変更された場合のみ処理
            if new_width != self.canvas_width or new_height != self.canvas_height:
                print(f"[DEBUG] キャンバスサイズ変更: {self.canvas_width}x{self.canvas_height} → {new_width}x{new_height}")
                
                self.canvas_width = new_width
                self.canvas_height = new_height
                
                # スクロール領域を更新
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                
                # キャンバスサイズ変更のコールバックがある場合は呼び出し
                if 'on_canvas_resize' in self.callbacks:
                    self.callbacks['on_canvas_resize'](new_width, new_height)
    
    def _on_mousewheel(self, event):
        """マウスホイールによる縦スクロール"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _on_shift_mousewheel(self, event):
        """Shift+マウスホイールによる横スクロール"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self.callbacks.update(callbacks)
    
    def display_image(self, tk_image: ImageTk.PhotoImage, width: int = None, height: int = None):
        """画像を表示"""
        self.clear_canvas()
        
        # キャンバスサイズを取得
        canvas_width = self.canvas.winfo_width() or self.canvas_width
        canvas_height = self.canvas.winfo_height() or self.canvas_height
        
        # 画像を中央に配置
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # 画像サイズが大きい場合は、スクロール領域を適切に設定
        if tk_image.width() > canvas_width or tk_image.height() > canvas_height:
            # スクロール領域を画像サイズに合わせて設定
            scroll_width = max(tk_image.width(), canvas_width)
            scroll_height = max(tk_image.height(), canvas_height)
            self.canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))
            
            # 画像を中央に配置（スクロール領域の中央）
            center_x = scroll_width // 2
            center_y = scroll_height // 2
        
        # 既存UIと同じように画像を表示（中央配置）
        self.current_image = self.canvas.create_image(center_x, center_y, anchor="center", image=tk_image)
        
        # 画像参照を保持（ガベージコレクション防止）
        self.canvas.image = tk_image
        
        # スクロール領域を更新
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        print(f"[DEBUG] 画像を表示: キャンバスサイズ {canvas_width}x{canvas_height}, 画像を中央({center_x}, {center_y})に配置")
    
    def add_coordinate_marker(self, x: int, y: int, number: int, color: str = "red") -> int:
        """座標マーカーを追加"""
        # 円マーカー（ttkbootstrapのスタイルに合わせて調整）
        circle = self.canvas.create_oval(
            x-8, y-8, x+8, y+8,
            fill=color, 
            outline="#ffffff", 
            width=3,
            tags="coordinate_marker"
        )
        
        # 番号テキスト（より視認性の良いスタイル）
        text = self.canvas.create_text(
            x, y-20, 
            text=str(number),
            fill="#000000", 
            font=("Arial", 12, "bold"),
            tags="coordinate_text"
        )
        
        # 番号の背景（視認性向上）
        text_bg = self.canvas.create_rectangle(
            x-12, y-32, x+12, y-8,
            fill="#ffffff",
            outline="#cccccc",
            width=1,
            tags="coordinate_text_bg"
        )
        
        # テキストを最前面に
        self.canvas.tag_raise(text)
        
        marker_id = len(self.coordinate_markers)
        self.coordinate_markers.append({
            'id': marker_id,
            'circle': circle,
            'text': text,
            'text_bg': text_bg,
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
            if 'text_bg' in marker:
                self.canvas.delete(marker['text_bg'])
            return True
        return False
    
    def clear_coordinate_markers(self):
        """全座標マーカーをクリア"""
        for marker in self.coordinate_markers:
            self.canvas.delete(marker['circle'])
            self.canvas.delete(marker['text'])
            if 'text_bg' in marker:
                self.canvas.delete(marker['text_bg'])
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
            
            # ハイライト用の大きな円を描画（アニメーション効果付き）
            self.highlight_marker = self.canvas.create_oval(
                x-15, y-15, x+15, y+15,
                fill="", 
                outline="#ffff00", 
                width=4,
                tags="highlight_marker"
            )
            
            # ハイライトマーカーを点滅させる（アニメーション効果）
            self._animate_highlight()
    
    def _animate_highlight(self):
        """ハイライトマーカーのアニメーション"""
        if self.highlight_marker:
            # 色を変更してアニメーション効果
            current_color = self.canvas.itemcget(self.highlight_marker, "outline")
            new_color = "#ff6600" if current_color == "#ffff00" else "#ffff00"
            self.canvas.itemconfig(self.highlight_marker, outline=new_color)
            
            # 500ms後に再度実行
            self.canvas.after(500, self._animate_highlight)
    
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
    
    def find_nearest_coordinate(self, x: int, y: int, max_distance: int = 25) -> Optional[int]:
        """最寄りの座標インデックスを検索（クリック範囲を少し拡大）"""
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
        self.canvas.configure(width=width, height=height)
        
        # スクロール領域を更新
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # 画像が表示されている場合は再配置
        self._reposition_image()
    
    def _reposition_image(self):
        """画像を現在のキャンバスサイズに合わせて再配置"""
        if self.current_image and self.canvas.image:
            # キャンバスサイズを取得
            canvas_width = self.canvas.winfo_width() or self.canvas_width
            canvas_height = self.canvas.winfo_height() or self.canvas_height
            
            # 新しい中央位置を計算
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # 画像を新しい位置に移動
            self.canvas.coords(self.current_image, center_x, center_y)
            print(f"[DEBUG] 画像を再配置: 新しい中央位置({center_x}, {center_y})")
    
    def get_image_offset(self) -> Tuple[int, int]:
        """画像の表示オフセットを取得（座標変換用）"""
        if self.current_image:
            canvas_width = self.canvas.winfo_width() or self.canvas_width
            canvas_height = self.canvas.winfo_height() or self.canvas_height
            
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # 画像サイズを取得してオフセットを計算
            if hasattr(self.canvas, 'image') and self.canvas.image:
                image_width = self.canvas.image.width()
                image_height = self.canvas.image.height()
                
                offset_x = center_x - image_width // 2
                offset_y = center_y - image_height // 2
                
                return (offset_x, offset_y)
        
        return (0, 0)
    
    def zoom_in(self, factor: float = 1.2):
        """ズームイン"""
        # 実装予定: 画像のズーム機能
        pass
    
    def zoom_out(self, factor: float = 0.8):
        """ズームアウト"""
        # 実装予定: 画像のズーム機能
        pass
    
    def reset_zoom(self):
        """ズームリセット"""
        # 実装予定: ズームを100%に戻す
        pass
    
    def center_view(self):
        """ビューを中央に戻す"""
        if self.current_image:
            # スクロール位置を中央に戻す
            self.canvas.xview_moveto(0.5)
            self.canvas.yview_moveto(0.5)
    
    def fit_to_window(self):
        """画像をウィンドウサイズに合わせる"""
        # 実装予定: 画像をウィンドウサイズに自動調整
        pass
