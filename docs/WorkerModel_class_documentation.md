# WorkerModel クラス ドキュメント

## 概要

`WorkerModel`クラスは、作業者情報の管理を行うモデルクラスです。CSVファイルを使用して作業者データの永続化を行い、作業者の追加・更新・削除・検証機能を提供します。

## クラス定義

```python
class WorkerModel:
    """作業者データを管理するモデル"""
```

## 初期化

### `__init__()`

WorkerModelインスタンスを初期化します。

```python
worker_model = WorkerModel()
```

#### 初期化される属性

| 属性名 | 型 | 初期値 | 説明 |
|-------|---|-------|-----|
| `_worker_file` | `str` | `"worker.csv"` | 作業者データファイル名 |
| `_current_worker_no` | `str` | `""` | 現在の作業者番号 |
| `_workers` | `Dict[str, str]` | `{}` | 作業者データ（番号: 名前） |

## プロパティ

### `current_worker_no` → `str`

現在の作業者番号を取得・設定します。

```python
# 取得
worker_no = worker_model.current_worker_no

# 設定
worker_model.current_worker_no = "W001"
```

### `current_worker_name` → `str`

現在の作業者名を取得します（読み取り専用）。

```python
worker_name = worker_model.current_worker_name
print(f"現在の作業者: {worker_name}")
```

## メソッド一覧

### 作業者検索

#### `get_worker_name(worker_no: str) -> Optional[str]`

作業者番号から名前を取得します。

- **パラメータ**: `worker_no` - 作業者番号
- **戻り値**: 作業者名、または`None`

```python
# 使用例
worker_name = worker_model.get_worker_name("W001")
if worker_name:
    print(f"作業者名: {worker_name}")
else:
    print("作業者が見つかりません")
```

#### `worker_exists(worker_no: str) -> bool`

作業者が存在するかチェックします。

- **パラメータ**: `worker_no` - 作業者番号
- **戻り値**: 存在する場合は`True`

```python
# 使用例
if worker_model.worker_exists("W001"):
    print("作業者が存在します")
```

### 作業者管理

#### `add_worker(worker_no: str, worker_name: str) -> bool`

新しい作業者を追加します。

- **パラメータ**:
  - `worker_no`: 作業者番号
  - `worker_name`: 作業者名
- **戻り値**: 追加成功時は`True`

```python
# 使用例
success = worker_model.add_worker("W002", "田中太郎")
if success:
    print("作業者を追加しました")
else:
    print("作業者の追加に失敗しました")
```

#### `update_worker(worker_no: str, worker_name: str) -> bool`

既存の作業者情報を更新します。

- **パラメータ**:
  - `worker_no`: 作業者番号
  - `worker_name`: 新しい作業者名
- **戻り値**: 更新成功時は`True`

```python
# 使用例
success = worker_model.update_worker("W001", "山田花子")
if success:
    print("作業者情報を更新しました")
```

#### `remove_worker(worker_no: str) -> bool`

作業者を削除します。

- **パラメータ**: `worker_no` - 削除する作業者番号
- **戻り値**: 削除成功時は`True`

```python
# 使用例
success = worker_model.remove_worker("W001")
if success:
    print("作業者を削除しました")
```

### データ取得

#### `get_all_workers() -> Dict[str, str]`

全作業者データを取得します。

- **戻り値**: 作業者データの辞書（番号: 名前）

```python
# 使用例
all_workers = worker_model.get_all_workers()
for worker_no, worker_name in all_workers.items():
    print(f"{worker_no}: {worker_name}")
```

#### `get_worker_numbers() -> List[str]`

作業者番号のリストを取得します。

- **戻り値**: 作業者番号のリスト

```python
# 使用例
worker_numbers = worker_model.get_worker_numbers()
print(f"登録済み作業者番号: {worker_numbers}")
```

#### `get_worker_names() -> List[str]`

作業者名のリストを取得します。

- **戻り値**: 作業者名のリスト

```python
# 使用例
worker_names = worker_model.get_worker_names()
print(f"登録済み作業者名: {worker_names}")
```

### 入力検証

#### `validate_worker_input(worker_input: str) -> Dict[str, any]`

作業者入力を検証します。

- **パラメータ**: `worker_input` - 入力された作業者情報
- **戻り値**: 検証結果を含む辞書

#### 戻り値の構造

| キー | 型 | 説明 |
|-----|---|-----|
| `valid` | `bool` | 入力が有効かどうか |
| `worker_no` | `str` | 作業者番号 |
| `worker_name` | `str` | 作業者名 |
| `is_new` | `bool` | 新規作業者かどうか |
| `message` | `str` | 検証結果メッセージ |

```python
# 使用例
result = worker_model.validate_worker_input("W001")
if result['valid']:
    if result['is_new']:
        print(f"新規作業者: {result['worker_name']}")
    else:
        print(f"既存作業者: {result['worker_name']}")
else:
    print(f"エラー: {result['message']}")
```

## プライベートメソッド

### `_load_workers()`

CSVファイルから作業者データを読み込みます。

- **ファイル形式**: CSV（作業者番号, 作業者名）
- **エンコーディング**: UTF-8

### `_save_workers() -> bool`

作業者データをCSVファイルに保存します。

- **戻り値**: 保存成功時は`True`

## 使用例

### 基本的な使用方法

```python
from src.models.worker_model import WorkerModel

# WorkerModelインスタンスを作成
worker_model = WorkerModel()

# 作業者を追加
worker_model.add_worker("W001", "山田太郎")
worker_model.add_worker("W002", "田中花子")

# 作業者を検索
worker_name = worker_model.get_worker_name("W001")
print(f"作業者: {worker_name}")

# 現在の作業者を設定
worker_model.current_worker_no = "W001"
print(f"現在の作業者: {worker_model.current_worker_name}")

# 全作業者を表示
all_workers = worker_model.get_all_workers()
for worker_no, worker_name in all_workers.items():
    print(f"{worker_no}: {worker_name}")
```

### 入力検証の使用例

```python
# ユーザー入力の検証
user_input = "W003"
result = worker_model.validate_worker_input(user_input)

if result['valid']:
    if result['is_new']:
        # 新規作業者の場合
        print(f"新規作業者として登録します: {result['worker_name']}")
        worker_model.add_worker(result['worker_no'], result['worker_name'])
    else:
        # 既存作業者の場合
        print(f"既存作業者です: {result['worker_name']}")
    
    # 現在の作業者として設定
    worker_model.current_worker_no = result['worker_no']
else:
    print(f"入力エラー: {result['message']}")
```

### CRUD操作の例

```python
# Create（作成）
worker_model.add_worker("W004", "佐藤次郎")

# Read（読み取り）
worker_name = worker_model.get_worker_name("W004")
worker_exists = worker_model.worker_exists("W004")

# Update（更新）
worker_model.update_worker("W004", "佐藤二郎")

# Delete（削除）
worker_model.remove_worker("W004")
```

### エラーハンドリング付きの使用例

```python
try:
    # 作業者の追加
    if worker_model.add_worker("W005", "鈴木一郎"):
        print("作業者を追加しました")
    else:
        print("作業者の追加に失敗しました")
    
    # 作業者の検索
    worker_name = worker_model.get_worker_name("W005")
    if worker_name:
        print(f"作業者が見つかりました: {worker_name}")
    else:
        print("作業者が見つかりません")
    
    # 入力検証
    validation_result = worker_model.validate_worker_input("")
    if not validation_result['valid']:
        print(f"入力エラー: {validation_result['message']}")
        
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## ファイル形式

### worker.csv

```csv
W001,山田太郎
W002,田中花子
W003,佐藤次郎
```

- **列1**: 作業者番号
- **列2**: 作業者名
- **エンコーディング**: UTF-8
- **改行コード**: システム依存

## 特徴

### データ永続化

- **CSV形式**: 人間が読みやすいCSV形式でデータを保存
- **UTF-8エンコーディング**: 日本語文字を正しく処理
- **自動読み込み**: 初期化時に既存データを自動読み込み

### 柔軟な検証

- **既存作業者チェック**: 登録済み作業者の自動識別
- **新規作業者対応**: 未登録の場合は新規作業者として処理
- **入力検証**: 空文字などの無効な入力をチェック

### CRUD操作

- **Create**: 新規作業者の追加
- **Read**: 作業者情報の検索・取得
- **Update**: 既存作業者情報の更新
- **Delete**: 作業者の削除

### 状態管理

- **現在の作業者**: 現在選択中の作業者を管理
- **プロパティアクセス**: 現在の作業者情報への簡単なアクセス

## 注意事項

1. **ファイルアクセス**: CSVファイルの読み書き権限が必要です
2. **文字エンコーディング**: UTF-8形式で保存されます
3. **データ整合性**: ファイル操作時のエラーハンドリングを実装
4. **一意性**: 作業者番号の重複は上書きされます
5. **空文字チェック**: 空の作業者番号・名前は受け付けません

## 依存関係

- **標準ライブラリ**:
  - `os`: ファイル存在チェック
  - `csv`: CSVファイル操作
  - `typing`: 型ヒント
    - `Dict`: 辞書型
    - `List`: リスト型
    - `Optional`: オプショナル型
