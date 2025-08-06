"""
画像データモデル
画像情報とリサイズロジックを管理
"""
import os
from PIL import Image, ImageTk
from typing import Dict, List, Optional, Tuple, Any


class ImageModel:
    """画像データを管理するモデル"""
    
    def __init__(self):
        self._current_image_path: str = ""
        self._original_size: Tuple[int, int] = (0, 0)
        self._display_size: Tuple[int, int] = (0, 0)
        self._scale_factor: float = 1.0
        self._tk_image: Optional[ImageTk.PhotoImage] = None
        self._image_files: List[Dict[str, str]] = []
        
        # サポートする画像形式
        self._supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    def load_image(self, image_path: str, canvas_width: int = 800, canvas_height: int = 600) -> Optional[ImageTk.PhotoImage]:
        """画像を読み込み、指定サイズにリサイズ"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")
            
            # PIL画像として読み込み
            with Image.open(image_path) as pil_image:
                self._original_size = pil_image.size
                
                # リサイズ計算
                new_size, scale_factor = self._calculate_display_size(
                    self._original_size, (canvas_width, canvas_height)
                )
                
                # リサイズ実行
                resized_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                
                # Tkinter用に変換
                self._tk_image = ImageTk.PhotoImage(resized_image)
                self._current_image_path = image_path
                self._display_size = new_size
                self._scale_factor = scale_factor
                
                return self._tk_image
                
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return None
    
    def _calculate_display_size(self, original_size: Tuple[int, int], canvas_size: Tuple[int, int]) -> Tuple[Tuple[int, int], float]:
        """表示サイズとスケールファクターを計算"""
        orig_width, orig_height = original_size
        canvas_width, canvas_height = canvas_size
        
        # アスペクト比を維持しながらキャンバスに収まるサイズを計算
        scale_w = canvas_width / orig_width
        scale_h = canvas_height / orig_height
        scale_factor = min(scale_w, scale_h)
        
        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)
        
        return (new_width, new_height), scale_factor
    
    def convert_display_to_original_coords(self, display_x: int, display_y: int) -> Tuple[int, int]:
        """表示座標を元画像の座標に変換"""
        if self._scale_factor > 0:
            orig_x = int(display_x / self._scale_factor)
            orig_y = int(display_y / self._scale_factor)
            return orig_x, orig_y
        return display_x, display_y
    
    def convert_original_to_display_coords(self, orig_x: int, orig_y: int) -> Tuple[int, int]:
        """元画像の座標を表示座標に変換"""
        display_x = int(orig_x * self._scale_factor)
        display_y = int(orig_y * self._scale_factor)
        return display_x, display_y
    
    def load_image_files_from_directory(self, directory: str) -> List[Dict[str, str]]:
        """ディレクトリから画像ファイル一覧を読み込み"""
        self._image_files = []
        
        try:
            if not os.path.exists(directory):
                return self._image_files
            
            for filename in os.listdir(directory):
                if self._is_image_file(filename):
                    full_path = os.path.join(directory, filename)
                    name_without_ext = os.path.splitext(filename)[0]
                    self._image_files.append({name_without_ext: full_path})
            
            # ファイル名でソート
            self._image_files.sort(key=lambda x: list(x.keys())[0])
            
        except Exception as e:
            print(f"画像ファイル読み込みエラー: {e}")
        
        return self._image_files
    
    def _is_image_file(self, filename: str) -> bool:
        """ファイルが画像ファイルかどうかを判定"""
        _, ext = os.path.splitext(filename.lower())
        return ext in self._supported_extensions
    
    def get_image_path_by_name(self, name: str) -> Optional[str]:
        """画像名からフルパスを取得"""
        for image_dict in self._image_files:
            if name in image_dict:
                return image_dict[name]
        return None
    
    def get_image_names(self) -> List[str]:
        """画像名一覧を取得"""
        names = []
        for image_dict in self._image_files:
            names.extend(image_dict.keys())
        return names
    
    @property
    def current_image_path(self) -> str:
        """現在の画像パス"""
        return self._current_image_path
    
    @property
    def original_size(self) -> Tuple[int, int]:
        """元画像のサイズ"""
        return self._original_size
    
    @property
    def display_size(self) -> Tuple[int, int]:
        """表示サイズ"""
        return self._display_size
    
    @property
    def scale_factor(self) -> float:
        """スケールファクター"""
        return self._scale_factor
    
    @property
    def tk_image(self) -> Optional[ImageTk.PhotoImage]:
        """Tkinter画像オブジェクト"""
        return self._tk_image
    
    def get_image_info(self) -> Dict[str, Any]:
        """画像情報を取得"""
        return {
            'path': self._current_image_path,
            'original_size': self._original_size,
            'display_size': self._display_size,
            'scale_factor': self._scale_factor,
            'tk_image': self._tk_image
        }
    
    def clear_image(self):
        """画像情報をクリア"""
        self._current_image_path = ""
        self._original_size = (0, 0)
        self._display_size = (0, 0)
        self._scale_factor = 1.0
        self._tk_image = None
