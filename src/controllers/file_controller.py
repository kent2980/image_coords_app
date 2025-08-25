"""
ファイルコントローラー
ファイル操作とデータの保存・読み込みを制御
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from src.db.schema import Detail, DetailList, Lot, Worker

if TYPE_CHECKING:
    from ..models.coordinate_model import CoordinateModel
    from ..models.app_settings_model import AppSettingsModel
    from ..models.worker_model import WorkerModel
    from ..models.board_model import BoardModel
    from ..models.lot_model import LotModel

from pathlib import Path


class FileController:
    """ファイル操作を管理するコントローラー（FileManager統合版）"""

    def __init__(
        self,
        coordinate_model: "CoordinateModel",
        settings_model: "AppSettingsModel",
        worker_model: "WorkerModel",
        board_model: "BoardModel",
        lot_model: "LotModel",
    ):
        self.coordinate_model = coordinate_model
        self.settings_model = settings_model
        self.worker_model = worker_model
        self.board_model = board_model
        self.lot_model = lot_model

        # 現在の保存ディレクトリ
        self.save_dir = None

        # 現在のJSONファイルパス
        self.current_json_path = None

        # デフォルトの不良項目
        self.default_defects = None

        # ロットディレクトリ
        self.lot_directory = None

    def load_defects_from_file(self) -> List[str]:
        """defects.txtから不良項目を読み込み"""
        try:
            if os.path.exists("defects.txt"):
                with open("defects.txt", "r", encoding="utf-8") as f:
                    defects = [line.strip() for line in f if line.strip()]
                return defects if defects else self.default_defects
            else:
                return self.default_defects
        except Exception as e:
            print(f"不良項目読み込みエラー: {e}")
            return self.default_defects

    def init_lot_number_directory(self, lot_number: str):
        """ロット番号用のディレクトリを初期化"""
        data_root_path = self.settings_model.data_directory
        lot_directory = Path(data_root_path) / lot_number

        if not lot_directory.exists():
            lot_directory.mkdir(parents=True, exist_ok=True)

        self.lot_directory = lot_directory

        return self.lot_directory

    def create_lot_number_dir_lock_file(self) -> Path | None:
        """ロット番号ディレクトリのロックファイルを作成"""
        if self.lot_directory:
            lock_file_path = self.lot_directory / "lock"
            lock_file_path.touch(exist_ok=True)
            return lock_file_path
        return None

    def delete_lot_number_dir_lock_file(self) -> None:
        """ロット番号ディレクトリのロックファイルを削除"""
        if self.lot_directory:
            lock_file_path = self.lot_directory / "lock"
            if lock_file_path.exists():
                lock_file_path.unlink()

    def is_lock_file_exists(self) -> bool:
        """ロット番号ディレクトリにロックファイルが存在するかチェック"""
        if self.lot_directory:
            lock_file_path = self.lot_directory / "lock"
            return lock_file_path.exists()
        return False

    def get_lot_dir_data_list(self) -> List[Path]:
        """ロットディレクトリ内のdataファイル一覧を取得"""
        if not self.lot_directory:
            return []

        data_files = list(self.lot_directory.glob("*.data"))
        return [file for file in data_files if file.is_file()]

    def get_max_data_index(self, data_list: List[Path]) -> int:
        """dataファイルの最大インデックスを取得"""
        max_index = 0
        for data_file in data_list:
            try:
                index = int(
                    data_file.stem.split("_")[0]
                )  # ファイル名からインデックスを取得
                if index > max_index:
                    max_index = index
            except ValueError:
                continue
        return max_index

    def save_data_file(self, data_path: Path, data: Dict[str, Any]) -> bool:
        """dataデータをファイルに保存"""
        try:
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"data保存エラー: {e}")
            return False

    def create_lot_text(
        self, lot:Lot
    ) -> Optional[Path]:
        """ロットデータを作成"""
        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        json_path = self.lot_directory / "lotInfo.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(lot.model_dump(), f, ensure_ascii=False, indent=4)
            return json_path
        except Exception as e:
            print(f"ロットデータ保存エラー: {e}")
            return None
    
    def create_worker_text(self, worker: Worker) -> Path:
        """作業者情報を作成"""
        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        json_path = self.lot_directory / "workerInfo.json"
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(worker.model_dump(), f, ensure_ascii=False, indent=4)
            return json_path
        except Exception as e:
            print(f"作業者情報保存エラー: {e}")
            return None

    def create_detail_text(self, detail: Detail) -> Optional[Path]:
        """インデックス用のdataファイルを作成"""
        
        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        # ファイル名の生成
        index = detail.count_number
        next_index = index + 1
        index_str = f"{next_index:04d}"
        json_path = self.lot_directory / f"{index_str}.data"

        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(detail.model_dump(), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"インデックスデータファイル作成エラー: {e}")
            return None
        
        return json_path

    def read_index_data_file(self,index: int) -> DetailList:
        """インデックス用のdataファイルを読み込む"""
        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        json_path = self.lot_directory / f"{index:04d}.data"
        if not json_path.exists():
            raise FileNotFoundError(f"{json_path} が見つかりません。")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return DetailList(**data)
    
    def read_lot_text(self, lot: str) -> Optional[Lot]:
        """ロットデータを読み込む"""
        if not self.lot_directory:
            raise ValueError("ロットディレクトリが設定されていません。")

        json_path = self.lot_directory / "lotInfo.json"
        if not json_path.exists():
            raise FileNotFoundError(f"{json_path} が見つかりません。")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Lot(**data)
