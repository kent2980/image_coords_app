"""
作業者データモデル
作業者情報を管理
"""

import csv
import os
from typing import Dict, List, Optional


class WorkerModel:
    """作業者データを管理するモデル"""

    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self._worker_file = os.path.join(project_root, "settings/worker.txt")
        self._current_worker_no: str = ""
        self._workers: Dict[str, str] = {}  # worker_no: worker_name
        self._load_workers()

    def _load_workers(self):
        """作業者データを読み込み"""
        try:
            if os.path.exists(self._worker_file):
                with open(self._worker_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) >= 2:
                            worker_no, worker_name = row[0].strip(), row[1].strip()
                            if worker_no and worker_name:
                                self._workers[worker_no] = worker_name
        except Exception as e:
            print(f"作業者データ読み込みエラー: {e}")

    def get_worker_name(self, worker_no: str) -> Optional[str]:
        """作業者番号から名前を取得"""
        return self._workers.get(worker_no)

    def add_worker(self, worker_no: str, worker_name: str) -> bool:
        """作業者を追加"""
        if not worker_no or not worker_name:
            return False

        self._workers[worker_no] = worker_name
        return self._save_workers()

    def update_worker(self, worker_no: str, worker_name: str) -> bool:
        """作業者情報を更新"""
        if worker_no in self._workers:
            self._workers[worker_no] = worker_name
            return self._save_workers()
        return False

    def remove_worker(self, worker_no: str) -> bool:
        """作業者を削除"""
        if worker_no in self._workers:
            del self._workers[worker_no]
            return self._save_workers()
        return False

    def _save_workers(self) -> bool:
        """作業者データを保存"""
        try:
            with open(self._worker_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                for worker_no, worker_name in self._workers.items():
                    writer.writerow([worker_no, worker_name])
            return True
        except Exception as e:
            print(f"作業者データ保存エラー: {e}")
            return False

    def get_all_workers(self) -> Dict[str, str]:
        """全作業者データを取得"""
        return self._workers.copy()

    def get_worker_numbers(self) -> List[str]:
        """作業者番号のリストを取得"""
        return list(self._workers.keys())

    def get_worker_names(self) -> List[str]:
        """作業者名のリストを取得"""
        return list(self._workers.values())

    def worker_exists(self, worker_no: str) -> bool:
        """作業者が存在するかチェック"""
        return worker_no in self._workers

    @property
    def current_worker_no(self) -> str:
        """現在の作業者番号"""
        return self._current_worker_no

    @current_worker_no.setter
    def current_worker_no(self, worker_no: str):
        """現在の作業者番号を設定"""
        self._current_worker_no = worker_no

    @property
    def current_worker_name(self) -> str:
        """現在の作業者名"""
        return self._workers.get(self._current_worker_no, "")

    def validate_worker_input(self, worker_input: str) -> Dict[str, any]:
        """作業者入力を検証"""
        result = {
            "valid": False,
            "worker_no": "",
            "worker_name": "",
            "is_new": False,
            "message": "",
        }

        if not worker_input.strip():
            result["message"] = "作業者情報が入力されていません"
            return result

        # 既存の作業者番号かチェック
        if worker_input in self._workers:
            result.update(
                {
                    "valid": True,
                    "worker_no": worker_input,
                    "worker_name": self._workers[worker_input],
                    "is_new": False,
                    "message": f"作業者: {self._workers[worker_input]}",
                }
            )
        else:
            # 新しい作業者として扱う
            result.update(
                {
                    "valid": True,
                    "worker_no": worker_input,
                    "worker_name": worker_input,  # 番号と名前を同じにする
                    "is_new": True,
                    "message": f"新規作業者: {worker_input}",
                }
            )

        return result
