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
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def save_lot_number_info(self, lot_number: str, save_dir: str) -> bool:
        """ロット番号情報をJSONファイルに保存
        
        Args:
            lot_number: ロット番号
            save_dir: 保存ディレクトリのパス
            
        Returns:
            bool: 保存成功時はTrue、失敗時はFalse
        """
        try:
            # {lot_number: file_path}の辞書を作成
            lot_number_dict = {lot_number: save_dir}
            
            # プロジェクトのルートディレクトリにlot_number_info.jsonが存在しなければ作成、存在すれば追加する
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            lot_number_info_path = os.path.join(project_root, "lot_number_info.json")
            
            if os.path.exists(lot_number_info_path):
                try:
                    with open(lot_number_info_path, 'r', encoding='utf-8') as f:
                        lot_number_info = json.load(f)
                except (json.JSONDecodeError, Exception):
                    lot_number_info = {}
            else:
                lot_number_info = {}
            
            # ロット番号情報を更新
            lot_number_info.update(lot_number_dict)
            
            with open(lot_number_info_path, 'w', encoding='utf-8') as f:
                json.dump(lot_number_info, f, ensure_ascii=False, indent=2)
            
            print(f"ロット番号情報を保存しました: {lot_number} -> {save_dir}")
            return True
            
        except Exception as e:
            print(f"ロット番号情報の保存エラー: {e}")
            return False
    
    def get_lot_number_directory(self, lot_number: str) -> Optional[str]:
        """ロット番号からディレクトリパスを取得
        
        Args:
            lot_number: ロット番号
            
        Returns:
            Optional[str]: ディレクトリパス（見つからない場合はNone）
        """
        try:
            # プロジェクトのルートディレクトリからlot_number_info.jsonを読み込み
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            lot_number_info_path = os.path.join(project_root, "lot_number_info.json")
            
            if not os.path.exists(lot_number_info_path):
                print(f"ロット番号情報ファイルが存在しません: {lot_number_info_path}")
                return None
            
            try:
                with open(lot_number_info_path, 'r', encoding='utf-8') as f:
                    lot_number_info = json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"ロット番号情報ファイルの読み込みエラー: {e}")
                return None
            
            # ロット番号に対応するディレクトリパスを取得
            directory_path = lot_number_info.get(lot_number)
            
            if directory_path:
                # ディレクトリが実際に存在するかチェック
                if os.path.exists(directory_path):
                    print(f"ロット番号 '{lot_number}' のディレクトリパスを取得しました: {directory_path}")
                    return directory_path
                else:
                    print(f"ロット番号 '{lot_number}' のディレクトリが存在しません: {directory_path}")
                    return None
            else:
                print(f"ロット番号 '{lot_number}' の情報が見つかりません")
                return None
                
        except Exception as e:
            print(f"ロット番号ディレクトリ取得エラー: {e}")
            return None
    
    def setup_json_save_dir(self, current_date, model_name: str, lot_number: str) -> Optional[str]:
        """
        JSONファイルの保存先ディレクトリを作成 
        \データディレクトリ\日付\モデル名\ロット番号\
        
        Args:
            current_date: 現在の日付
            model_name: モデル名
            lot_number: ロット番号
            
        Returns:
            str: 作成されたディレクトリのパス（作成できない場合はNone）
        """
        try:
            # 設定を読み込み
            settings = self.settings_model.get_all_settings()
            data_directory = settings.get('data_directory', '')
            
            if not data_directory or data_directory == "未選択":
                print("データディレクトリが設定されていません。")
                return None
            
            # データディレクトリが存在するかチェック、存在しない場合は作成
            if not os.path.exists(data_directory):
                try:
                    os.makedirs(data_directory, exist_ok=True)
                    print(f"データディレクトリを作成しました: {data_directory}")
                except Exception as e:
                    print(f"データディレクトリの作成に失敗しました: {data_directory}, エラー: {e}")
                    return None
            
            # 現在の日付を取得（YYYY-MM-DD形式）
            current_date_str = current_date.strftime('%Y-%m-%d')
            
            if not model_name or model_name.startswith("画像") or model_name == "設定エラー":
                print("有効なモデルが選択されていません。")
                return None
            
            if not lot_number or lot_number.strip() == "":
                print("ロット番号が設定されていません。")
                return None
            
            # ディレクトリパスを構築: データディレクトリ\日付\モデル名\ロット番号
            save_dir = os.path.join(data_directory, current_date_str, model_name, lot_number)
            
            # ディレクトリを作成（存在しない場合）
            os.makedirs(save_dir, exist_ok=True)
            
            # ロット番号情報をJSONファイルに保存
            self.save_lot_number_info(lot_number, save_dir)

            print(f"保存ディレクトリを作成/確認しました: {save_dir}")
            return save_dir
            
        except Exception as e:
            print(f"保存ディレクトリ作成エラー: {e}")
            return None
    
    def get_next_sequential_number(self, directory: str) -> int:
        """指定されたディレクトリ内の連番ファイル名の次の番号を取得
        
        Args:
            directory: 検索対象のディレクトリパス
            
        Returns:
            int: 次の連番（0001から開始）
        """
        if not directory or not os.path.exists(directory):
            return 1
        
        try:
            # ディレクトリ内のJSONファイルを検索
            json_files = []
            for filename in os.listdir(directory):
                if filename.endswith('.json') and os.path.isfile(os.path.join(directory, filename)):
                    # ファイル名から数字部分を抽出
                    name_without_ext = os.path.splitext(filename)[0]
                    
                    # 4桁の数字のみのファイル名かチェック
                    if name_without_ext.isdigit() and len(name_without_ext) == 4:
                        json_files.append(int(name_without_ext))
            
            if not json_files:
                # 連番ファイルが存在しない場合は1から開始
                return 1
            
            # 最大値の次の番号を返す
            return max(json_files) + 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def setup_save_name_entry(self, current_date, model_name: str, lot_number: str, current_save_name: str) -> str:
        """保存名エントリに連番ファイル名を自動設定
        
        Args:
            current_date: 現在の日付
            model_name: モデル名
            lot_number: ロット番号
            current_save_name: 現在の保存名
            
        Returns:
            str: 自動生成された保存名（空文字列の場合は変更なし）
        """
        try:
            # 現在の保存名をチェック
            if current_save_name and current_save_name.strip():
                # 保存名が既に設定されている場合は変更しない
                return current_save_name
            
            # 保存ディレクトリを取得
            save_dir = self.setup_json_save_dir(current_date, model_name, lot_number)
            
            if save_dir:
                # 次の連番を取得
                next_number = self.get_next_sequential_number(save_dir)
                
                # 4桁ゼロパディングで保存名を設定
                auto_save_name = f"{next_number:04d}"
                print(f"保存名を自動設定しました: {auto_save_name}")
                return auto_save_name
            
            return current_save_name
                
        except Exception as e:
            print(f"保存名自動設定エラー: {e}")
            return current_save_name
    
    def show_info_message(self, message: str, title: str = "情報"):
        """情報メッセージを表示"""
        from tkinter import messagebox
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
