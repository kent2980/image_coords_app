# FileManager クラス ドキュメント

## 概要

`FileManager`クラスは、指定されたルートディレクトリ内のファイルを管理し、様々な操作を提供するユーティリティクラスです。ファイル操作の効率化と安全性を向上させることを目的としています。

## クラス定義

```python
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
    """
```

## 初期化

### `__init__(root_dir, user, search_limit=100, file_extension=".json")`

FileManagerインスタンスを初期化します。

#### パラメータ

| パラメータ | 型 | デフォルト値 | 説明 |
|-----------|---|-------------|-----|
| `root_dir` | `str` | - | ルートディレクトリのパス |
| `user` | `str` | - | 操作ユーザー名 |
| `search_limit` | `int` | `100` | 検索結果の上限件数 |
| `file_extension` | `str` | `".json"` | 対象ファイル拡張子 |

#### 処理内容

初期化時に以下の処理が自動実行されます：

1. ディレクトリ構造の設定
2. 権限チェック
3. 古い履歴の自動削除
4. ファイルのバックアップ作成

## メソッド一覧

### 権限管理

#### `check_permissions() -> bool`

操作権限があるかを確認します。

- **戻り値**: `bool` - 権限がある場合は`True`
- **例外**: `PermissionError` - 権限がない場合

```python
# 使用例
try:
    file_manager.check_permissions()
    print("権限があります")
except PermissionError as e:
    print(f"権限エラー: {e}")
```

### ファイル検索

#### `search_files(query: str) -> list[str]`

指定されたクエリでファイルを検索します（部分一致）。

- **パラメータ**: `query` - 検索クエリ文字列
- **戻り値**: `list[str]` - マッチしたファイルパスのリスト

```python
# 使用例
results = file_manager.search_files("test")
for file_path in results:
    print(f"見つかったファイル: {file_path}")
```

### ファイル操作

#### `open_file(file_path: str) -> dict`

JSONファイルを開いて内容を返します。

- **パラメータ**: `file_path` - ファイルパス
- **戻り値**: `dict` - JSONファイルの内容

```python
# 使用例
data = file_manager.open_file("/path/to/file.json")
print(data)
```

#### `move_to_history(file_path: str) -> None`

ファイルを履歴フォルダに移動します。

- **パラメータ**: `file_path` - 移動するファイルパス
- **処理内容**:
  - ファイル名にタイムスタンプを付加
  - 履歴フォルダに移動
  - 整合性チェック実行
  - 操作ログ記録

```python
# 使用例
file_manager.move_to_history("/path/to/file.json")
```

#### `restore_latest(original_path: str) -> None`

最新の履歴ファイルを復元します。

- **パラメータ**: `original_path` - 復元先のパス
- **処理内容**:
  - 対応する履歴ファイルを検索
  - 最新のファイルを特定
  - 元の場所に復元
  - 操作ログ記録

```python
# 使用例
file_manager.restore_latest("/path/to/file.json")
```

### バックアップ管理

#### `backup_files() -> None`

履歴フォルダ内の全JSONファイルをバックアップします。

```python
# 使用例
file_manager.backup_files()
```

#### `auto_delete_old_history() -> None`

1年以上古い履歴とバックアップファイルを自動削除します。

```python
# 使用例
file_manager.auto_delete_old_history()
```

### ログ管理

#### `log_action(action: str, file_path: str) -> None`

操作ログをCSVファイルに記録します。

- **パラメータ**:
  - `action` - 実行されたアクション名
  - `file_path` - 対象ファイルパス

#### ログ形式

| フィールド | 説明 |
|-----------|-----|
| `timestamp` | タイムスタンプ（ISO形式） |
| `user` | 操作ユーザー |
| `action` | 実行されたアクション |
| `file_path` | 対象ファイルパス |

```python
# 使用例
file_manager.log_action("file_opened", "/path/to/file.json")
```

### ファイルロック

#### `lock_file(file_path: str) -> None`

指定されたファイルをロック状態にします。

```python
# 使用例
file_manager.lock_file("/path/to/file.json")
```

#### `unlock_file(file_path: str) -> None`

指定されたファイルのロックを解除します。

```python
# 使用例
file_manager.unlock_file("/path/to/file.json")
```

### 整合性チェック

#### `check_file_integrity(src: str, dest: str) -> bool`

2つのファイルの内容が一致するかを確認します。

- **パラメータ**:
  - `src` - 元ファイルパス
  - `dest` - 比較先ファイルパス
- **戻り値**: `bool` - ファイル内容が一致する場合は`True`

```python
# 使用例
is_identical = file_manager.check_file_integrity("file1.json", "file2.json")
if is_identical:
    print("ファイルは同一です")
```

## ディレクトリ構造

FileManagerが管理するディレクトリ構造：

root_dir/
├── operation_log.csv          # 操作ログファイル
├── history/                   # 履歴フォルダ
│   ├── file1_20250816T123456.json
│   ├── file2_20250816T123457.json
│   └── backup/                # バックアップフォルダ
│       ├── file1_20250815T123456.json
│       └── file2_20250815T123456.json
└── [その他のファイル]

## 使用例

### 基本的な使用方法

```python
from src.utils.file_manager_class import FileManager

# FileManagerインスタンスを作成
file_manager = FileManager(
    root_dir="/path/to/workspace",
    user="検査担当者",
    search_limit=50,
    file_extension=".json"
)

# ファイル検索
results = file_manager.search_files("coordinates")
print(f"検索結果: {len(results)}件")

# JSONファイルを開く
if results:
    data = file_manager.open_file(results[0])
    print(f"ファイル内容: {data}")

# ファイルを履歴に移動
file_manager.move_to_history(results[0])

# 最新履歴を復元
file_manager.restore_latest(results[0])
```

### エラーハンドリング付きの使用例

```python
try:
    # FileManagerインスタンスを作成
    file_manager = FileManager("/workspace", "検査担当者")
    
    # ファイル操作
    file_path = "/workspace/data.json"
    
    # ファイルロック
    file_manager.lock_file(file_path)
    
    # ファイル処理
    data = file_manager.open_file(file_path)
    # ... データ処理 ...
    
    # ファイルロック解除
    file_manager.unlock_file(file_path)
    
except PermissionError as e:
    print(f"権限エラー: {e}")
except FileNotFoundError as e:
    print(f"ファイルが見つかりません: {e}")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## 特徴

### セキュリティ

- ユーザー権限チェック機能
- ファイルロック機能による排他制御
- 操作ログによる監査証跡

### 信頼性

- ファイルの整合性チェック
- 自動バックアップ機能
- 履歴管理による復元機能

### パフォーマンス

- 検索結果の上限制御
- 古いファイルの自動削除
- 効率的なファイル検索

### 保守性

- 詳細な操作ログ
- 設定可能なパラメータ
- 明確なエラーハンドリング

## 注意事項

1. **権限管理**: 「検査担当者」のみが操作可能です
2. **ファイル形式**: デフォルトではJSONファイルのみを対象とします
3. **自動削除**: 1年以上古いファイルは自動的に削除されます
4. **バックアップ**: 初期化時に自動でバックアップが作成されます
5. **ログファイル**: 操作ログはCSV形式で記録されます

## 依存関係

- `csv`: ログファイル操作
- `json`: JSONファイル操作
- `os`: ファイルシステム操作
- `shutil`: ファイル移動・コピー
- `datetime`: タイムスタンプ生成
