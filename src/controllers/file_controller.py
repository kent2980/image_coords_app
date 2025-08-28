"""
ファイルコントローラー
ファイル操作とデータの保存・読み込みを制御
"""

import json
import os
from typing import TYPE_CHECKING, List, Optional

from src.db.schema import Detail, Lot, Worker

if TYPE_CHECKING:
    from ..models.app_settings_model import AppSettingsModel

from pathlib import Path


class FileController:
    """ファイル操作を管理するコントローラー（FileManager統合版）"""

    def __init__(
        self,
        settings_model: "AppSettingsModel",
    ):
        self.settings_model = settings_model


    def load_defects_from_file(self) -> List[str]:
        """defects.txtから不良項目を読み込み"""
        try:
            if os.path.exists("defects.txt"):
                with open("defects.txt", "r", encoding="utf-8") as f:
                    defects = [line.strip() for line in f if line.strip()]
                return defects 
            else:
                raise ValueError("不良項目が見つかりませんでした。")
        except Exception as e:
            print(f"不良項目読み込みエラー: {e}")
            raise Exception("不良項目の読み込みに失敗しました。")

    def __create_lot_number_directory(self, lot_number: str) -> Path:
        """ロット番号用のディレクトリを初期化"""
        data_root_path = self.settings_model.data_directory
        lot_directory = Path(data_root_path) / lot_number

        if not lot_directory.exists():
            lot_directory.mkdir(parents=True, exist_ok=True)

        return lot_directory

    def create_lot_number_dir_lock_file(self, lot_number: str) -> Path | None:
        """ロット番号ディレクトリのロックファイルを作成"""
        lot_directory = self.__create_lot_number_directory(lot_number)
        if lot_directory:
            lock_file_path = lot_directory / "lock"
            lock_file_path.touch(exist_ok=True)
            return lock_file_path
        return None

    def delete_lot_number_dir_lock_file(self, lot_number: Optional[str] = None):
        """ロット番号ディレクトリのロックファイルを削除"""
        if not lot_number:
            # lot_numberがNoneや空文字なら何もしない
            return
        lot_directory = self.__create_lot_number_directory(lot_number)
        lock_file = lot_directory / "lock"
        if lock_file.exists():
            lock_file.unlink()

    def is_lock_file_exists(self, lot_number: str) -> bool:
        """ロット番号ディレクトリにロックファイルが存在するかチェック"""
        lot_directory = self.__create_lot_number_directory(lot_number)
        if lot_directory:
            lock_file_path = lot_directory / "lock"
            return lock_file_path.exists()
        return False

    def get_lot_dir_data_list(self, lot_number: str) -> List[Path]:
        """ロットディレクトリ内のdataファイル一覧を取得"""
        lot_directory = self.__create_lot_number_directory(lot_number)
        if not lot_directory:
            return []

        data_files = list(lot_directory.glob("*.data"))
        return [file for file in data_files if file.is_file()]
    
    def next_data_index(self, data_files: List[Path]) -> int:
        """次のデータインデックスを取得"""
        if not data_files:
            return 1

        # 既存のファイル名からインデックスを取得
        indices = [
            int(file.stem) for file in data_files if file.stem.isdigit()
        ]
        return max(indices) + 1 if indices else 1

    def create_lot_text(self, lot: Lot) -> Optional[Path]:
        """ロット情報を作成"""
        lot_directory = self.__create_lot_number_directory(lot.lot_number)
        json_path = lot_directory / "lotInfo.txt"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(lot.model_dump(), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"ロット情報保存エラー: {e}")
            return None
        return json_path

    def create_worker_text(self, lot_number: str, worker: Worker) -> Optional[Path]:
        """作業者情報を作成"""
        lot_directory = self.__create_lot_number_directory(lot_number)
        json_path = lot_directory / "workerInfo.txt"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(worker.model_dump(), f, ensure_ascii=False, indent=4)
            return json_path
        except Exception as e:
            print(f"作業者情報保存エラー: {e}")
            return None

    def create_detail_text(self, lot_number: str,index:int, detail: List[Detail] = None)-> Optional[Path]:
        """インデックス用のdataファイルを作成"""
        print("インデックスデータファイル作成")
        print(f"[DEBUG] ロット番号: {lot_number}, インデックス: {index}")
        lot_directory = self.__create_lot_number_directory(lot_number)
        if not lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        # ファイル名の生成
        index_str = f"{index:04d}"
        json_path = lot_directory / f"{index_str}.data"

        # list[Detail]をjsonに変換
        detail_json_list = [d.model_dump() for d in detail] if detail else []

        if not lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                if detail_json_list:
                    json.dump(detail_json_list, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"インデックスデータファイル作成エラー: {e}")
            return None
        
        return json_path

    def get_detail_text_count(self, lot_number: str) -> int:
        """ロット内のデータファイル数を取得"""
        data_files = self.get_lot_dir_data_list(lot_number)
        return len(data_files)

    def read_lot_text(self, lot_number: str) -> Optional[Lot]:
        """ロットデータを読み込む"""
        lot_directory = self.__create_lot_number_directory(lot_number)
        if not lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        json_path = lot_directory / "lotInfo.txt"
        if not json_path.exists():
            raise FileNotFoundError(f"{json_path} が見つかりません。")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Lot(**data)
