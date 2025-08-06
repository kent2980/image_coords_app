"""
File Controller
ファイル操作を制御するコントローラー
"""

import os
import json
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
from tkinter import filedialog, messagebox

from ..models.coordinate_model import CoordinateModel
from ..models.app_settings_model import AppSettingsModel
from ..models.worker_model import WorkerModel


class FileController:
    """ファイルコントローラークラス"""
    
    def __init__(self, coordinate_model: CoordinateModel, settings_model: AppSettingsModel, worker_model: WorkerModel):
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        self._callbacks: Dict[str, Callable] = {}
        self.current_json_path: Optional[str] = None
    
    def set_callbacks(self, callbacks: Dict[str, Callable]):
        """コールバック関数を設定"""
        self._callbacks.update(callbacks)
    
    def save_coordinates(self, file_path: str = None, lot_number: str = "", 
                        save_name: str = "") -> bool:
        """座標データを保存"""
        try:
            # 座標データを取得
            coordinates = self.coordinate_model.get_coordinates()
            coordinate_details = self.coordinate_model.get_coordinate_details()
            image_path = self.coordinate_model.get_current_image_path() or ""
            
            if not coordinates:
                messagebox.showinfo("情報", "座標がありません。")
                return False
            
            # 作業者情報を取得
            worker_no = self.worker_model.get_current_worker_no()
            if not worker_no:
                messagebox.showerror("エラー", "作業者が設定されていません。")
                return False
            
            # ファイルパスが指定されていない場合は自動生成
            if not file_path:
                file_path = self._generate_save_path(lot_number, save_name)
                if not file_path:
                    return False
            
            # 保存データを作成
            save_data = self._create_save_data(
                coordinates, image_path, coordinate_details, lot_number, worker_no
            )
            
            # JSONファイルに保存
            self._save_json_data(file_path, save_data)
            self.current_json_path = file_path
            
            messagebox.showinfo("保存完了", f"座標をJSON形式で保存しました。\n保存先: {file_path}")
            
            # コールバックを呼び出し
            callback = self._callbacks.get('on_data_saved')
            if callback:
                callback(file_path)
            
            return True
            
        except Exception as e:
            messagebox.showerror("保存エラー", f"保存中にエラーが発生しました: {e}")
            return False
    
    def load_coordinates(self, file_path: str = None) -> bool:
        """座標データを読み込み"""
        try:
            # ファイルパスが指定されていない場合はダイアログで選択
            if not file_path:
                file_path = self._select_json_file()
                if not file_path:
                    return False
            
            # JSONデータを読み込み
            data = self._load_json_data(file_path)
            parsed_data = self._parse_loaded_data(data)
            
            # 画像パスをチェック
            image_path = parsed_data.get('image_path', '')
            if not image_path:
                messagebox.showerror("エラー", "画像パスがJSONに含まれていません。")
                return False
            
            # 座標と詳細情報を設定
            coordinates = parsed_data.get('coordinates', [])
            coordinate_details = parsed_data.get('coordinate_details', [])
            
            self.coordinate_model.set_coordinates_with_details(coordinates, coordinate_details)
            
            # 画像情報を設定（可能であれば）
            if os.path.exists(image_path):
                # 画像情報を座標モデルに設定する処理は
                # メインコントローラーで行う
                pass
            
            self.current_json_path = file_path
            
            # ロット番号と作業者情報を返す
            lot_number = parsed_data.get('lot_number', '')
            worker_no = parsed_data.get('worker_no', '')
            
            # コールバックを呼び出し
            callback = self._callbacks.get('on_data_loaded')
            if callback:
                callback({
                    'coordinates': coordinates,
                    'coordinate_details': coordinate_details,
                    'image_path': image_path,
                    'lot_number': lot_number,
                    'worker_no': worker_no,
                    'file_path': file_path
                })
            
            coord_count = len(coordinates)
            messagebox.showinfo("読み込み完了", f"JSONファイルを読み込みました。\n座標数: {coord_count}個")
            
            return True
            
        except Exception as e:
            messagebox.showerror("読み込みエラー", f"ファイル読み込み中にエラーが発生しました: {e}")
            return False
    
    def auto_save_coordinates(self, lot_number: str = "") -> bool:
        """自動保存（現在のJSONファイルを更新）"""
        if not self.current_json_path:
            return False
        
        try:
            coordinates = self.coordinate_model.get_coordinates()
            coordinate_details = self.coordinate_model.get_coordinate_details()
            image_path = self.coordinate_model.get_current_image_path() or ""
            worker_no = self.worker_model.get_current_worker_no() or ""
            
            # 保存データを作成
            save_data = self._create_save_data(
                coordinates, image_path, coordinate_details, lot_number, worker_no
            )
            
            # JSONファイルを更新
            self._save_json_data(self.current_json_path, save_data)
            
            print(f"JSONファイルを自動更新しました: {self.current_json_path}")
            return True
            
        except Exception as e:
            print(f"自動保存エラー: {e}")
            return False
    
    def _generate_save_path(self, lot_number: str, save_name: str) -> Optional[str]:
        """保存パスを自動生成"""
        try:
            # データディレクトリが設定されているかチェック
            if not self.settings_model.is_data_directory_valid():
                # ファイルダイアログで保存先を選択
                default_filename = f"{save_name}.json" if save_name else "coordinates.json"
                return filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    initialfilename=default_filename
                )
            
            # ディレクトリを自動生成
            save_dir = self._create_save_directory(lot_number)
            if not save_dir:
                return None
            
            # ファイル名を生成
            if save_name:
                filename = f"{save_name}.json"
                file_path = os.path.join(save_dir, filename)
                
                # 同名ファイルが存在する場合は連番を付ける
                counter = 1
                while os.path.exists(file_path):
                    name_part = os.path.splitext(filename)[0]
                    file_path = os.path.join(save_dir, f"{name_part}_{counter:04d}.json")
                    counter += 1
            else:
                # 保存名が設定されていない場合は連番ファイル名を生成
                next_number = self._get_next_sequential_number(save_dir)
                filename = f"{next_number:04d}.json"
                file_path = os.path.join(save_dir, filename)
            
            return file_path
            
        except Exception as e:
            print(f"保存パス生成エラー: {e}")
            return None
    
    def _create_save_directory(self, lot_number: str) -> Optional[str]:
        """保存ディレクトリを作成"""
        try:
            if not self.settings_model.ensure_data_directory_exists():
                return None
            
            data_directory = self.settings_model.get_data_directory()
            
            # 現在の日付を取得
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # モデル名は外部から取得する必要があるため、
            # ここでは基本的なディレクトリ構造のみ作成
            if not lot_number:
                return data_directory
            
            # ディレクトリパスを構築（モデル名は含まない）
            save_dir = os.path.join(data_directory, current_date)
            
            # ディレクトリを作成
            os.makedirs(save_dir, exist_ok=True)
            
            return save_dir
            
        except Exception as e:
            print(f"保存ディレクトリ作成エラー: {e}")
            return None
    
    def _get_next_sequential_number(self, directory: str) -> int:
        """指定されたディレクトリ内の連番ファイル名の次の番号を取得"""
        if not directory or not os.path.exists(directory):
            return 1
        
        try:
            json_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json') and os.path.isfile(os.path.join(directory, filename)):
                    name_without_ext = os.path.splitext(filename)[0]
                    if name_without_ext.isdigit() and len(name_without_ext) == 4:
                        json_files.append(int(name_without_ext))
            
            return max(json_files) + 1 if json_files else 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def _create_save_data(self, coordinates: List, image_path: str, 
                         coordinate_details: List, lot_number: str, worker_no: str) -> Dict[str, Any]:
        """保存データを作成"""
        return {
            'coordinates': coordinates,
            'coordinate_details': coordinate_details,
            'image_path': image_path,
            'lot_number': lot_number,
            'worker_no': worker_no,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0'
        }
    
    def _save_json_data(self, file_path: str, data: Dict[str, Any]):
        """JSONデータをファイルに保存"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_json_data(self, file_path: str) -> Dict[str, Any]:
        """JSONデータをファイルから読み込み"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _parse_loaded_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """読み込んだデータを解析"""
        # バージョンチェック
        version = data.get('version', '1.0')
        
        if version == '1.0':
            # 旧形式のデータを新形式に変換
            return self._convert_old_format(data)
        else:
            # 新形式のデータをそのまま返す
            return data
    
    def _convert_old_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """旧形式のデータを新形式に変換"""
        coordinates = data.get('coordinates', [])
        image_path = data.get('image_path', '')
        
        # 詳細情報が存在しない場合はデフォルト値で作成
        coordinate_details = []
        for i in range(len(coordinates)):
            coordinate_details.append({
                'item_number': str(i + 1),
                'reference': '',
                'defect': '',
                'comment': '',
                'repaired': 'いいえ',
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            'coordinates': coordinates,
            'coordinate_details': coordinate_details,
            'image_path': image_path,
            'lot_number': '',
            'worker_no': '',
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'version': '2.0'
        }
    
    def _select_json_file(self) -> Optional[str]:
        """JSONファイル選択ダイアログを表示"""
        return filedialog.askopenfilename(
            title="JSONファイルを選択",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
    
    def select_image_file(self) -> Optional[str]:
        """画像ファイル選択ダイアログを表示"""
        return filedialog.askopenfilename(
            title="画像ファイルを選択",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
    
    def export_coordinates_csv(self, file_path: str = None) -> bool:
        """座標データをCSV形式でエクスポート"""
        try:
            import csv
            
            if not file_path:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    initialfilename="coordinates.csv"
                )
                if not file_path:
                    return False
            
            coordinates = self.coordinate_model.get_coordinates()
            coordinate_details = self.coordinate_model.get_coordinate_details()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # ヘッダー行
                writer.writerow([
                    '項目番号', 'X座標', 'Y座標', 'リファレンス', '不良名', 
                    'コメント', '修理済み', 'タイムスタンプ'
                ])
                
                # データ行
                for i, (x, y) in enumerate(coordinates):
                    detail = coordinate_details[i] if i < len(coordinate_details) else {}
                    writer.writerow([
                        detail.get('item_number', str(i + 1)),
                        x, y,
                        detail.get('reference', ''),
                        detail.get('defect', ''),
                        detail.get('comment', ''),
                        detail.get('repaired', 'いいえ'),
                        detail.get('timestamp', '')
                    ])
            
            messagebox.showinfo("エクスポート完了", f"座標データをCSV形式で保存しました。\n保存先: {file_path}")
            return True
            
        except Exception as e:
            messagebox.showerror("エクスポートエラー", f"CSVエクスポート中にエラーが発生しました: {e}")
            return False
    
    def get_current_file_path(self) -> Optional[str]:
        """現在のファイルパスを取得"""
        return self.current_json_path
    
    def clear_current_file_path(self):
        """現在のファイルパスをクリア"""
        self.current_json_path = None
