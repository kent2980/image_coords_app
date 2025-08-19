"""
ファイルコントローラー
ファイル操作とデータの保存・読み込みを制御
"""
import os
import json
from tkinter import filedialog, messagebox
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.coordinate_model import CoordinateModel
    from ..models.app_settings_model import AppSettingsModel
    from ..models.worker_model import WorkerModel
    from ..models.board_model import BoardModel
    from ..models.lot_model import LotModel
from pathlib import Path

# FileManagerクラスをインポート
from src.utils.file_manager_class import FileManager


class FileController:
    """ファイル操作を管理するコントローラー（FileManager統合版）"""

    def __init__(self, coordinate_model: "CoordinateModel", settings_model: "AppSettingsModel", worker_model: "WorkerModel", board_model: "BoardModel", lot_model: "LotModel"):
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        self.board_model = board_model
        self.lot_model = lot_model

        # 現在の保存ディレクトリ
        self.save_dir = None
        
        # 現在のJSONファイルパス
        self.current_json_path = None
        
        # FileManagerのインスタンス
        self.file_manager = None
        
        # デフォルトの不良項目
        self.default_defects = [
            "ズレ", "裏", "飛び", "傷", "汚れ", "欠け",
            "変色", "寸法不良", "形状不良", "その他"
        ]
    
    def initialize_file_manager(self, current_user: str = "作業者"):
        """FileManagerを初期化"""
        data_directory = self.settings_model.data_directory
        if data_directory and data_directory != "未選択":
            self.file_manager = FileManager(
                root_dir=data_directory,
                user=current_user,
                search_limit=100
            )
            print(f"FileManagerを初期化しました: {data_directory}")
        else:
            print("警告: データディレクトリが設定されていません")
    
    def ensure_file_manager(self) -> bool:
        """FileManagerが初期化されているかチェック"""
        if self.file_manager is None:
            self.initialize_file_manager()
        return self.file_manager is not None
    
    # ゲッター関数
    def get_save_dir(self) -> Optional[str]:
        """現在の保存ディレクトリを取得"""
        return self.save_dir
    
    def get_current_json_path(self) -> Optional[str]:
        """現在のJSONファイルパスを取得"""
        return self.current_json_path

    def set_current_json_path(self,board_number:int):
        # 4桁の数字文字列（0埋め）を生成
        board_number_str = f"{board_number:04d}"
        self.current_json_path = os.path.join(self.save_dir, f"{board_number_str}.json")
        print(f"現在のJSONファイルパスを設定しました: {self.current_json_path}")

    def get_default_defects(self) -> List[str]:
        """デフォルトの不良項目リストを取得"""
        return self.default_defects.copy()
    
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
            # 最初にutf-8-sigで試行（BOM付きUTF-8対応）
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
                print(f"[JSON読み込み] UTF-8 (BOM対応) で読み込み成功: {file_path}")
                return data
            except UnicodeDecodeError:
                # utf-8-sigで失敗した場合はcp932（Shift_JIS）で試行
                try:
                    with open(file_path, 'r', encoding='cp932') as f:
                        data = json.load(f)
                    print(f"[JSON読み込み] CP932 (Shift_JIS) で読み込み成功: {file_path}")
                    return data
                except UnicodeDecodeError:
                    # それでも失敗した場合はutf-8で試行
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    print(f"[JSON読み込み] UTF-8 で読み込み成功: {file_path}")
                    return data
        except Exception as e:
            raise Exception(f"JSONファイル読み込みエラー: {e}")
    
    def save_json_data(self, file_path: str, data: Dict[str, Any]) -> bool:
        """JSONファイルに保存"""
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 現在のJSONファイルパスを記録
            self.current_json_path = file_path
            return True
        except Exception as e:
            raise Exception(f"JSONファイル保存エラー: {e}")

    def create_save_data(self, model: str, coordinates: List[Tuple[int, int]], image_path: str,
                         coordinate_details: List[Dict[str, Any]], lot_number: str,
                         worker_no: str) -> Dict[str, Any]:
        """保存用データを作成"""
        return self.file_manager.create_defective_info_data(
            model=model,
            coordinates=coordinates,
            image_path=image_path,
            coordinate_details=coordinate_details,
            lot_number=lot_number,
            worker_no=worker_no
        )

    def parse_loaded_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """読み込んだデータを解析"""
        parsed_data = {
            'model': data.get('model', ''),
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
    
    def get_automatic_save_path(self, lot_number: str, save_name: str) -> Optional[str]:
        """自動保存パスを生成"""
        try:
            data_directory = self.settings_model.data_directory
            
            if data_directory == "未選択" or not data_directory:
                return None
            
            # ディレクトリパス: データディレクトリ/ロット番号
            save_dir = os.path.join(data_directory, lot_number)
            
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
                                        lot_number: str, worker_no: str, model: str = "") -> bool:
        """座標データを自動更新保存（現在のJSONファイルに）"""
        if not self.current_json_path:
            return False
        
        try:
            # 現在の画像パス
            image_path = self.coordinate_model.image_path
            
            # 保存データを作成
            save_data = self.create_save_data(
                model, coordinates, image_path, coordinate_details, lot_number, worker_no
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
                with open(lot_number_info_path, 'r', encoding='utf-8-sig') as f:
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
    
    def setup_json_save_dir(self, model_name: str, lot_number: str) -> Optional[str]:
        """
        設計書に従ったJSONファイル保存先ディレクトリを作成
        フォルダ構造: データディレクトリ/ロット番号/
        """
        try:
            # FileManagerの確認
            if not self.ensure_file_manager():
                print("FileManagerが利用できません")
                return None
            
            # ロット番号の形式検証
            if not self.file_manager.validate_lot_number(lot_number):
                print(f"ロット番号の形式が不正です: {lot_number} (正しい形式: 1234567-10 または 1234567-20)")
                return None
            
            if not model_name or model_name.startswith("画像") or model_name == "設定エラー":
                print("有効なモデルが選択されていません。")
                return None
            
            if not lot_number or lot_number.strip() == "":
                print("ロット番号が設定されていません。")
                return None
            
            # 設計書に従ったディレクトリ構造を作成
            save_dir = self.file_manager.create_lot_directory_structure(lot_number)

            print(f"保存ディレクトリを作成/確認しました: {save_dir}")
            return str(save_dir)
            
        except Exception as e:
            print(f"保存ディレクトリ作成エラー: {e}")
            return None
    
    def is_defective_info_file(self,index: int) -> bool:
        """不良情報ファイルが存在するか判定"""
        return self.file_manager.is_defective_info_file(index)

    def get_next_sequential_number(self, directory: str) -> int:
        """
        設計書に従った連番ファイル名の次の番号を取得
        ファイル命名規則: <ロット番号>_<識別番号>.json
        """
        if not self.ensure_file_manager():
            return 1
        
        try:
            # ディレクトリ内の最大識別番号を取得
            directory_path = Path(directory)
            if not directory_path.exists():
                return 1
            
            max_number = 0
            for json_file in directory_path.glob("*.json"):
                filename = json_file.stem
                # ロット番号_識別番号の形式をパース
                if "_" in filename:
                    parts = filename.split("_")
                    if len(parts) >= 2:
                        try:
                            number = int(parts[-1])
                            max_number = max(max_number, number)
                        except ValueError:
                            continue
            
            return max_number + 1
            
        except Exception as e:
            print(f"連番取得エラー: {e}")
            return 1
    
    def setup_save_name_entry(self, model_name: str, lot_number: str, current_save_name: str) -> str:
        """
        設計書に従った保存名を自動生成
        ファイル命名規則: <ロット番号>_<識別番号>.json
        """
        try:
            # 現在の保存名をチェック
            if current_save_name and current_save_name.strip():
                # 保存名が既に設定されている場合は変更しない
                return current_save_name
            
            # FileManagerの確認
            if not self.ensure_file_manager():
                return current_save_name
            
            # 保存ディレクトリを取得
            self.save_dir = self.setup_json_save_dir(model_name, lot_number)
            
            if self.save_dir:
                # 次の識別番号を取得
                next_sequence = self.file_manager.get_next_sequence_number(lot_number)
                
                # 設計書に従ったファイル名を生成: <ロット番号>_<識別番号>
                auto_save_name = self.file_manager.generate_sequential_filename(
                    lot_number, next_sequence
                ).replace('.json', '')  # 拡張子を除去
                
                print(f"保存名を自動設定しました: {auto_save_name}")
                return auto_save_name
            
            return current_save_name
                
        except Exception as e:
            print(f"保存名自動設定エラー: {e}")
            return current_save_name

    # ----------------------------
    # FileManager統合メソッド
    # ----------------------------
    def search_files(self, query: str, lot_number: str = None) -> List[Dict[str, str]]:
        """ファイル検索（FileManager使用）"""
        if not self.ensure_file_manager():
            return []
        
        return self.file_manager.search_files(query, lot_number)
    
    def move_file_to_history(self, file_path: str, lot_number: str) -> bool:
        """ファイルを履歴フォルダに退避（検査担当者のみ）"""
        if not self.ensure_file_manager():
            return False
        
        return self.file_manager.move_to_history(file_path, lot_number)
    
    def restore_file_from_history(self, original_path: str, lot_number: str) -> bool:
        """履歴から最新ファイルを復元（検査担当者のみ）"""
        if not self.ensure_file_manager():
            return False
        
        return self.file_manager.restore_latest(original_path, lot_number)
    
    def get_lot_files(self, lot_number: str, include_history: bool = False) -> List[Dict[str, str]]:
        """指定ロットの全ファイルを取得"""
        if not self.ensure_file_manager():
            return []
        
        return self.file_manager.get_lot_files(lot_number, include_history)
    
    def get_operation_logs(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, str]]:
        """操作ログを取得"""
        if not self.ensure_file_manager():
            return []
        
        return self.file_manager.get_operation_logs(start_date, end_date)
    
    def get_file_manager_statistics(self) -> Dict[str, int]:
        """ファイル管理統計情報を取得"""
        if not self.ensure_file_manager():
            return {}
        
        return self.file_manager.get_statistics()
    
    def check_user_permissions(self, user: str) -> Dict[str, bool]:
        """ユーザー権限をチェック"""
        if not self.ensure_file_manager():
            return {"view": False, "edit": False, "delete": False, "history": False}
        
        try:
            # 基本権限（全ユーザー）
            permissions = {
                "view": True,
                "edit": True,
                "delete": False,
                "history": False
            }
            
            # 管理者権限チェック
            try:
                # FileManagerのユーザー情報を一時的に変更してチェック
                original_user = self.file_manager.user
                self.file_manager.user = user
                self.file_manager.check_admin_permissions()
                
                # 権限ありの場合
                permissions["delete"] = True
                permissions["history"] = True
                
                # 元のユーザー情報に戻す
                self.file_manager.user = original_user
                
            except PermissionError:
                # 権限なしの場合はそのまま
                pass
            
            return permissions
            
        except Exception as e:
            print(f"権限チェックエラー: {e}")
            return {"view": False, "edit": False, "delete": False, "history": False}

    def get_json_lists(self) -> List[str]:

        save_dir = self.get_save_dir()
        if not save_dir:
            return []

        json_files = [
            f for f in os.listdir(save_dir) if f.endswith('.json')
        ]

        return json_files
    
    def reload_lot_info(self) -> List[str]:
        """lotInfo.jsonを更新"""
        return self.file_manager.reload_lot_info()

    def load_json_info(self) -> Dict[str,List[str]]:
        return self.file_manager.load_json_info()

    def create_defective_info_file(self, index: int, coordinates:List[Tuple[int, int]]=None, coordinate_details:List[Dict[str, Any]]=None) -> str:
        """不良情報ファイルを作成"""
        if not self.ensure_file_manager():
            return ""
        
        info_data = self.file_manager.create_defective_info_data(
            model=self.lot_model.model,
            coordinates=coordinates,
            image_path=self.lot_model.image_path,
            coordinate_details=coordinate_details,
            lot_number=self.lot_model.lot_no,
            worker_no=self.lot_model.worker_no
        )

        return self.file_manager.create_defective_info_file(index, info_data)

    def get_next_board_number(self, index:int) -> int:
        """次のボード番号を取得"""
        # jsonInfoからデータ取得
        json_data = self.load_json_info()

        # 存在するjsonファイルのリストを取得
        json_list = json_data.get("json_list",[])

        # jsonファイル名を生成
        file_name = f"{index:04d}.json"

        # json_listからfile_nameを探す
        file_name_index = json_list.index(file_name) if file_name in json_list else -1

        # file_name_indexが-1の場合は次のファイル名がないためエラー
        if file_name_index == -1:
            raise ValueError("ファイル名が見つかりません")

        # 次のファイル名を取得
        next_file_name = json_list[file_name_index + 1]

        # ファイル名から番号を抽出して整数に変換
        return int(next_file_name.split(".")[0])

    def get_previous_board_number(self, index: int) -> int:
        """前のボード番号を取得"""
        # jsonInfoからデータ取得
        json_data = self.load_json_info()

        # 存在するjsonファイルのリストを取得
        json_list = json_data.get("json_list",[])

        # jsonファイル名を生成
        file_name = f"{index:04d}.json"

        # json_listからfile_nameを探す
        file_name_index = json_list.index(file_name) if file_name in json_list else -1

        # file_name_indexが-1の場合またはインデックスが0の場合は前のファイル名がないためエラー
        if file_name_index <= 0:
            raise ValueError("前のファイルが見つかりません")

        # 前のファイル名を取得
        previous_file_name = json_list[file_name_index - 1]

        # ファイル名から番号を抽出して整数に変換
        return int(previous_file_name.split(".")[0])


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
    
    def check_and_fix_hidden_file(self, file_path: str) -> bool:
        """隠しファイル属性をチェックして必要に応じて解除"""
        if self.ensure_file_manager() and hasattr(self.file_manager, 'check_and_remove_hidden_attribute'):
            return self.file_manager.check_and_remove_hidden_attribute(Path(file_path))
        return False

    def reload_lot_info(self) -> bool:
        """lotInfo.jsonを安全に再読み込み（隠しファイル対応）"""
        try:
            if not self.ensure_file_manager():
                return False
                
            # FileManagerのlot_info.json更新機能を使用
            if hasattr(self.file_manager, 'reload_lot_info'):
                # 隠しファイル対応の再読み込み
                json_list = self.file_manager.reload_lot_info()
                print(f"[reload_lot_info] lotInfo.json再読み込み完了: {len(json_list)}件のファイル")
                return True
            else:
                print("[reload_lot_info] FileManager.reload_lot_info method not found")
                return False
                
        except Exception as e:
            print(f"[reload_lot_info] エラー: {e}")
            return False

    def show_warning_message(self, message: str, title: str = "警告"):
        """警告メッセージを表示"""
        messagebox.showwarning(title, message)

    def delete_current_file(self) -> bool:
        """
        現在のJSONファイルを履歴フォルダに移動（削除の代替）
        検査担当者権限が必要
        """
        try:
            # FileManagerの確認
            if not self.ensure_file_manager():
                self.show_error_message("ファイル管理システムが利用できません")
                return False
            
            # 現在のJSONファイルパスの確認
            if not self.current_json_path or not os.path.exists(self.current_json_path):
                self.show_error_message("削除対象のファイルが見つかりません")
                return False
            
            # ファイルパスから情報を抽出
            file_info = self._extract_file_info(self.current_json_path)
            if not file_info:
                self.show_error_message("ファイル情報の取得に失敗しました")
                return False
            
            # file_infoからworker_noとlot_numberを取得
            worker_no = file_info.get('worker_no', '不明')
            lot_number = file_info.get('lot_number', '')
            
            # 権限チェック
            try:
                self.file_manager.check_admin_permissions(worker_no)
            except PermissionError:
                self.show_error_message(
                    f"ファイル削除権限がありません。\n"
                )
                return False
            
            # 履歴フォルダに移動
            success = self.file_manager.move_to_history(
                self.current_json_path,
                lot_number,
                worker_no
            )
            
            if success:
                self.show_success_message(
                    f"ファイルの削除が完了しました:\n{os.path.basename(self.current_json_path)}"
                )
                # 現在のパスをクリア
                self.current_json_path = None
                return True
            else:
                self.show_error_message("ファイルの履歴移動に失敗しました")
                return False
                
        except Exception as e:
            self.show_error_message(f"ファイル削除処理中にエラーが発生しました:\n{str(e)}")
            return False
    
    def _extract_file_info(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        ファイルパスから情報を抽出
        パス形式: データディレクトリ/ロット番号/ファイル名.json
        """
        try:
            path_obj = Path(file_path)
            parts = path_obj.parts
            
            # 最低2つの階層が必要（データディレクトリ/ロット番号）
            if len(parts) < 2:
                return None
            
            # パスの最後から情報を抽出
            lot_number = parts[-2]      # ロット番号（ファイルの親ディレクトリ）
            
            # ロット番号の形式検証
            if not self.file_manager.validate_lot_number(lot_number):
                print(f"ロット番号の形式が不正: {lot_number}")
                return None
            
            # JSONファイルを読み込んで情報を取得
            json_data = json.loads(path_obj.read_text(encoding='utf-8-sig'))
            if not json_data:
                print(f"JSONファイルの読み込みに失敗: {file_path}")
                return None
            
            worker_no = json_data.get('worker_no', '不明')

            return {
                'lot_number': lot_number,
                'worker_no': worker_no
            }
            
        except Exception as e:
            print(f"ファイル情報抽出エラー: {e}")
            return None
