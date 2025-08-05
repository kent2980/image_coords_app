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
        self.coordinate_details = []  # 座標ごとの詳細情報
        self.current_coordinate_index = -1  # 現在選択中の座標インデックス
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
        
        # 新しい座標の詳細情報を初期化
        detail = {
            'item_number': str(len(self.coordinates)),
            'reference': '',
            'defect': 'ズレ',
            'comment': '',
            'repaired': 'いいえ'
        }
        self.coordinate_details.append(detail)
        
        self._save_state()  # 状態を履歴に保存
        
    def remove_coordinate(self, index):
        """指定インデックスの座標を削除"""
        if 0 <= index < len(self.coordinates):
            coord = self.coordinates.pop(index)
            if index < len(self.coordinate_details):
                self.coordinate_details.pop(index)
            self._save_state()
            return coord
        return None
        
    def clear_coordinates(self):
        """全座標をクリア"""
        self.coordinates.clear()
        self.coordinate_details.clear()
        self.current_coordinate_index = -1
        self._save_state()  # 状態を履歴に保存
        
    def set_current_coordinate(self, index):
        """現在選択中の座標を設定"""
        if 0 <= index < len(self.coordinates):
            self.current_coordinate_index = index
            return True
        return False
        
    def get_current_coordinate_detail(self):
        """現在選択中の座標の詳細情報を取得"""
        if 0 <= self.current_coordinate_index < len(self.coordinate_details):
            return self.coordinate_details[self.current_coordinate_index].copy()
        return None
        
    def update_current_coordinate_detail(self, detail):
        """現在選択中の座標の詳細情報を更新"""
        if 0 <= self.current_coordinate_index < len(self.coordinate_details):
            self.coordinate_details[self.current_coordinate_index].update(detail)
            return True
        return False
        
    def get_all_coordinate_details(self):
        """全座標の詳細情報を取得"""
        return [detail.copy() for detail in self.coordinate_details]
        
    def get_coordinates(self):
        """座標リストを取得"""
        return self.coordinates.copy()
        
    def set_coordinates(self, coordinates):
        """座標リストを設定"""
        self.coordinates = coordinates.copy()
        
    def set_coordinates_with_details(self, coordinates, coordinate_details=None):
        """座標リストと詳細情報を設定"""
        self.coordinates = coordinates.copy()
        
        if coordinate_details:
            self.coordinate_details = coordinate_details.copy()
        else:
            # 詳細情報がない場合は初期化
            self.coordinate_details = []
            for i in range(len(coordinates)):
                detail = {
                    'item_number': str(i + 1),
                    'reference': '',
                    'defect': 'ズレ',
                    'comment': '',
                    'repaired': 'いいえ'
                }
                self.coordinate_details.append(detail)
        
        self.current_coordinate_index = -1
        self._save_state()
        
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
        
    def draw_coordinate_marker(self, canvas, x, y, number, size=12, is_selected=False):
        """座標マーカーを描画"""
        # 選択状態に応じて色を変更
        if is_selected:
            fill_color = "yellow"
            outline_color = "orange"
            outline_width = 3
            text_color = "black"
        else:
            fill_color = "red"
            outline_color = "white"
            outline_width = 2
            text_color = "white"
        
        # 背景の円を描画（視認性向上）
        canvas.create_oval(
            x - size, y - size, x + size, y + size,
            fill=fill_color, outline=outline_color, width=outline_width,
            tags=f"marker_{number}"
        )
        # 数字を描画
        canvas.create_text(
            x, y, text=str(number), fill=text_color,
            font=("Arial", 10, "bold"),
            tags=f"marker_{number}"
        )
        
    def redraw_all_markers(self, canvas, selected_index=-1):
        """すべての座標マーカーを再描画"""
        canvas.delete("all")
        
        # 画像を再描画
        if self.tk_img:
            canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            
        # 座標マーカーを再描画（数字付き）
        for i, (x, y) in enumerate(self.coordinates, 1):
            is_selected = (i - 1) == selected_index
            self.draw_coordinate_marker(canvas, x, y, i, is_selected=is_selected)
    
    def highlight_coordinate(self, canvas, index):
        """指定された座標をハイライト表示"""
        if 0 <= index < len(self.coordinates):
            # すべてのマーカーを再描画（選択状態を反映）
            self.redraw_all_markers(canvas, selected_index=index)
            return True
        return False
    
    def clear_highlight(self, canvas):
        """ハイライト表示をクリア"""
        self.redraw_all_markers(canvas, selected_index=-1)
            
    def get_current_image(self):
        """現在の画像を取得"""
        return self.tk_img
        
    def get_current_image_path(self):
        """現在の画像パスを取得"""
        return self.current_image_path
    
    def set_image_info(self, image_info):
        """画像情報を設定"""
        self.current_image_path = image_info['image_path']
        # 画像の表示領域情報も保存（座標変換で使用）
        self.image_display_info = {
            'display_x': image_info['display_x'],
            'display_y': image_info['display_y'],
            'display_width': image_info['display_width'],
            'display_height': image_info['display_height'],
            'original_width': image_info['original_width'],
            'original_height': image_info['original_height']
        }
    
    def get_coordinate_summary(self):
        """座標の概要情報を取得（閲覧モード用）"""
        summary = {
            'total_count': len(self.coordinates),
            'defect_counts': {},
            'repaired_count': 0,
            'unrepaired_count': 0
        }
        
        for detail in self.coordinate_details:
            # 不良種別ごとの件数をカウント
            defect = detail.get('defect', 'ズレ')
            summary['defect_counts'][defect] = summary['defect_counts'].get(defect, 0) + 1
            
            # 修理済み/未修理の件数をカウント
            repaired = detail.get('repaired', 'いいえ')
            if repaired == 'はい':
                summary['repaired_count'] += 1
            else:
                summary['unrepaired_count'] += 1
        
        return summary
    
    def get_coordinate_detail_with_position(self, index):
        """座標の詳細情報と位置情報を取得（閲覧モード用）"""
        if 0 <= index < len(self.coordinates) and index < len(self.coordinate_details):
            x, y = self.coordinates[index]
            detail = self.coordinate_details[index].copy()
            detail['position'] = {'x': x, 'y': y}
            detail['coordinate_number'] = index + 1
            return detail
        return None
    
    def clear_markers(self):
        """座標マーカーをクリア"""
        self.coordinates = []
        # 状態を保存
        self._save_state()
