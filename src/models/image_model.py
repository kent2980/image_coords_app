"""
Image Model
画像情報を管理するモデル
"""

import os
from typing import List, Dict, Optional, Any
from PIL import Image, ImageTk
import tkinter as tk


class ImageModel:
    """画像情報モデル"""
    
    def __init__(self):
        self._current_image_path: Optional[str] = None
        self._image_info: Optional[Dict[str, Any]] = None
        self._available_images: List[Dict[str, str]] = []
        self._tk_image: Optional[ImageTk.PhotoImage] = None
        
        # サポートする画像拡張子
        self._supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    
    def load_image(self, image_path: str, canvas_width: int = 800, canvas_height: int = 600) -> Optional[ImageTk.PhotoImage]:
        """画像を読み込んでTkinter用に変換"""
        try:
            if not os.path.exists(image_path):
                print(f"画像ファイルが存在しません: {image_path}")
                return None
            
            with Image.open(image_path) as pil_image:
                # 元の画像サイズ
                orig_width, orig_height = pil_image.size
                
                # アスペクト比を計算
                aspect_ratio = orig_width / orig_height
                
                # キャンバスに収まるサイズを計算
                if aspect_ratio > canvas_width / canvas_height:
                    # 横長の画像
                    new_width = canvas_width
                    new_height = int(canvas_width / aspect_ratio)
                else:
                    # 縦長の画像
                    new_height = canvas_height
                    new_width = int(canvas_height * aspect_ratio)
                
                # 画像をリサイズ
                resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # PhotoImageに変換
                self._tk_image = ImageTk.PhotoImage(resized_image)
                
                # 画像情報を保存
                self._current_image_path = image_path
                self._image_info = {
                    'image_path': image_path,
                    'display_width': new_width,
                    'display_height': new_height,
                    'original_width': orig_width,
                    'original_height': orig_height,
                    'display_x': (canvas_width - new_width) // 2,
                    'display_y': (canvas_height - new_height) // 2
                }
                
                return self._tk_image
                
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return None
    
    def get_current_image_path(self) -> Optional[str]:
        """現在の画像パスを取得"""
        return self._current_image_path
    
    def get_image_info(self) -> Optional[Dict[str, Any]]:
        """画像情報を取得"""
        return self._image_info.copy() if self._image_info else None
    
    def get_current_tk_image(self) -> Optional[ImageTk.PhotoImage]:
        """現在のTkinter画像オブジェクトを取得"""
        return self._tk_image
    
    def clear_current_image(self):
        """現在の画像情報をクリア"""
        self._current_image_path = None
        self._image_info = None
        self._tk_image = None
    
    def load_images_from_directory(self, directory: str) -> List[Dict[str, str]]:
        """指定されたディレクトリから画像ファイル一覧を取得"""
        if not directory or not os.path.exists(directory):
            return []
        
        try:
            image_files = []
            for filename in os.listdir(directory):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    # 拡張子をチェック
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in self._supported_extensions:
                        # 拡張子を除いたファイル名をキーに、フルパスを値にした辞書を作成
                        name_without_ext = os.path.splitext(filename)[0]
                        image_files.append({name_without_ext: full_path})
            
            # ファイル名でソート
            self._available_images = sorted(image_files, key=lambda x: list(x.keys())[0])
            return self._available_images
            
        except Exception as e:
            print(f"画像ファイル読み込みエラー: {e}")
            return []
    
    def get_available_images(self) -> List[Dict[str, str]]:
        """利用可能な画像一覧を取得"""
        return self._available_images.copy()
    
    def find_image_path_by_name(self, image_name: str) -> Optional[str]:
        """画像名から画像パスを検索"""
        for image_dict in self._available_images:
            if image_name in image_dict:
                return image_dict[image_name]
        return None
    
    def is_supported_image_file(self, file_path: str) -> bool:
        """サポートされている画像ファイルかチェック"""
        _, ext = os.path.splitext(file_path)
        return ext.lower() in self._supported_extensions
    
    def get_supported_extensions(self) -> set:
        """サポートされている拡張子一覧を取得"""
        return self._supported_extensions.copy()
    
    def calculate_display_position(self, canvas_width: int, canvas_height: int) -> Dict[str, int]:
        """画像の表示位置を計算"""
        if not self._image_info:
            return {'x': 0, 'y': 0}
        
        display_width = self._image_info.get('display_width', 0)
        display_height = self._image_info.get('display_height', 0)
        
        return {
            'x': (canvas_width - display_width) // 2,
            'y': (canvas_height - display_height) // 2
        }
    
    def is_point_in_image(self, x: int, y: int) -> bool:
        """指定された座標が画像内にあるかチェック"""
        if not self._image_info:
            return False
        
        display_x = self._image_info.get('display_x', 0)
        display_y = self._image_info.get('display_y', 0)
        display_width = self._image_info.get('display_width', 0)
        display_height = self._image_info.get('display_height', 0)
        
        return (display_x <= x <= display_x + display_width and 
                display_y <= y <= display_y + display_height)
    
    def convert_display_to_original_coordinates(self, display_x: int, display_y: int) -> Optional[tuple]:
        """表示座標を元画像座標に変換"""
        if not self._image_info:
            return None
        
        img_x = self._image_info.get('display_x', 0)
        img_y = self._image_info.get('display_y', 0)
        display_width = self._image_info.get('display_width', 0)
        display_height = self._image_info.get('display_height', 0)
        original_width = self._image_info.get('original_width', 0)
        original_height = self._image_info.get('original_height', 0)
        
        if display_width == 0 or display_height == 0:
            return None
        
        # 画像内の相対座標に変換
        relative_x = display_x - img_x
        relative_y = display_y - img_y
        
        # 元画像座標に変換
        original_x = int(relative_x * original_width / display_width)
        original_y = int(relative_y * original_height / display_height)
        
        return (original_x, original_y)
    
    def convert_original_to_display_coordinates(self, original_x: int, original_y: int) -> Optional[tuple]:
        """元画像座標を表示座標に変換"""
        if not self._image_info:
            return None
        
        img_x = self._image_info.get('display_x', 0)
        img_y = self._image_info.get('display_y', 0)
        display_width = self._image_info.get('display_width', 0)
        display_height = self._image_info.get('display_height', 0)
        original_width = self._image_info.get('original_width', 0)
        original_height = self._image_info.get('original_height', 0)
        
        if original_width == 0 or original_height == 0:
            return None
        
        # 表示座標に変換
        display_x = int(original_x * display_width / original_width) + img_x
        display_y = int(original_y * display_height / original_height) + img_y
        
        return (display_x, display_y)
