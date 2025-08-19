import csv
import json
import os
import shutil
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import ctypes


class FileManager:
    """
    社内製造ライン向けファイル管理クラス
    
    設計仕様：
    - フォルダ構造: ロット番号/
    - ファイル命名: <ロット番号>_<識別番号>.json
    - 履歴管理: history/フォルダに退避（削除禁止）
    - 権限管理: 検査担当者のみ削除・履歴操作可能
    - 操作ログ: CSV形式で全操作を記録
    - バックアップ: 履歴フォルダ内にバックアップを保持
    - 検索機能: ファイル名部分一致、大文字小文字区別なし
    """

    def __init__(
        self,
        root_dir: str,
        user: str,
        search_limit: int = 100,
        file_extension: str = ".json",
    ):
        # ルートディレクトリと各サブディレクトリのパス設定
        self.root_dir = Path(root_dir)
        self.user = user
        self.log_file = self.root_dir / "operation_log.csv"
        self.file_lock = {}  # ファイルのロック状態を管理 {file_path: bool}
        self.search_limit = search_limit  # 検索結果の上限件数
        self.file_extension = file_extension  # 対象ファイル拡張子
        self.lot_dir = ""
        
        # 検査担当者の権限リスト
        self.authorized_users = ["検査担当者", "管理者", "admin", "inspector"]
        
        # ロット番号の正規表現パターン（7桁-2桁形式）
        self.lot_pattern = re.compile(r'^\d{7}-(10|20)$')

        # lotInfo.jsonのパス
        self.lot_info_path = ""
        
        # 初期処理：権限チェック、古い履歴削除、バックアップ作成
        self.check_permissions()  # 権限確認
        self.auto_delete_old_history()  # 古い履歴自動削除
        self.backup_files()  # ファイルバックアップ

    # ----------------------------
    # 権限チェック（設計書に従った権限管理）
    # ----------------------------
    def check_permissions(self) -> bool:
        """権限チェック：検査担当者のみ削除・履歴操作可能"""
        return True  # 基本的にはファイル閲覧は全ユーザー可能

    def check_admin_permissions(self, worker_no: str) -> bool:
        """管理者権限チェック：削除・履歴操作用"""
        if self.user != worker_no:
            raise PermissionError(f"このユーザーには削除・履歴操作権限がありません。検査担当者権限が必要です。")
        return True

    # ----------------------------
    # 社内製造ライン用フォルダ構造管理
    # ----------------------------
    def get_lot_directory_path(self, lot_number: str) -> Path:
        """設計書に従ったディレクトリパスを生成: ロット番号/"""
        return self.root_dir / lot_number
    
    def get_history_directory_path(self, lot_number: str) -> Path:
        """履歴ディレクトリパスを生成"""
        return self.get_lot_directory_path(lot_number) / "history"
    
    def get_backup_directory_path(self, lot_number: str) -> Path:
        """バックアップディレクトリパスを生成"""
        return self.get_history_directory_path(lot_number) / "backup"
    
    def create_lot_directory_structure(self, lot_number: str) -> Path:
        """ロット用ディレクトリ構造を作成"""
        self.lot_dir = self.get_lot_directory_path(lot_number)
        history_dir = self.get_history_directory_path(lot_number)
        backup_dir = self.get_backup_directory_path(lot_number)
        
        # ディレクトリを作成
        self.lot_dir.mkdir(parents=True, exist_ok=True)
        history_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.mkdir(parents=True, exist_ok=True)

        return self.lot_dir

    def create_defective_info_file(self, index:int, info_data: dict = None) -> str:
        """不良情報ファイルを作成"""

        if info_data is None:
            info_data = self.create_defective_info_data()

        defective_info_path = self.lot_dir / f"{index:04d}.json"
        # 空のjsonファイルを作成
        with open(defective_info_path, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, ensure_ascii=False, indent=4)
        return str(defective_info_path)

    def create_defective_info_data(self, model: str=None, coordinates: List[Tuple[int, int]]=None, image_path: str=None,
                    coordinate_details: List[Dict[str, Any]]=None, lot_number: str=None,
                    worker_no: str=None) -> Dict[str, Any]:
        """保存用データを作成"""
        return {
            'model': model,
            'coordinates': coordinates,
            'image_path': image_path,
            'coordinate_details': coordinate_details,
            'lot_number': lot_number,
            'worker_no': worker_no,
            'created_at': datetime.now().isoformat(),
            'total_coordinates': len(coordinates)
        }
    
    def is_defective_info_file(self,index: int) -> bool:
        """不良情報ファイルが存在するか判定"""
        return (self.lot_dir / f"{index:04d}.json").is_file()

    def reload_lot_info(self) -> List[str]:
        """ロット情報を再読み込み"""
        json_set = set()
        remove_set = set()
        # ロットディレクトリ内のJSONファイルをリストアップ
        # self.lot_dir配下のサブフォルダも含めてすべてのファイルをループ
        for json_file in self.lot_dir.rglob(f"*{self.file_extension}"):
            if json_file.is_file():
            # 例: ファイル名が4桁+拡張子の場合のみ追加
                if re.match(r'^\d{4}\.json$', json_file.name):
                    json_set.add(json_file.name)
                elif re.match(r'^\d{4}_.*json$', json_file.name):
                    remove_set.add(json_file.name)
        json_list = sorted(json_set)
        remove_list = sorted(remove_set)


        # lotInfo.jsonファイルの内容を隠しファイルとして上書き保存（存在しなくても新規作成される）
        lot_info_path = self.lot_dir / "lotInfo.json"
        
        # 隠しファイル対応の安全な書き込み
        data = {"json_list": json_list, "remove_list": remove_list}
        success = self.safe_write_json_file(lot_info_path, data, set_hidden=True)
        
        if not success:
            print(f"[reload_lot_info] lotInfo.json書き込みに失敗しました: {lot_info_path}")
            # 失敗してもプログラムは継続
        
        return json_list

    def load_json_info(self) -> Dict[str, List[str]]:
        """現在のロットのJSONファイル一覧を取得"""
        lot_info_path = self.lot_dir / "lotInfo.json"
        if not lot_info_path.is_file():
            return None

        with open(lot_info_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                "json_list": data.get("json_list", []),
                "remove_list": data.get("remove_list", [])
            }

    def validate_lot_number(self, lot_number: str) -> bool:
        """ロット番号の形式検証（7桁-2桁）"""
        return bool(self.lot_pattern.match(lot_number))
    
    def generate_sequential_filename(self, lot_number: str, sequence_number: int) -> str:
        """設計書に従ったファイル名生成: <ロット番号>_<識別番号>.json"""
        return f"{lot_number}_{sequence_number:03d}.json"
    
    def get_next_sequence_number(self, lot_number: str) -> int:
        """次の識別番号を取得（1から開始）"""
        lot_dir = self.get_lot_directory_path(lot_number)
        
        if not lot_dir.exists():
            return 1
        
        max_number = 0
        for file_path in lot_dir.glob(f"{lot_number}_*.json"):
            try:
                # ファイル名から識別番号を抽出
                filename = file_path.stem
                if '_' in filename:
                    parts = filename.split('_')
                    if len(parts) >= 2:
                        number_str = parts[-1]
                        if number_str.isdigit():
                            max_number = max(max_number, int(number_str))
            except (ValueError, IndexError):
                continue
        
        return max_number + 1

    # ----------------------------
    # バックアップ処理（設計書に従った実装）
    # ----------------------------
    def backup_files(self) -> None:
        """履歴フォルダ内のJSONファイルをバックアップ"""
        try:
            # ルートディレクトリ配下の全履歴ディレクトリを検索
            for history_dir in self.root_dir.rglob("history"):
                if not history_dir.is_dir():
                    continue
                
                backup_dir = history_dir / "backup"
                backup_dir.mkdir(exist_ok=True)
                
                # 履歴フォルダ内のJSONファイルをバックアップ
                for json_file in history_dir.glob(f"*{self.file_extension}"):
                    if json_file.is_file():
                        backup_file = backup_dir / json_file.name
                        try:
                            shutil.copy2(json_file, backup_file)
                        except Exception as e:
                            print(f"バックアップエラー: {json_file} -> {backup_file}, {e}")
                            
        except Exception as e:
            print(f"バックアップ処理エラー: {e}")

    # ----------------------------
    # 自動削除（古い履歴・バックアップ：1年保持）
    # ----------------------------
    def auto_delete_old_history(self) -> None:
        """1年以上古い履歴・バックアップファイルを自動削除"""
        cutoff_date = datetime.now() - timedelta(days=365)  # 1年前
        cutoff_timestamp = cutoff_date.timestamp()
        
        try:
            # 全ての履歴・バックアップディレクトリを検索
            for folder_pattern in ["history", "backup"]:
                for folder in self.root_dir.rglob(folder_pattern):
                    if not folder.is_dir():
                        continue
                    
                    for file_path in folder.glob(f"*{self.file_extension}"):
                        if file_path.is_file():
                            try:
                                file_mtime = file_path.stat().st_mtime
                                if file_mtime < cutoff_timestamp:
                                    file_path.unlink()
                                    self.log_action("auto_delete_old", str(file_path))
                                    print(f"古いファイルを削除: {file_path}")
                            except Exception as e:
                                print(f"ファイル削除エラー: {file_path}, {e}")
                                
        except Exception as e:
            print(f"自動削除処理エラー: {e}")

    # ----------------------------
    # ファイル検索機能（部分一致・設計書仕様）
    # ----------------------------
    def search_files(self, query: str, lot_number: str = None) -> List[Dict[str, str]]:
        """
        ファイル検索（大文字小文字区別なし、部分一致）
        
        Returns:
            List[Dict]: [{"file_path": str, "lot_number": str, "sequence": str, "created": str}]
        """
        results = []
        query_lower = query.lower()
        
        try:
            # 検索対象ディレクトリを決定
            if lot_number:
                search_root = self.root_dir / lot_number
            else:
                search_root = self.root_dir
            
            if not search_root.exists():
                return results
            
            # JSONファイルを再帰的に検索
            for json_file in search_root.rglob(f"*{self.file_extension}"):
                if not json_file.is_file():
                    continue
                
                # historyフォルダは除外（設計書仕様）
                if "history" in json_file.parts:
                    continue
                
                filename = json_file.name.lower()
                if query_lower in filename:
                    # ファイル情報を抽出
                    file_info = self._extract_file_info(json_file)
                    results.append(file_info)
                    
                    # 上限チェック
                    if len(results) >= self.search_limit:
                        break
                        
        except Exception as e:
            print(f"検索エラー: {e}")
        
        # 作成日時順でソート
        results.sort(key=lambda x: x.get("created", ""), reverse=True)
        return results
    
    def _extract_file_info(self, file_path: Path) -> Dict[str, str]:
        """ファイル情報を抽出"""
        try:
            stat = file_path.stat()
            created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
            
            # ファイル名からロット番号と識別番号を抽出
            filename = file_path.stem
            lot_number = ""
            sequence = ""
            
            if "_" in filename:
                parts = filename.split("_")
                if len(parts) >= 2:
                    lot_number = "_".join(parts[:-1])
                    sequence = parts[-1]
            
            return {
                "file_path": str(file_path),
                "lot_number": lot_number,
                "sequence": sequence,
                "created": created_time,
                "filename": file_path.name
            }
            
        except Exception:
            return {
                "file_path": str(file_path),
                "lot_number": "",
                "sequence": "",
                "created": "",
                "filename": file_path.name
            }

    # ----------------------------
    # 隠しファイル対応ユーティリティ
    # ----------------------------
    def check_and_remove_hidden_attribute(self, file_path: Path) -> bool:
        """隠しファイル属性をチェックして一時的に解除"""
        try:
            if not file_path.exists():
                return False
                
            import subprocess
            result = subprocess.run(['attrib', str(file_path)], capture_output=True, text=True)
            if result.returncode == 0 and 'H' in result.stdout:
                # 隠しファイル属性を解除
                remove_result = subprocess.run(['attrib', '-H', str(file_path)], capture_output=True, text=True)
                if remove_result.returncode == 0:
                    print(f"[check_hidden] 隠しファイル属性を解除: {file_path}")
                    return True
                else:
                    print(f"[check_hidden] 隠しファイル属性解除失敗: {remove_result.stderr}")
                    return False
            return False  # 隠しファイルではない
            
        except Exception as e:
            print(f"[check_hidden] 隠しファイル属性チェックエラー: {e}")
            return False
    
    def set_hidden_attribute(self, file_path: Path) -> bool:
        """ファイルに隠しファイル属性を設定"""
        try:
            FILE_ATTRIBUTE_HIDDEN = 0x02
            result = ctypes.windll.kernel32.SetFileAttributesW(str(file_path), FILE_ATTRIBUTE_HIDDEN)
            if result:
                print(f"[set_hidden] 隠しファイル属性を設定: {file_path}")
                return True
            else:
                print(f"[set_hidden] 隠しファイル属性設定失敗: {file_path}")
                return False
        except Exception as e:
            print(f"[set_hidden] 隠しファイル属性設定エラー: {e}")
            return False
    
    def safe_write_json_file(self, file_path: Path, data: dict, set_hidden: bool = False, max_retries: int = 3) -> bool:
        """隠しファイル対応の安全なJSON書き込み"""
        import time
        
        # 既存ファイルが隠しファイルの場合は一時的に属性を解除
        was_hidden = self.check_and_remove_hidden_attribute(file_path)
        
        # 書き込み処理（リトライ付き）
        for attempt in range(max_retries):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                # 書き込み成功
                print(f"[safe_write_json] ファイル書き込み成功: {file_path}")
                
                # 隠しファイル属性を設定（必要な場合）
                if set_hidden or was_hidden:
                    self.set_hidden_attribute(file_path)
                
                return True
                
            except PermissionError as pe:
                print(f"[safe_write_json] 書き込み試行 {attempt + 1}/{max_retries} 失敗: {pe}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)  # 0.5秒待機してリトライ
                else:
                    print(f"[safe_write_json] 全ての書き込み試行が失敗: {file_path}")
                    # 失敗した場合でも元の隠しファイル属性を復元
                    if was_hidden:
                        self.set_hidden_attribute(file_path)
                    return False
            except Exception as e:
                print(f"[safe_write_json] 書き込みエラー {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    # 失敗した場合でも元の隠しファイル属性を復元
                    if was_hidden:
                        self.set_hidden_attribute(file_path)
                    return False
                time.sleep(0.2)
        
        return False

    # ----------------------------
    # JSONファイル操作
    # ----------------------------
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """JSONファイルを読み込み"""
        try:
            file_path_obj = Path(file_path)
            with open(file_path_obj, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.log_action("open_file", file_path)
            return data
            
        except Exception as e:
            raise Exception(f"JSONファイル読み込みエラー: {e}")
    
    def save_file(self, file_path: str, data: Dict[str, Any]) -> bool:
        """JSONファイルを保存（隠しファイル対応）"""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 隠しファイル対応の安全な書き込み
            success = self.safe_write_json_file(file_path_obj, data, set_hidden=False)
            
            if success:
                self.log_action("save_file", file_path)
                return True
            else:
                print(f"JSONファイル保存エラー: {file_path}")
                return False
            
        except Exception as e:
            print(f"JSONファイル保存エラー: {e}")
            return False

    # ----------------------------
    # 履歴管理（設計書仕様：削除禁止、履歴フォルダへ退避）
    # ----------------------------
    def move_to_history(self, file_path: str, lot_number: str = None, worker_no: str = None) -> bool:
        """
        ファイルを履歴フォルダに退避（削除の代わり）
        検査担当者のみ実行可能
        """
        try:
            # 権限チェック
            self.check_admin_permissions(worker_no)
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            
            # 履歴ディレクトリを決定
            if lot_number:
                history_dir = self.get_history_directory_path(lot_number)
            else:
                # ファイルパスから推定
                history_dir = file_path_obj.parent / "history"
            
            history_dir.mkdir(parents=True, exist_ok=True)
            
            # タイムスタンプ付きファイル名で退避
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            original_name = file_path_obj.stem
            new_name = f"{original_name}_{timestamp}{self.file_extension}"
            dest_path = history_dir / new_name
            
            # ファイルを移動
            shutil.move(file_path_obj, dest_path)
            
            # 整合性チェック
            if not self.check_file_integrity(file_path, str(dest_path)):
                print(f"警告: ファイル整合性チェックに失敗: {dest_path}")
            
            self.log_action("move_to_history", str(dest_path))
            print(f"ファイルを履歴に退避: {file_path} -> {dest_path}")
            return True
            
        except PermissionError as e:
            print(f"権限エラー: {e}")
            return False
        except Exception as e:
            print(f"履歴退避エラー: {e}")
            return False

    def restore_latest(self, original_path: str, lot_number: str = None) -> bool:
        """
        最新履歴を復元（検査担当者のみ）
        """
        try:
            # 権限チェック
            self.check_admin_permissions()
            
            original_path_obj = Path(original_path)
            
            # 履歴ディレクトリを決定
            if lot_number:
                history_dir = self.get_history_directory_path(lot_number)
            else:
                history_dir = original_path_obj.parent / "history"
            
            if not history_dir.exists():
                print("履歴フォルダが存在しません")
                return False
            
            # 対象ファイルの履歴を検索
            original_stem = original_path_obj.stem
            history_files = list(history_dir.glob(f"{original_stem}_*{self.file_extension}"))
            
            if not history_files:
                print("復元可能な履歴が見つかりません")
                return False
            
            # 最新の履歴ファイルを取得（ファイル名のタイムスタンプで判定）
            latest_file = max(history_files, key=lambda x: x.stat().st_mtime)
            
            # 元の場所に復元
            original_path_obj.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(latest_file, original_path_obj)
            
            self.log_action("restore_latest", original_path)
            print(f"履歴を復元: {latest_file} -> {original_path}")
            return True
            
        except PermissionError as e:
            print(f"権限エラー: {e}")
            return False
        except Exception as e:
            print(f"復元エラー: {e}")
            return False

    def get_history_files(self, lot_number: str) -> List[Dict[str, str]]:
        """指定ロットの履歴ファイル一覧を取得"""
        history_dir = self.get_history_directory_path(lot_number)
        
        if not history_dir.exists():
            return []
        
        history_files = []
        for json_file in history_dir.glob(f"*{self.file_extension}"):
            if json_file.is_file() and json_file.parent.name != "backup":
                file_info = self._extract_file_info(json_file)
                history_files.append(file_info)
        
        # 日時順でソート
        history_files.sort(key=lambda x: x.get("created", ""), reverse=True)
        return history_files

    # ----------------------------
    # 操作ログ記録（設計書仕様）
    # ----------------------------
    def log_action(self, action: str, file_path: str) -> None:
        """操作ログをCSV形式で記録"""
        try:
            header = ["timestamp", "user", "action", "file_path"]
            log_exists = self.log_file.exists()
            
            with open(self.log_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not log_exists:
                    writer.writerow(header)  # 新規ファイルならヘッダーを書き込み
                writer.writerow([
                    datetime.now().isoformat(), 
                    self.user, 
                    action, 
                    file_path
                ])
                
        except Exception as e:
            print(f"ログ記録エラー: {e}")

    def get_operation_logs(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, str]]:
        """操作ログを取得"""
        logs = []
        
        if not self.log_file.exists():
            return logs
        
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 日付フィルタ
                    if start_date or end_date:
                        try:
                            log_time = datetime.fromisoformat(row["timestamp"])
                            if start_date and log_time < start_date:
                                continue
                            if end_date and log_time > end_date:
                                continue
                        except ValueError:
                            continue
                    
                    logs.append(row)
                    
        except Exception as e:
            print(f"ログ読み込みエラー: {e}")
        
        return logs

    # ----------------------------
    # ファイルロック管理
    # ----------------------------
    def lock_file(self, file_path: str) -> bool:
        """ファイルをロック（同時アクセス制御）"""
        if file_path in self.file_lock and self.file_lock[file_path]:
            print(f"ファイルは既にロックされています: {file_path}")
            return False
        
        self.file_lock[file_path] = True
        self.log_action("lock_file", file_path)
        return True

    def unlock_file(self, file_path: str) -> None:
        """ファイルロックを解除"""
        if file_path in self.file_lock:
            self.file_lock[file_path] = False
            self.log_action("unlock_file", file_path)

    def is_file_locked(self, file_path: str) -> bool:
        """ファイルがロックされているかチェック"""
        return self.file_lock.get(file_path, False)

    # ----------------------------
    # ファイル整合性チェック
    # ----------------------------
    def check_file_integrity(self, src: str, dest: str) -> bool:
        """ファイル内容の整合性をチェック"""
        try:
            src_path = Path(src)
            dest_path = Path(dest)
            
            if not src_path.exists() or not dest_path.exists():
                return False
            
            # バイナリ読み込みでファイル内容比較
            with open(src_path, "rb") as f1, open(dest_path, "rb") as f2:
                return f1.read() == f2.read()
                
        except Exception as e:
            print(f"整合性チェックエラー: {e}")
            return False

    # ----------------------------
    # 便利なユーティリティメソッド
    # ----------------------------
    def get_lot_files(self, lot_number: str, include_history: bool = False) -> List[Dict[str, str]]:
        """指定ロットの全ファイルを取得"""
        files = []
        
        # メインディレクトリのファイル
        lot_dir = self.get_lot_directory_path(lot_number)
        if lot_dir.exists():
            for json_file in lot_dir.glob(f"*{self.file_extension}"):
                if json_file.is_file():
                    file_info = self._extract_file_info(json_file)
                    file_info["type"] = "current"
                    files.append(file_info)
        
        # 履歴ファイルも含める場合
        if include_history:
            history_files = self.get_history_files(lot_number)
            for history_file in history_files:
                history_file["type"] = "history"
                files.append(history_file)
        
        return files
    
    def cleanup_locks(self) -> None:
        """すべてのファイルロックを解除（アプリ終了時等）"""
        for file_path in list(self.file_lock.keys()):
            if self.file_lock[file_path]:
                self.unlock_file(file_path)
    
    def get_statistics(self) -> Dict[str, int]:
        """ファイル管理統計情報を取得"""
        stats = {
            "total_files": 0,
            "history_files": 0,
            "backup_files": 0,
            "locked_files": 0
        }
        
        try:
            # 全ファイル数
            for json_file in self.root_dir.rglob(f"*{self.file_extension}"):
                if json_file.is_file():
                    stats["total_files"] += 1
                    
                    if "history" in json_file.parts:
                        if json_file.parent.name == "backup":
                            stats["backup_files"] += 1
                        else:
                            stats["history_files"] += 1
            
            # ロックファイル数
            stats["locked_files"] = sum(1 for locked in self.file_lock.values() if locked)
            
        except Exception as e:
            print(f"統計情報取得エラー: {e}")
        
        return stats
