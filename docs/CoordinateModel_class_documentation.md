# CoordinateModel クラス ドキュメント

## 概要

`CoordinateModel`クラスは、座標データとその詳細情報を管理するモデルクラスです。座標の追加、削除、更新、およびアンドゥ/リドゥ機能を提供します。

## クラス定義

```python
class CoordinateModel:
    """座標データを管理するモデル"""
```

## 初期化

### `__init__()`

CoordinateModelインスタンスを初期化します。

```python
coordinate_model = CoordinateModel()
```

#### 初期化される属性

| 属性名 | 型 | 初期値 | 説明 |
|-------|---|-------|-----|
| `_coordinates` | `List[Tuple[int, int]]` | `[]` | 座標リスト |
| `_coordinate_details` | `List[Dict[str, Any]]` | `[]` | 座標詳細情報リスト |
| `_current_index` | `int` | `-1` | 現在選択中の座標インデックス |
| `_image_path` | `str` | `""` | 画像パス |
| `_undo_stack` | `List[List[Tuple[int, int]]]` | `[]` | アンドゥ用スタック |
| `_redo_stack` | `List[List[Tuple[int, int]]]` | `[]` | リドゥ用スタック |

## プロパティ

### `coordinates` → `List[Tuple[int, int]]`

座標リストを取得します（読み取り専用）。

```python
coords = coordinate_model.coordinates
print(f"座標数: {len(coords)}")
```

### `coordinate_details` → `List[Dict[str, Any]]`

座標詳細リストを取得します（読み取り専用）。

```python
details = coordinate_model.coordinate_details
```

### `current_index` → `int`

現在選択中の座標インデックスを取得します。

```python
index = coordinate_model.current_index
if index >= 0:
    print(f"選択中の座標: {index + 1}")
```

### `image_path` → `str`

画像パスを取得します。

```python
path = coordinate_model.image_path
```

## メソッド一覧

### 座標管理

#### `add_coordinate(x: int, y: int) -> int`

新しい座標を追加します。

- **パラメータ**:
  - `x`: X座標
  - `y`: Y座標
- **戻り値**: 追加された座標のインデックス

```python
# 使用例
index = coordinate_model.add_coordinate(100, 200)
print(f"座標 ({100}, {200}) をインデックス {index} に追加しました")
```

#### `remove_coordinate(index: int) -> bool`

指定されたインデックスの座標を削除します。

- **パラメータ**: `index` - 削除する座標のインデックス
- **戻り値**: 削除成功時は`True`、失敗時は`False`

```python
# 使用例
success = coordinate_model.remove_coordinate(0)
if success:
    print("座標を削除しました")
```

#### `update_coordinate(index: int, x: int, y: int) -> bool`

指定されたインデックスの座標を更新します。

- **パラメータ**:
  - `index`: 更新する座標のインデックス
  - `x`: 新しいX座標
  - `y`: 新しいY座標
- **戻り値**: 更新成功時は`True`、失敗時は`False`

```python
# 使用例
success = coordinate_model.update_coordinate(0, 150, 250)
if success:
    print("座標を更新しました")
```

#### `clear_coordinates()`

全座標をクリアします。

```python
# 使用例
coordinate_model.clear_coordinates()
print("全座標をクリアしました")
```

### 詳細情報管理

#### `set_coordinate_detail(index: int, detail: Dict[str, Any]) -> bool`

座標の詳細情報を設定します。

- **パラメータ**:
  - `index`: 座標のインデックス
  - `detail`: 詳細情報の辞書
- **戻り値**: 設定成功時は`True`、失敗時は`False`

```python
# 使用例
detail = {
    "reference": "R1",
    "defect": "はんだ不良",
    "comment": "再作業要"
}
success = coordinate_model.set_coordinate_detail(0, detail)
```

#### `get_coordinate_detail(index: int) -> Optional[Dict[str, Any]]`

座標の詳細情報を取得します。

- **パラメータ**: `index` - 座標のインデックス
- **戻り値**: 詳細情報の辞書、または`None`

```python
# 使用例
detail = coordinate_model.get_coordinate_detail(0)
if detail:
    print(f"リファレンス: {detail.get('reference', 'なし')}")
```

### 現在の座標管理

#### `set_current_coordinate(index: int) -> bool`

現在の座標を設定します。

- **パラメータ**: `index` - 設定する座標のインデックス（-1で選択解除）
- **戻り値**: 設定成功時は`True`、失敗時は`False`

```python
# 使用例
success = coordinate_model.set_current_coordinate(0)
if success:
    print("最初の座標を選択しました")

# 選択を解除
coordinate_model.set_current_coordinate(-1)
```

#### `get_current_coordinate() -> Optional[Tuple[int, int]]`

現在選択中の座標を取得します。

- **戻り値**: 座標のタプル、または`None`

```python
# 使用例
current_coord = coordinate_model.get_current_coordinate()
if current_coord:
    x, y = current_coord
    print(f"現在の座標: ({x}, {y})")
```

#### `get_current_coordinate_detail() -> Optional[Dict[str, Any]]`

現在選択中の座標の詳細情報を取得します。

- **戻り値**: 詳細情報の辞書、または`None`

```python
# 使用例
detail = coordinate_model.get_current_coordinate_detail()
if detail:
    print(f"現在の座標の詳細: {detail}")
```

### 一括操作

#### `set_coordinates_with_details(coordinates: List[Tuple[int, int]], details: List[Dict[str, Any]])`

座標と詳細情報を一括設定します。

- **パラメータ**:
  - `coordinates`: 座標のリスト
  - `details`: 詳細情報のリスト

```python
# 使用例
coords = [(100, 200), (300, 400)]
details = [
    {"reference": "R1", "defect": "はんだ不良"},
    {"reference": "C1", "defect": "部品欠け"}
]
coordinate_model.set_coordinates_with_details(coords, details)
```

### 画像管理

#### `set_image_path(path: str)`

画像パスを設定します。

- **パラメータ**: `path` - 画像ファイルのパス

```python
# 使用例
coordinate_model.set_image_path("/path/to/image.jpg")
```

### アンドゥ/リドゥ機能

#### `undo() -> bool`

最後の操作を元に戻します。

- **戻り値**: アンドゥ成功時は`True`、失敗時は`False`

```python
# 使用例
if coordinate_model.undo():
    print("操作を元に戻しました")
else:
    print("元に戻す操作がありません")
```

#### `redo() -> bool`

アンドゥした操作をやり直します。

- **戻り値**: リドゥ成功時は`True`、失敗時は`False`

```python
# 使用例
if coordinate_model.redo():
    print("操作をやり直しました")
else:
    print("やり直す操作がありません")
```

#### `can_undo() -> bool`

アンドゥ可能かどうかを確認します。

- **戻り値**: アンドゥ可能時は`True`

```python
# 使用例
if coordinate_model.can_undo():
    print("アンドゥが可能です")
```

#### `can_redo() -> bool`

リドゥ可能かどうかを確認します。

- **戻り値**: リドゥ可能時は`True`

```python
# 使用例
if coordinate_model.can_redo():
    print("リドゥが可能です")
```

### 概要情報

#### `get_coordinate_summary() -> Dict[str, Any]`

座標の概要情報を取得します。

- **戻り値**: 概要情報を含む辞書

```python
# 使用例
summary = coordinate_model.get_coordinate_summary()
print(f"座標数: {summary['total_count']}")
print(f"現在のインデックス: {summary['current_index']}")
print(f"画像パス: {summary['image_path']}")
```

## 使用例

### 基本的な使用方法

```python
from src.models.coordinate_model import CoordinateModel

# CoordinateModelインスタンスを作成
coord_model = CoordinateModel()

# 画像パスを設定
coord_model.set_image_path("/path/to/image.jpg")

# 座標を追加
index1 = coord_model.add_coordinate(100, 200)
index2 = coord_model.add_coordinate(300, 400)

# 詳細情報を設定
detail1 = {
    "reference": "R1",
    "defect": "はんだ不良",
    "comment": "再作業要"
}
coord_model.set_coordinate_detail(index1, detail1)

# 現在の座標を設定
coord_model.set_current_coordinate(index1)

# 現在の座標を取得
current_coord = coord_model.get_current_coordinate()
if current_coord:
    print(f"現在の座標: {current_coord}")

# 概要情報を表示
summary = coord_model.get_coordinate_summary()
print(f"総座標数: {summary['total_count']}")
```

### アンドゥ/リドゥの使用例

```python
# 座標を追加
coord_model.add_coordinate(100, 200)
coord_model.add_coordinate(300, 400)

# 操作を元に戻す
if coord_model.can_undo():
    coord_model.undo()
    print("最後の座標追加を元に戻しました")

# 操作をやり直す
if coord_model.can_redo():
    coord_model.redo()
    print("座標追加をやり直しました")
```

### エラーハンドリング付きの使用例

```python
try:
    # 座標を追加
    index = coord_model.add_coordinate(100, 200)
    
    # 詳細情報を設定
    detail = {"reference": "R1"}
    if coord_model.set_coordinate_detail(index, detail):
        print("詳細情報を設定しました")
    else:
        print("詳細情報の設定に失敗しました")
    
    # 座標を更新
    if coord_model.update_coordinate(index, 150, 250):
        print("座標を更新しました")
    else:
        print("座標の更新に失敗しました")
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
```

## 特徴

### データ管理

- **座標と詳細情報の同期管理**: 座標と対応する詳細情報を自動的に同期
- **インデックス管理**: 座標の追加・削除時に自動的にインデックスを調整
- **データ整合性**: 座標数と詳細情報数を常に一致させる

### アンドゥ/リドゥ機能

- **操作履歴管理**: 最大50件の操作履歴を保持
- **メモリ効率**: スタックサイズを制限してメモリ使用量を制御
- **状態復元**: 座標データと詳細情報を正確に復元

### 安全性

- **インデックス範囲チェック**: 不正なインデックスアクセスを防止
- **データコピー**: プロパティ経由でのデータアクセス時にコピーを返す
- **型安全性**: 型ヒントによる型チェックサポート

## 注意事項

1. **インデックス管理**: インデックスは0ベースで管理されます
2. **アンドゥスタック**: 最大50件の操作履歴が保持されます
3. **詳細情報**: 座標数と詳細情報数は自動的に同期されます
4. **現在のインデックス**: -1は「選択なし」を表します
5. **データコピー**: プロパティから取得されるデータは元データのコピーです

## 依存関係

- `typing`: 型ヒント用のモジュール
  - `List`: リスト型
  - `Dict`: 辞書型
  - `Any`: 任意の型
  - `Optional`: オプショナル型
  - `Tuple`: タプル型
