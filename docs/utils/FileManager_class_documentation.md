# FileManager クラス詳細仕様書

## 概要

`FileManager`クラスは、Image Coordinates Appの社内製造ライン向けファイル管理機能を提供します。設計書に従った厳密なフォルダ構造の管理、権限制御、履歴管理、操作ログを実現しています。

## クラス設計

### 基本情報

- **ファイル**: `src/utils/file_manager_class.py`
- **クラス名**: `FileManager`
- **継承**: なし
- **実装インターフェース**: なし

### 設計原則

```python
"""
社内製造ライン向けファイル管理クラス

設計仕様：
- フォルダ構造: 日付/モデル名/ロット番号/
- ファイル命名: <ロット番号>_<識別番号>.json
- 履歴管理: history/フォルダに退避（削除禁止）
- 権限管理: 検査担当者のみ削除・履歴操作可能
- 操作ログ: CSV形式で全操作を記録
- バックアップ: 履歴フォルダ内にバックアップを保持
- 検索機能: ファイル名部分一致、大文字小文字区別なし
"""
```

## 初期化

### コンストラクタ

```python
def __init__(self, root_dir: str, user: str, search_limit: int = 100, file_extension: str = ".json")
```

#### パラメータ

| パラメータ | 型 | 説明 | デフォルト値 |
|-----------|----|----|------------|
| `root_dir` | str | ルートディレクトリパス | 必須 |
| `user` | str | 現在のユーザー名 | 必須 |
| `search_limit` | int | 検索結果の上限件数 | 100 |
| `file_extension` | str | 対象ファイル拡張子 | ".json" |

#### 初期化処理

1. **権限チェック**: `check_permissions()`を実行
2. **古い履歴削除**: `auto_delete_old_history()`で1年以上古いファイルを削除
3. **バックアップ作成**: `backup_files()`で履歴ファイルをバックアップ

## 権限管理

### 権限レベル

```python
# 検査担当者の権限リスト
self.authorized_users = ["検査担当者", "管理者", "admin", "inspector"]
```

### 権限チェックメソッド

#### `check_permissions() -> bool`
- **機能**: 基本権限チェック（全ユーザーがファイル閲覧可能）
- **戻り値**: 常にTrue

#### `check_admin_permissions() -> bool`
- **機能**: 管理者権限チェック（削除・履歴操作用）
- **例外**: `PermissionError` - 権限がない場合
- **戻り値**: True（権限がある場合）

```python
# 使用例
try:
    file_manager.check_admin_permissions()
    # 削除・履歴操作を実行
except PermissionError as e:
    print(f"権限エラー: {e}")
```

## フォルダ構造管理

### 設計書準拠のディレクトリ構造

```
ルートディレクトリ/
├── 2025-08-18/
│   ├── MODEL_A/
│   │   ├── 1234567-10/
│   │   │   ├── 1234567-10_001.json
│   │   │   ├── 1234567-10_002.json
│   │   │   └── history/
│   │   │       ├── 1234567-10_001_20250818T143000.json
│   │   │       └── backup/
│   │   │           └── 1234567-10_001_20250818T143000.json
│   │   └── 1234567-20/
│   └── MODEL_B/
└── operation_log.csv
```

### ディレクトリ管理メソッド

#### `get_lot_directory_path(date_str: str, model_name: str, lot_number: str) -> Path`
- **機能**: ロット用ディレクトリパスを生成
- **戻り値**: `日付/モデル名/ロット番号/` のPathオブジェクト

#### `create_lot_directory_structure(date_str: str, model_name: str, lot_number: str) -> Path`
- **機能**: ロット用ディレクトリ構造を作成
- **作成ディレクトリ**:
  - メインディレクトリ
  - historyディレクトリ  
  - backupディレクトリ
- **戻り値**: 作成されたロットディレクトリのPath

```python
# 使用例
lot_dir = file_manager.create_lot_directory_structure(
    "2025-08-18", "MODEL_A", "1234567-10"
)
print(f"作成されたディレクトリ: {lot_dir}")
```

### ロット番号検証

#### `validate_lot_number(lot_number: str) -> bool`
- **機能**: ロット番号の形式検証（7桁-2桁）
- **有効形式**: `1234567-10` または `1234567-20`
- **戻り値**: 形式が正しい場合True

```python
# 使用例
if file_manager.validate_lot_number("1234567-10"):
    print("有効なロット番号です")
else:
    print("無効なロット番号です")
```

## ファイル命名規則

### 設計書準拠のファイル名生成

#### `generate_sequential_filename(lot_number: str, sequence_number: int) -> str`
- **機能**: 設計書に従ったファイル名生成
- **形式**: `<ロット番号>_<識別番号>.json`
- **戻り値**: 生成されたファイル名

#### `get_next_sequence_number(date_str: str, model_name: str, lot_number: str) -> int`
- **機能**: 次の識別番号を取得（1から開始）
- **戻り値**: 次に使用する識別番号

```python
# 使用例
next_seq = file_manager.get_next_sequence_number(
    "2025-08-18", "MODEL_A", "1234567-10"
)
filename = file_manager.generate_sequential_filename("1234567-10", next_seq)
print(f"次のファイル名: {filename}")  # 例: 1234567-10_003.json
```

## ファイル操作

### 基本ファイル操作

#### `open_file(file_path: str) -> Dict[str, Any]`
- **機能**: JSONファイルを読み込み
- **ログ記録**: "open_file"アクションを記録
- **例外**: ファイル読み込みエラー時は`Exception`

#### `save_file(file_path: str, data: Dict[str, Any]) -> bool`
- **機能**: JSONファイルを保存
- **ディレクトリ作成**: 必要に応じて親ディレクトリを作成
- **ログ記録**: "save_file"アクションを記録
- **戻り値**: 保存成功時True

```python
# 使用例
data = {"coordinates": [], "model": "MODEL_A"}
success = file_manager.save_file("/path/to/file.json", data)
if success:
    print("保存完了")
```

## 履歴管理

### 削除禁止・履歴退避システム

#### `move_to_history(file_path: str, date_str: str = None, model_name: str = None, lot_number: str = None) -> bool`
- **機能**: ファイルを履歴フォルダに退避（削除の代わり）
- **権限**: 検査担当者のみ実行可能
- **ファイル名**: 元ファイル名_タイムスタンプ.json
- **整合性チェック**: 移動後のファイル内容を検証
- **ログ記録**: "move_to_history"アクションを記録

#### `restore_latest(original_path: str, date_str: str = None, model_name: str = None, lot_number: str = None) -> bool`
- **機能**: 最新履歴を復元
- **権限**: 検査担当者のみ実行可能
- **復元対象**: タイムスタンプが最新の履歴ファイル
- **ログ記録**: "restore_latest"アクションを記録

```python
# 履歴退避例
success = file_manager.move_to_history(
    "/path/to/file.json", "2025-08-18", "MODEL_A", "1234567-10"
)

# 復元例
success = file_manager.restore_latest(
    "/path/to/file.json", "2025-08-18", "MODEL_A", "1234567-10"
)
```

#### `get_history_files(date_str: str, model_name: str, lot_number: str) -> List[Dict[str, str]]`
- **機能**: 指定ロットの履歴ファイル一覧を取得
- **戻り値**: ファイル情報辞書のリスト（日時順ソート）

## 検索機能

### 部分一致検索

#### `search_files(query: str, date_str: str = None, model_name: str = None) -> List[Dict[str, str]]`
- **機能**: ファイル名部分一致検索
- **特徴**:
  - 大文字小文字区別なし
  - historyフォルダは除外
  - 作成日時順でソート
  - 上限件数制限あり

**検索範囲**:
- `date_str`と`model_name`指定: 該当モデルディレクトリ
- `date_str`のみ指定: 該当日付ディレクトリ
- 指定なし: 全ディレクトリ

**戻り値形式**:
```python
[
    {
        "file_path": "/path/to/file.json",
        "lot_number": "1234567-10",
        "sequence": "001",
        "created": "2025-08-18T14:30:00",
        "filename": "1234567-10_001.json"
    }
]
```

```python
# 検索例
results = file_manager.search_files("1234567", "2025-08-18", "MODEL_A")
for result in results:
    print(f"ファイル: {result['filename']}, 作成日時: {result['created']}")
```

## 操作ログ

### CSV形式ログ管理

#### `log_action(action: str, file_path: str) -> None`
- **機能**: 操作ログをCSV形式で記録
- **ファイル**: `operation_log.csv`
- **形式**: timestamp,user,action,file_path

#### `get_operation_logs(start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, str]]`
- **機能**: 操作ログを取得
- **フィルタ**: 開始日時・終了日時での絞り込み可能
- **戻り値**: ログエントリの辞書リスト

```python
# ログ取得例
from datetime import datetime, timedelta

# 過去7日間のログを取得
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
logs = file_manager.get_operation_logs(start_date, end_date)

for log in logs:
    print(f"{log['timestamp']}: {log['user']} - {log['action']} - {log['file_path']}")
```

## ファイルロック

### 同時アクセス制御

#### `lock_file(file_path: str) -> bool`
- **機能**: ファイルをロック
- **戻り値**: ロック成功時True、既にロック済みの場合False
- **ログ記録**: "lock_file"アクションを記録

#### `unlock_file(file_path: str) -> None`
- **機能**: ファイルロックを解除
- **ログ記録**: "unlock_file"アクションを記録

#### `is_file_locked(file_path: str) -> bool`
- **機能**: ファイルがロックされているかチェック
- **戻り値**: ロック中の場合True

```python
# ファイルロック例
if file_manager.lock_file("/path/to/file.json"):
    try:
        # ファイル操作を実行
        data = file_manager.open_file("/path/to/file.json")
        # データ処理...
    finally:
        file_manager.unlock_file("/path/to/file.json")
else:
    print("ファイルは他のプロセスで使用中です")
```

## バックアップ・自動削除

### 自動メンテナンス

#### `backup_files() -> None`
- **機能**: 履歴フォルダ内のJSONファイルをバックアップ
- **バックアップ先**: `history/backup/`ディレクトリ
- **実行タイミング**: アプリ起動時

#### `auto_delete_old_history() -> None`
- **機能**: 1年以上古い履歴・バックアップファイルを自動削除
- **対象**: 履歴ディレクトリとバックアップディレクトリ
- **ログ記録**: 削除されたファイルは"auto_delete_old"として記録

## ユーティリティメソッド

### 便利機能

#### `get_lot_files(date_str: str, model_name: str, lot_number: str, include_history: bool = False) -> List[Dict[str, str]]`
- **機能**: 指定ロットの全ファイルを取得
- **include_history**: 履歴ファイルも含める場合True
- **戻り値**: ファイル情報辞書のリスト（"type"フィールドで"current"/"history"を区別）

#### `cleanup_locks() -> None`
- **機能**: すべてのファイルロックを解除
- **用途**: アプリケーション終了時

#### `get_statistics() -> Dict[str, int]`
- **機能**: ファイル管理統計情報を取得
- **戻り値**: 
  ```python
  {
      "total_files": 150,      # 総ファイル数
      "history_files": 45,     # 履歴ファイル数
      "backup_files": 45,      # バックアップファイル数
      "locked_files": 2        # ロック中ファイル数
  }
  ```

#### `check_file_integrity(src: str, dest: str) -> bool`
- **機能**: ファイル内容の整合性をチェック
- **比較方法**: バイナリレベルでの完全一致
- **戻り値**: 内容が一致する場合True

## エラーハンドリング

### 例外処理

| 例外クラス | 発生条件 | 対処方法 |
|----------|----------|---------|
| `PermissionError` | 権限不足時 | 検査担当者権限の確認 |
| `FileNotFoundError` | ファイルが存在しない | ファイルパスの確認 |
| `Exception` | その他のエラー | ログ記録・エラーメッセージ表示 |

### エラーログ

全ての例外は適切にキャッチされ、エラー内容がコンソールに出力されます。

```python
try:
    file_manager.move_to_history("/path/to/file.json")
except PermissionError as e:
    print(f"権限エラー: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## 使用例

### 基本的な使用フロー

```python
from pathlib import Path
from src.utils.file_manager_class import FileManager

# FileManagerの初期化
file_manager = FileManager(
    root_dir="/data/production",
    user="検査担当者",
    search_limit=100
)

# ディレクトリ構造の作成
lot_dir = file_manager.create_lot_directory_structure(
    "2025-08-18", "MODEL_A", "1234567-10"
)

# ファイル名の生成
next_seq = file_manager.get_next_sequence_number(
    "2025-08-18", "MODEL_A", "1234567-10"
)
filename = file_manager.generate_sequential_filename("1234567-10", next_seq)

# ファイルの保存
data = {
    "model": "MODEL_A",
    "coordinates": [(100, 200), (150, 250)],
    "lot_number": "1234567-10"
}
file_path = lot_dir / filename
file_manager.save_file(str(file_path), data)

# ファイルの検索
results = file_manager.search_files("1234567")
print(f"検索結果: {len(results)}件")

# 履歴管理（検査担当者のみ）
try:
    file_manager.check_admin_permissions()
    file_manager.move_to_history(str(file_path), "2025-08-18", "MODEL_A", "1234567-10")
    file_manager.restore_latest(str(file_path), "2025-08-18", "MODEL_A", "1234567-10")
except PermissionError:
    print("管理者権限が必要です")

# 統計情報の取得
stats = file_manager.get_statistics()
print(f"管理中ファイル数: {stats['total_files']}")

# クリーンアップ
file_manager.cleanup_locks()
```

### 権限チェック付きの安全な操作

```python
def safe_file_operation(file_manager, operation, *args, **kwargs):
    """権限チェック付きの安全なファイル操作"""
    try:
        if operation in ['move_to_history', 'restore_latest']:
            file_manager.check_admin_permissions()
        
        method = getattr(file_manager, operation)
        return method(*args, **kwargs)
        
    except PermissionError as e:
        print(f"権限エラー: {e}")
        return False
    except Exception as e:
        print(f"操作エラー: {e}")
        return False

# 使用例
success = safe_file_operation(
    file_manager, 'move_to_history',
    "/path/to/file.json", "2025-08-18", "MODEL_A", "1234567-10"
)
```

## 設定とカスタマイズ

### 設定可能な項目

- **search_limit**: 検索結果の上限件数
- **file_extension**: 対象ファイルの拡張子
- **authorized_users**: 管理者権限を持つユーザーリスト
- **lot_pattern**: ロット番号の検証パターン

### カスタマイズ例

```python
# カスタム設定でFileManagerを初期化
custom_file_manager = FileManager(
    root_dir="/custom/data/path",
    user="カスタムユーザー",
    search_limit=200,  # 検索結果上限を200件に
    file_extension=".json"
)

# 管理者権限ユーザーを追加
custom_file_manager.authorized_users.append("新規管理者")
```

---

## 注意事項

1. **権限管理**: 削除・履歴操作は検査担当者のみ実行可能
2. **ファイル命名**: 設計書の命名規則に厳密に従う必要がある
3. **ロット番号形式**: 7桁-2桁の形式以外は受け付けない
4. **バックアップ**: 1年以上古いファイルは自動削除される
5. **同時アクセス**: ファイルロック機能を活用して排他制御を行う

---

**最終更新**: 2025年8月18日  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot
