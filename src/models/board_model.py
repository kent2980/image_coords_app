"""
基盤管理モデル
基盤の切り替えと管理を担当
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class BoardModel:
    """基盤データを管理するモデル"""

    def __init__(self):
        self._current_board_number: int = 1
        self._boards_data: Dict[int, Dict[str, Any]] = {}
        self._board_history: List[int] = []
        self._project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    @property
    def current_board_number(self) -> int:
        """現在の基盤番号"""
        return self._current_board_number

    @property
    def boards_data(self) -> Dict[int, Dict[str, Any]]:
        """全基盤データ"""
        return self._boards_data.copy()

    @property
    def board_history(self) -> List[int]:
        """基盤履歴"""
        return self._board_history.copy()

    def set_current_board(self, board_number: int) -> bool:
        """現在の基盤番号を設定"""
        if board_number > 0:
            # 履歴に現在の基盤を追加（重複は避ける）
            if self._current_board_number not in self._board_history:
                self._board_history.append(self._current_board_number)

            self._current_board_number = board_number
            return True
        return False

    def get_next_board_number(self) -> int:
        """次の基盤番号を取得"""
        return self._current_board_number + 1

    def get_previous_board_number(self) -> Optional[int]:
        """前の基盤番号を取得"""
        if self._current_board_number > 1:
            return self._current_board_number - 1
        return None

    def save_board_data(
        self,
        board_number: int,
        coordinates: List[Tuple[int, int]],
        coordinate_details: List[Dict[str, Any]],
        lot_number: str,
        worker_no: str,
        image_path: str,
        model_name: str = "",
    ) -> bool:
        """基盤データを保存"""
        try:
            board_data = {
                "board_number": board_number,
                "coordinates": coordinates,
                "coordinate_details": coordinate_details,
                "lot_number": lot_number,
                "worker_no": worker_no,
                "image_path": image_path,
                "model_name": model_name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "total_coordinates": len(coordinates),
            }

            self._boards_data[board_number] = board_data
            return True

        except Exception as e:
            print(f"基盤データ保存エラー: {e}")
            return False

    def get_board_data(self, board_number: int) -> Optional[Dict[str, Any]]:
        """基盤データを取得"""
        return self._boards_data.get(board_number)

    def delete_board_data(self, board_number: int) -> bool:
        """基盤データを削除"""
        if board_number in self._boards_data:
            del self._boards_data[board_number]

            # 履歴からも削除
            if board_number in self._board_history:
                self._board_history.remove(board_number)

            return True
        return False

    def get_board_count(self) -> int:
        """保存された基盤数を取得"""
        return len(self._boards_data)

    def get_board_list(self) -> List[int]:
        """基盤番号リストを取得（ソート済み）"""
        return sorted(self._boards_data.keys())

    def has_unsaved_changes(
        self,
        current_coordinates: List[Tuple[int, int]],
        current_details: List[Dict[str, Any]],
    ) -> bool:
        """現在の基盤に未保存の変更があるかチェック"""
        current_board_data = self._boards_data.get(self._current_board_number)

        if not current_board_data:
            # 基盤データが存在しない場合、座標があれば未保存
            return len(current_coordinates) > 0

        # 座標数の比較
        if len(current_coordinates) != len(current_board_data.get("coordinates", [])):
            return True

        # 座標内容の比較
        for i, coord in enumerate(current_coordinates):
            if (
                i >= len(current_board_data["coordinates"])
                or coord != current_board_data["coordinates"][i]
            ):
                return True

        # 詳細情報の比較（簡略版）
        if len(current_details) != len(
            current_board_data.get("coordinate_details", [])
        ):
            return True

        return False

    def save_board_info_to_file(
        self, date_str: str, model_name: str, lot_number: str
    ) -> bool:
        """基盤情報をJSONファイルに保存"""
        try:
            board_info_file = os.path.join(self._project_root, "board_info.json")

            # 既存の基盤情報を読み込み
            board_info = {}
            if os.path.exists(board_info_file):
                try:
                    with open(board_info_file, "r", encoding="utf-8") as f:
                        board_info = json.load(f)
                except (json.JSONDecodeError, Exception):
                    board_info = {}

            # キーを作成: "日付_モデル名_ロット番号"
            key = f"{date_str}_{model_name}_{lot_number}"

            # 基盤情報を更新
            board_info[key] = {
                "date": date_str,
                "model_name": model_name,
                "lot_number": lot_number,
                "current_board": self._current_board_number,
                "boards_data": self._boards_data,
                "board_history": self._board_history,
                "updated_at": datetime.now().isoformat(),
            }

            # ファイルに保存
            with open(board_info_file, "w", encoding="utf-8") as f:
                json.dump(board_info, f, ensure_ascii=False, indent=2)

            print(f"基盤情報をファイルに保存しました: {key}")
            return True

        except Exception as e:
            print(f"基盤情報ファイル保存エラー: {e}")
            return False

    def load_board_info_from_file(
        self, date_str: str, model_name: str, lot_number: str
    ) -> bool:
        """基盤情報をJSONファイルから読み込み"""
        try:
            board_info_file = os.path.join(self._project_root, "board_info.json")

            if not os.path.exists(board_info_file):
                return False

            with open(board_info_file, "r", encoding="utf-8") as f:
                board_info = json.load(f)

            # キーを作成: "日付_モデル名_ロット番号"
            key = f"{date_str}_{model_name}_{lot_number}"

            if key in board_info:
                data = board_info[key]
                self._current_board_number = data.get("current_board", 1)

                # 基盤データを復元
                boards_data_raw = data.get("boards_data", {})
                self._boards_data = {}
                for board_num_str, board_data in boards_data_raw.items():
                    self._boards_data[int(board_num_str)] = board_data

                self._board_history = data.get("board_history", [])

                print(f"基盤情報をファイルから読み込みました: {key}")
                print(f"現在の基盤番号: {self._current_board_number}")
                print(f"保存された基盤数: {len(self._boards_data)}")
                return True

            return False

        except Exception as e:
            print(f"基盤情報ファイル読み込みエラー: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """基盤管理の概要情報を取得"""
        return {
            "current_board": self._current_board_number,
            "total_boards": len(self._boards_data),
            "board_list": self.get_board_list(),
            "has_previous": self._current_board_number > 1,
            "board_history": self._board_history,
        }

    def reset(self):
        """基盤管理をリセット"""
        self._current_board_number = 1
        self._boards_data.clear()
        self._board_history.clear()
