import csv
import json
import os
import shutil
from datetime import datetime


class FileManager:
    """
    ファイル管理を行うクラス
    ### 機能:
    - ファイルの検索
    - JSONファイルの読み込み
    - ファイルの履歴管理
    - 操作ログの記録
    - ファイルのバックアップ
    - ファイルのロック管理
    - ファイルの整合性チェック
    ### 説明:
    このクラスは、指定されたルートディレクトリ内のファイルを管理し、様々な操作を提供します。
    例えば、ファイルの検索、JSONファイルの読み込み、履歴管理、操作ログの記録などが可能です。
    このクラスを使用することで、ファイル操作の効率化と安全性を向上させることができます。
    """

    def __init__(
        self,
        root_dir: str,
        user: str,
        search_limit: int = 100,
        file_extension: str = ".json",
    ):
        # ルートディレクトリと各サブディレクトリのパスを設定
        self.root_dir = root_dir
        self.history_dir = os.path.join(root_dir, "history")
        self.backup_dir = os.path.join(self.history_dir, "backup")
        self.user = user
        self.log_file = os.path.join(self.root_dir, "operation_log.csv")
        self.file_lock = {}  # ファイルのロック状態を管理する辞書 {file_path: bool}
        self.search_limit = search_limit  # 検索結果の上限件数
        self.file_extension = file_extension  # 対象ファイル拡張子

        # 初期処理：権限チェック、古い履歴削除、バックアップ作成
        self.check_permissions()  # 権限があるか確認
        self.auto_delete_old_history()  # 古い履歴を自動削除
        self.backup_files()  # 履歴ファイルをバックアップ

    # ----------------------------
    # 権限チェック
    # ----------------------------
    def check_permissions(self) -> bool:
        allowed_users = ["検査担当者"]  # 操作可能なユーザー
        if self.user not in allowed_users:
            raise PermissionError(f"{self.user}には操作権限がありません。")
        return True

    # ----------------------------
    # バックアップ処理
    # ----------------------------
    def backup_files(self) -> None:
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)  # バックアップフォルダがなければ作成
        # 履歴フォルダ内の全てのJSONファイルをバックアップ
        for root, _, files in os.walk(self.history_dir):
            for f in files:
                if f.endswith(self.file_extension):
                    src = os.path.join(root, f)
                    dst = os.path.join(self.backup_dir, f)
                    shutil.copy2(src, dst)  # ファイル内容とタイムスタンプをコピー

    # ----------------------------
    # 自動削除（古い履歴・バックアップ）
    # ----------------------------
    def auto_delete_old_history(self) -> None:
        cutoff_date = (
            datetime.now().timestamp() - 365 * 24 * 60 * 60
        )  # 1年前のタイムスタンプ
        for folder in [self.history_dir, self.backup_dir]:
            if not os.path.exists(folder):
                continue
            for f in os.listdir(folder):
                path = os.path.join(folder, f)
                # ファイルが1年以上前なら削除
                if os.path.isfile(path) and os.path.getmtime(path) < cutoff_date:
                    os.remove(path)

    # ----------------------------
    # ファイル検索機能（部分一致）
    # ----------------------------
    def search_files(self, query: str) -> list[str]:
        result = []
        query = query.lower()  # 大文字小文字を区別しない検索
        for root, _, files in os.walk(self.root_dir):
            for f in files:
                if f.endswith(self.file_extension) and query in f.lower():
                    result.append(os.path.join(root, f))
                    if len(result) >= self.search_limit:
                        return result  # 上限件数に達したら返す
        return result

    # ----------------------------
    # JSONファイルを開く
    # ----------------------------
    def open_file(self, file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------------------
    # ファイルを履歴フォルダに退避
    # ----------------------------
    def move_to_history(self, file_path: str) -> None:
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
        filename = os.path.basename(file_path)
        # ファイル名にタイムスタンプを付加してリネーム
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        new_name = f"{os.path.splitext(filename)[0]}_{timestamp}{self.file_extension}"
        dst = os.path.join(self.history_dir, new_name)
        shutil.move(file_path, dst)  # 元ファイルを履歴フォルダに移動
        self.check_file_integrity(file_path, dst)  # 移動後の整合性チェック
        self.log_action("move_to_history", dst)  # 操作ログを記録

    # ----------------------------
    # 最新履歴を復元
    # ----------------------------
    def restore_latest(self, original_path: str) -> None:
        # 対象ファイルに対応する履歴ファイルを全て取得
        history_files = [
            f
            for f in os.listdir(self.history_dir)
            if f.startswith(os.path.splitext(os.path.basename(original_path))[0])
        ]
        if not history_files:
            return  # 履歴がない場合は処理しない
        # 最新の更新日時のファイルを取得
        latest_file = max(
            history_files,
            key=lambda x: os.path.getmtime(os.path.join(self.history_dir, x)),
        )
        src = os.path.join(self.history_dir, latest_file)
        shutil.copy2(src, original_path)  # 最新履歴を元ファイルに復元
        self.log_action("restore_latest", original_path)  # 操作ログを記録

    # ----------------------------
    # 操作ログ記録
    # ----------------------------
    def log_action(self, action: str, file_path: str) -> None:
        header = ["timestamp", "user", "action", "file_path"]
        exists = os.path.exists(self.log_file)
        with open(self.log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not exists:
                writer.writerow(header)  # 新規ファイルならヘッダーを書き込む
            writer.writerow([datetime.now().isoformat(), self.user, action, file_path])

    # ----------------------------
    # ファイルロック
    # ----------------------------
    def lock_file(self, file_path: str) -> None:
        self.file_lock[file_path] = True  # ファイルをロック状態にする

    def unlock_file(self, file_path: str) -> None:
        self.file_lock[file_path] = False  # ファイルロックを解除

    # ----------------------------
    # ファイル整合性チェック
    # ----------------------------
    def check_file_integrity(self, src: str, dest: str) -> bool:
        # バイナリ読み込みでファイル内容が一致するか確認
        with open(src, "rb") as f1, open(dest, "rb") as f2:
            return f1.read() == f2.read()
