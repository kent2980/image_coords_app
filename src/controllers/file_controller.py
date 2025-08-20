"""
ファイルコントローラー
ファイル操作とデータの保存・読み込みを制御
"""

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

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
