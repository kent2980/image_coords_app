"""
Worker Model
作業者情報を管理するモデル
"""

import os
import csv
from typing import Dict, Optional
from pathlib import Path


class WorkerModel:
    """作業者情報モデル"""
    
    def __init__(self):
        self._workers: Dict[str, str] = {}  # worker_no -> worker_name
        self._current_worker_no: Optional[str] = None
        self._current_worker_name: Optional[str] = None
        self._load_workers()
    
    def _get_executable_directory(self) -> str:
        """実行ファイルのディレクトリを取得"""
        import sys
        if getattr(sys, 'frozen', False):
            # PyInstallerでビルドされた実行ファイルの場合
            return os.path.dirname(sys.executable)
        else:
            # 開発環境の場合
            return os.path.dirname(os.path.abspath(__file__))
    
    def _load_workers(self):
        """worker.csvから作業者情報を読み込み"""
        try:
            # プロジェクトディレクトリのworker.csvを読み込み
            worker_file = os.path.join(
                Path(self._get_executable_directory()).parent.parent.as_posix(), 
                "worker.csv"
            )
            
            self._workers.clear()
            
            if os.path.exists(worker_file):
                with open(worker_file, 'r', encoding='utf-8') as f:
                    csv_reader = csv.reader(f)
                    for row in csv_reader:
                        if len(row) >= 2:
                            worker_no = row[0].strip()
                            worker_name = row[1].strip()
                            if worker_no and worker_name:
                                self._workers[worker_no] = worker_name
                
                print(f"作業者情報を読み込みました: {len(self._workers)}人")
            else:
                print(f"worker.csvが見つかりません: {worker_file}")
                
        except Exception as e:
            print(f"worker.csv読み込みエラー: {e}")
            self._workers.clear()
    
    def reload_workers(self):
        """作業者情報を再読み込み"""
        self._load_workers()
    
    def get_all_workers(self) -> Dict[str, str]:
        """全作業者情報を取得"""
        return self._workers.copy()
    
    def get_worker_name(self, worker_no: str) -> Optional[str]:
        """作業者番号から作業者名を取得"""
        return self._workers.get(worker_no)
    
    def is_valid_worker_no(self, worker_no: str) -> bool:
        """作業者番号が有効かチェック"""
        return worker_no in self._workers
    
    def set_current_worker(self, worker_no: str) -> bool:
        """現在の作業者を設定"""
        if worker_no in self._workers:
            self._current_worker_no = worker_no
            self._current_worker_name = self._workers[worker_no]
            return True
        else:
            # 存在しない作業者番号の場合も設定は可能（警告付き）
            self._current_worker_no = worker_no
            self._current_worker_name = f"不明({worker_no})"
            return False
    
    def get_current_worker_no(self) -> Optional[str]:
        """現在の作業者番号を取得"""
        return self._current_worker_no
    
    def get_current_worker_name(self) -> Optional[str]:
        """現在の作業者名を取得"""
        return self._current_worker_name
    
    def clear_current_worker(self):
        """現在の作業者情報をクリア"""
        self._current_worker_no = None
        self._current_worker_name = None
    
    def has_workers(self) -> bool:
        """作業者情報が存在するかチェック"""
        return len(self._workers) > 0
    
    def get_worker_count(self) -> int:
        """作業者数を取得"""
        return len(self._workers)
    
    def get_workers_list_text(self) -> str:
        """作業者リストをテキスト形式で取得"""
        return "\n".join([f"{no}: {name}" for no, name in self._workers.items()])
    
    def validate_worker_input(self, worker_no: str) -> Dict[str, any]:
        """作業者番号の入力を検証"""
        result = {
            'valid': False,
            'worker_no': worker_no.strip(),
            'worker_name': '',
            'error_message': ''
        }
        
        if not result['worker_no']:
            result['error_message'] = "作業者Noを入力してください。"
            return result
        
        if result['worker_no'] in self._workers:
            result['valid'] = True
            result['worker_name'] = self._workers[result['worker_no']]
        else:
            result['error_message'] = (
                f"作業者No '{result['worker_no']}' は存在しません。\n\n"
                f"利用可能な作業者:\n{self.get_workers_list_text()}"
            )
        
        return result
