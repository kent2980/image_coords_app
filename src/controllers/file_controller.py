"""
ファイルコントローラー
ファイル操作とデータの保存・読み込みを制御
"""
import os
import json
from tkinter import filedialog, messagebox
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional


class FileController:
    """ファイル操作を管理するコントローラー"""
    
    def __init__(self, coordinate_model, settings_model, worker_model):
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        
        # 現在のJSONファイルパス
        self.current_json_path = None
        
        # デフォルトの不良項目
        self.default_defects = [
            "ズレ", "裏", "飛び", "傷", "汚れ", "欠け",
            "変色", "寸法不良", "形状不良", "その他"
        ]
    
    def select_image_file(self) -> Optional[str]:
        """画像ファイルを選択"""
        filetypes = [
            ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
            ("すべてのファイル", "*.*")
        ]
        
        initial_dir = self.settings_model.image_directory
        if initial_dir == "未選択":
            initial_dir = None
        
        file_path = filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        return file_path if file_path else None
    
    def select_json_file(self) -> Optional[str]:
        """JSONファイルを選択"""
        filetypes = [
            ("JSONファイル", "*.json"),
            ("すべてのファイル", "*.*")
        ]
        
        initial_dir = self.settings_model.data_directory
        if initial_dir == "未選択":
            initial_dir = None
        
        file_path = filedialog.askopenfilename(
            title="JSONファイルを選択",
            filetypes=filetypes,
            initialdir=initial_dir
        )
        
        return file_path if file_path else None
    
    def save_json_file(self, default_filename: str = "coordinates.json") -> Optional[str]:
        """JSON保存先を選択"""
        filetypes = [
            ("JSONファイル", "*.json"),
            ("すべてのファイル", "*.*")
        ]
        
        initial_dir = self.settings_model.data_directory
        if initial_dir == "未選択":
            initial_dir = None
        
        file_path = filedialog.asksaveasfilename(
            title="座標をJSONで保存",
            defaultextension=".json",
            filetypes=filetypes,
            initialdir=initial_dir,
            initialfile=default_filename
        )
        
        return file_path if file_path else None
    
    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """JSONファイルを読み込み"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            raise Exception(f"JSONファイル読み込みエラー: {e}")
    
    def save_json_data(self, file_path: str, data: Dict[str, Any]) -> bool:
        """JSONファイルに保存"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 現在のJSONファイルパスを記録
            self.current_json_path = file_path
            return True
        except Exception as e:
            raise Exception(f"JSONファイル保存エラー: {e}")
    
    def create_save_data(self, coordinates: List[Tuple[int, int]], image_path: str, 
                        coordinate_details: List[Dict[str, Any]], lot_number: str, 
                        worker_no: str) -> Dict[str, Any]:
        """保存用データを作成"""
        return {
            'coordinates': coordinates,
            'image_path': image_path,
            'coordinate_details': coordinate_details,
            'lot_number': lot_number,
            'worker_no': worker_no,
            'created_at': datetime.now().isoformat(),
            'total_coordinates': len(coordinates)
        }
    
    def parse_loaded_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """読み込んだデータを解析"""
        parsed_data = {
            'coordinates': data.get('coordinates', []),
            'image_path': data.get('image_path', ''),
            'coordinate_details': data.get('coordinate_details', []),
            'lot_number': data.get('lot_number', ''),
            'worker_no': data.get('worker_no', ''),
            'created_at': data.get('created_at', ''),
            'total_coordinates': data.get('total_coordinates', 0)
        }
        
        # 座標データの検証
        if not isinstance(parsed_data['coordinates'], list):
            raise Exception("座標データが不正です")
        
        # 詳細情報の数を座標数に合わせる
        coord_count = len(parsed_data['coordinates'])
        detail_count = len(parsed_data['coordinate_details'])
        
        if detail_count < coord_count:
            # 不足分を空の辞書で埋める
            for _ in range(coord_count - detail_count):
                parsed_data['coordinate_details'].append({})
        elif detail_count > coord_count:
            # 余分な詳細情報を削除
            parsed_data['coordinate_details'] = parsed_data['coordinate_details'][:coord_count]
        
        return parsed_data
    
    def get_automatic_save_path(self, date_str: str, model_name: str, lot_number: str, save_name: str) -> Optional[str]:
        """自動保存パスを生成"""
        try:
            data_directory = self.settings_model.data_directory
            
            if data_directory == "未選択" or not data_directory:
                return None
            
            # ディレクトリパス: データディレクトリ/日付/モデル名/ロット番号
            save_dir = os.path.join(data_directory, date_str, model_name, lot_number)
            
            # ディレクトリを作成
            os.makedirs(save_dir, exist_ok=True)
            
            # ファイルパス
            filename = f"{save_name}.json"
            file_path = os.path.join(save_dir, filename)
            
            return file_path
        except Exception as e:
            print(f"自動保存パス生成エラー: {e}")
            return None
    
    def get_next_sequential_number(self, directory: str) -> int:
        """次の連番を取得"""
        try:
            if not os.path.exists(directory):
                return 1
            
            json_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    name_without_ext = os.path.splitext(filename)[0]
                    # 4桁の数字のみのファイル名かチェック
                    if name_without_ext.isdigit() and len(name_without_ext) == 4:
                        json_files.append(int(name_without_ext))
            
            if not json_files:
                return 1
            
            return max(json_files) + 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def load_defects_from_file(self) -> List[str]:
        """defects.txtから不良項目を読み込み"""
        try:
            if os.path.exists("defects.txt"):
                with open("defects.txt", 'r', encoding='utf-8') as f:
                    defects = [line.strip() for line in f if line.strip()]
                return defects if defects else self.default_defects
            else:
                return self.default_defects
        except Exception as e:
            print(f"不良項目読み込みエラー: {e}")
            return self.default_defects
    
    def save_coordinates_with_auto_update(self, coordinates: List[Tuple[int, int]], 
                                        coordinate_details: List[Dict[str, Any]], 
                                        lot_number: str, worker_no: str) -> bool:
        """座標データを自動更新保存（現在のJSONファイルに）"""
        if not self.current_json_path:
            return False
        
        try:
            # 現在の画像パス
            image_path = self.coordinate_model.image_path
            
            # 保存データを作成
            save_data = self.create_save_data(
                coordinates, image_path, coordinate_details, lot_number, worker_no
            )
            
            # 現在のJSONファイルを更新
            return self.save_json_data(self.current_json_path, save_data)
            
        except Exception as e:
            print(f"自動更新保存エラー: {e}")
            return False
    
    def validate_image_path(self, image_path: str) -> bool:
        """画像パスの検証"""
        if not image_path:
            return False
        
        if not os.path.exists(image_path):
            return False
        
        # 画像ファイルの拡張子をチェック
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        _, ext = os.path.splitext(image_path.lower())
        
        return ext in valid_extensions
    
    def show_info_message(self, message: str, title: str = "情報"):
        """情報メッセージを表示"""
        messagebox.showinfo(title, message)
    
    def show_error_message(self, message: str, title: str = "エラー"):
        """エラーメッセージを表示"""
        messagebox.showerror(title, message)
    
    def show_success_message(self, message: str, title: str = "成功"):
        """成功メッセージを表示"""
        messagebox.showinfo(title, message)
    
    def show_warning_message(self, message: str, title: str = "警告"):
        """警告メッセージを表示"""
        messagebox.showwarning(title, message)
