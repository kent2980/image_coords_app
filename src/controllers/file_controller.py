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
        self.default_defects = [
            "ズレ",
            "裏",
            "飛び",
            "傷",
            "汚れ",
            "欠け",
            "変色",
            "寸法不良",
            "形状不良",
            "その他",
        ]

    def initialize_file_manager(self, current_user: str = "作業者"):
        """FileManagerを初期化"""
        pass

    # ゲッター関数
    def get_save_dir(self) -> Optional[str]:
        """現在の保存ディレクトリを取得"""
        return self.save_dir

    def get_current_json_path(self) -> Optional[str]:
        """現在のJSONファイルパスを取得"""
        return self.current_json_path

    def set_current_json_path(self, board_number: int):
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
            ("すべてのファイル", "*.*"),
        ]

        initial_dir = self.settings_model.image_directory
        if initial_dir == "未選択":
            initial_dir = None

        file_path = filedialog.askopenfilename(
            title="画像ファイルを選択", filetypes=filetypes, initialdir=initial_dir
        )

        return file_path if file_path else None

    def select_json_file(self) -> Optional[str]:
        """JSONファイルを選択"""
        filetypes = [("JSONファイル", "*.json"), ("すべてのファイル", "*.*")]

        initial_dir = self.settings_model.data_directory
        if initial_dir == "未選択":
            initial_dir = None

        file_path = filedialog.askopenfilename(
            title="JSONファイルを選択", filetypes=filetypes, initialdir=initial_dir
        )

        return file_path if file_path else None

    def save_json_file(
        self, default_filename: str = "coordinates.json"
    ) -> Optional[str]:
        """JSON保存先を選択"""
        filetypes = [("JSONファイル", "*.json"), ("すべてのファイル", "*.*")]

        initial_dir = self.settings_model.data_directory
        if initial_dir == "未選択":
            initial_dir = None

        file_path = filedialog.asksaveasfilename(
            title="座標をJSONで保存",
            defaultextension=".json",
            filetypes=filetypes,
            initialdir=initial_dir,
            initialfile=default_filename,
        )

        return file_path if file_path else None

    def load_json_data(self, file_path: str) -> Dict[str, Any]:
        """JSONファイルを読み込み"""
        try:
            # 最初にutf-8-sigで試行（BOM付きUTF-8対応）
            try:
                with open(file_path, "r", encoding="utf-8-sig") as f:
                    data = json.load(f)
                print(f"[JSON読み込み] UTF-8 (BOM対応) で読み込み成功: {file_path}")
                return data
            except UnicodeDecodeError:
                # utf-8-sigで失敗した場合はcp932（Shift_JIS）で試行
                try:
                    with open(file_path, "r", encoding="cp932") as f:
                        data = json.load(f)
                    print(
                        f"[JSON読み込み] CP932 (Shift_JIS) で読み込み成功: {file_path}"
                    )
                    return data
                except UnicodeDecodeError:
                    # それでも失敗した場合はutf-8で試行
                    with open(file_path, "r", encoding="utf-8") as f:
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

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # 現在のJSONファイルパスを記録
            self.current_json_path = file_path
            return True
        except Exception as e:
            raise Exception(f"JSONファイル保存エラー: {e}")

    def create_save_data(
        self,
        model: str,
        coordinates: List[Tuple[int, int]],
        image_path: str,
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
        worker_no: str,
    ) -> Dict[str, Any]:
        """保存用データを作成"""
        pass

    def parse_loaded_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """読み込んだデータを解析"""
        pass

    def get_automatic_save_path(self, lot_number: str, save_name: str) -> Optional[str]:
        """自動保存パスを生成"""
        pass

    def get_next_sequential_number(self, directory: str) -> int:
        """次の連番を取得"""
        pass

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

    def save_coordinates_with_auto_update(
        self,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
        worker_no: str,
        model: str = "",
    ) -> bool:
        """座標データを自動更新保存（現在のJSONファイルに）"""
        pass

    def validate_image_path(self, image_path: str) -> bool:
        """画像パスの検証"""
        pass

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
        pass

    def setup_json_save_dir(self, model_name: str, lot_number: str) -> Optional[str]:
        """
        設計書に従ったJSONファイル保存先ディレクトリを作成
        フォルダ構造: データディレクトリ/ロット番号/
        """
        pass

    def is_defective_info_file(self, index: int) -> bool:
        """不良情報ファイルが存在するか判定"""
        pass

    def get_next_sequential_number(self, directory: str) -> int:
        """
        設計書に従った連番ファイル名の次の番号を取得
        ファイル命名規則: <ロット番号>_<識別番号>.json
        """
        pass

    def setup_save_name_entry(
        self, model_name: str, lot_number: str, current_save_name: str
    ) -> str:
        """
        設計書に従った保存名を自動生成
        ファイル命名規則: <ロット番号>_<識別番号>.json
        """
        pass

    def search_files(self, query: str, lot_number: str = None) -> List[Dict[str, str]]:
        """ファイル検索（FileManager使用）"""
        pass

    def move_file_to_history(self, file_path: str, lot_number: str) -> bool:
        """ファイルを履歴フォルダに退避（検査担当者のみ）"""
        pass

    def restore_file_from_history(self, original_path: str, lot_number: str) -> bool:
        """履歴から最新ファイルを復元（検査担当者のみ）"""
        pass

    def get_lot_files(
        self, lot_number: str, include_history: bool = False
    ) -> List[Dict[str, str]]:
        """指定ロットの全ファイルを取得"""
        pass

    def get_operation_logs(
        self, start_date: datetime = None, end_date: datetime = None
    ) -> List[Dict[str, str]]:
        """操作ログを取得"""
        pass

    def get_file_manager_statistics(self) -> Dict[str, int]:
        """ファイル管理統計情報を取得"""
        pass

    def check_user_permissions(self, user: str) -> Dict[str, bool]:
        """ユーザー権限をチェック"""
        pass

    def get_json_lists(self) -> List[str]:
        pass

    def get_next_board_number(self, index: int) -> int:
        pass

    def get_previous_board_number(self, index: int) -> int:
        pass

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
        pass

    def reload_lot_info(self) -> bool:
        """lotInfo.jsonを安全に再読み込み（隠しファイル対応）"""
        pass

    def show_warning_message(self, message: str, title: str = "警告"):
        """警告メッセージを表示"""
        messagebox.showwarning(title, message)

    def delete_current_file(self) -> bool:
        """
        現在のJSONファイルを履歴フォルダに移動（削除の代替）
        検査担当者権限が必要
        """
        pass

    def _extract_file_info(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        ファイルパスから情報を抽出
        パス形式: データディレクトリ/ロット番号/ファイル名.json
        """
        pass
