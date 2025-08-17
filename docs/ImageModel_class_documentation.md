# ImageModel クラス ドキュメント

## 概要

`ImageModel`クラスは、画像データとリサイズロジックを管理するモデルクラスです。PIL（Python Imaging Library）を使用して画像の読み込み、リサイズ、座標変換を行います。

## クラス定義

```python
class ImageModel:
    """画像データを管理するモデル"""
```

## 初期化

### `__init__()`

ImageModelインスタンスを初期化します。

```python
image_model = ImageModel()
```

#### 初期化される属性

| 属性名 | 型 | 初期値 | 説明 |
|-------|---|-------|-----|
| `_current_image_path` | `str` | `""` | 現在の画像パス |
| `_original_size` | `Tuple[int, int]` | `(0, 0)` | 元画像のサイズ |
| `_display_size` | `Tuple[int, int]` | `(0, 0)` | 表示サイズ |
| `_scale_factor` | `float` | `1.0` | スケールファクター |
| `_tk_image` | `Optional[ImageTk.PhotoImage]` | `None` | Tkinter画像オブジェクト |
| `_image_files` | `List[Dict[str, str]]` | `[]` | 画像ファイルリスト |
| `_supported_extensions` | `Set[str]` | `{'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}` | サポートする画像形式 |

## プロパティ

### `current_image_path` → `str`

現在の画像パスを取得します。

```python
path = image_model.current_image_path
```

### `original_size` → `Tuple[int, int]`

元画像のサイズを取得します。

```python
width, height = image_model.original_size
```

### `display_size` → `Tuple[int, int]`

表示サイズを取得します。

```python
display_width, display_height = image_model.display_size
```

### `scale_factor` → `float`

スケールファクターを取得します。

```python
factor = image_model.scale_factor
```

### `tk_image` → `Optional[ImageTk.PhotoImage]`

Tkinter画像オブジェクトを取得します。

```python
tk_img = image_model.tk_image
```

## メソッド一覧

### 画像読み込み

#### `load_image(image_path: str, canvas_width: int = 800, canvas_height: int = 600) -> Optional[ImageTk.PhotoImage]`

画像を読み込み、指定サイズにリサイズします。

- **パラメータ**:
  - `image_path`: 画像ファイルのパス
  - `canvas_width`: キャンバス幅（デフォルト: 800）
  - `canvas_height`: キャンバス高さ（デフォルト: 600）
- **戻り値**: Tkinter用画像オブジェクト、または`None`

```python
# 使用例
tk_image = image_model.load_image("/path/to/image.jpg", 1024, 768)
if tk_image:
    print(f"画像を読み込みました: {image_model.original_size}")
```

#### `reload_image_for_canvas_size(canvas_width: int, canvas_height: int) -> Optional[ImageTk.PhotoImage]`

現在の画像を新しいキャンバスサイズに合わせて再読み込みします。

- **パラメータ**:
  - `canvas_width`: 新しいキャンバス幅
  - `canvas_height`: 新しいキャンバス高さ
- **戻り値**: Tkinter用画像オブジェクト、または`None`

```python
# 使用例
# ウィンドウサイズ変更時
new_tk_image = image_model.reload_image_for_canvas_size(1200, 900)
if new_tk_image:
    print("画像をリサイズしました")
```

### 座標変換

#### `convert_display_to_original_coords(display_x: int, display_y: int) -> Tuple[int, int]`

表示座標を元画像の座標に変換します。

- **パラメータ**:
  - `display_x`: 表示X座標
  - `display_y`: 表示Y座標
- **戻り値**: 元画像の座標タプル

```python
# 使用例
# マウスクリック座標を元画像座標に変換
orig_x, orig_y = image_model.convert_display_to_original_coords(200, 150)
print(f"元画像座標: ({orig_x}, {orig_y})")
```

#### `convert_original_to_display_coords(orig_x: int, orig_y: int) -> Tuple[int, int]`

元画像の座標を表示座標に変換します。

- **パラメータ**:
  - `orig_x`: 元画像X座標
  - `orig_y`: 元画像Y座標
- **戻り値**: 表示座標タプル

```python
# 使用例
# 保存された座標を表示座標に変換
display_x, display_y = image_model.convert_original_to_display_coords(100, 75)
print(f"表示座標: ({display_x}, {display_y})")
```

### ディレクトリ管理

#### `load_image_files_from_directory(directory: str) -> List[Dict[str, str]]`

ディレクトリから画像ファイル一覧を読み込みます。

- **パラメータ**: `directory` - 検索するディレクトリパス
- **戻り値**: 画像ファイル情報のリスト

```python
# 使用例
image_files = image_model.load_image_files_from_directory("/path/to/images")
for image_dict in image_files:
    for name, path in image_dict.items():
        print(f"画像名: {name}, パス: {path}")
```

#### `get_image_path_by_name(name: str) -> Optional[str]`

画像名からフルパスを取得します。

- **パラメータ**: `name` - 画像名（拡張子なし）
- **戻り値**: 画像のフルパス、または`None`

```python
# 使用例
image_path = image_model.get_image_path_by_name("sample_image")
if image_path:
    print(f"画像パス: {image_path}")
```

#### `get_image_names() -> List[str]`

画像名一覧を取得します。

- **戻り値**: 画像名のリスト

```python
# 使用例
names = image_model.get_image_names()
print(f"利用可能な画像: {names}")
```

### 情報取得

#### `get_image_info() -> Dict[str, Any]`

画像情報を取得します。

- **戻り値**: 画像情報を含む辞書

```python
# 使用例
info = image_model.get_image_info()
print(f"パス: {info['path']}")
print(f"元サイズ: {info['original_size']}")
print(f"表示サイズ: {info['display_size']}")
print(f"スケール: {info['scale_factor']}")
```

### リセット機能

#### `clear_image()`

画像情報をクリアします。

```python
# 使用例
image_model.clear_image()
print("画像情報をクリアしました")
```

## プライベートメソッド

### `_calculate_display_size(original_size: Tuple[int, int], canvas_size: Tuple[int, int]) -> Tuple[Tuple[int, int], float]`

表示サイズとスケールファクターを計算します。

- **機能**: アスペクト比を維持しながらキャンバスに収まるサイズを計算
- **戻り値**: (表示サイズ, スケールファクター) のタプル

### `_is_image_file(filename: str) -> bool`

ファイルが画像ファイルかどうかを判定します。

- **機能**: サポートされている拡張子かどうかをチェック
- **戻り値**: 画像ファイルの場合は`True`

## 使用例

### 基本的な使用方法

```python
from src.models.image_model import ImageModel

# ImageModelインスタンスを作成
image_model = ImageModel()

# 画像を読み込み
tk_image = image_model.load_image("/path/to/image.jpg", 800, 600)
if tk_image:
    print(f"画像読み込み成功")
    print(f"元サイズ: {image_model.original_size}")
    print(f"表示サイズ: {image_model.display_size}")
    print(f"スケール: {image_model.scale_factor}")

# 座標変換の例
# マウスクリック位置を元画像座標に変換
mouse_x, mouse_y = 200, 150
orig_x, orig_y = image_model.convert_display_to_original_coords(mouse_x, mouse_y)
print(f"クリック位置 ({mouse_x}, {mouse_y}) → 元画像座標 ({orig_x}, {orig_y})")
```

### ディレクトリからの画像読み込み

```python
# ディレクトリから画像ファイルを検索
image_files = image_model.load_image_files_from_directory("/path/to/images")

# 利用可能な画像名を取得
image_names = image_model.get_image_names()
print(f"利用可能な画像: {image_names}")

# 特定の画像を名前で検索
if "sample" in image_names:
    image_path = image_model.get_image_path_by_name("sample")
    tk_image = image_model.load_image(image_path)
```

### キャンバスサイズ変更対応

```python
# ウィンドウリサイズ時の対応
def on_window_resize(new_width, new_height):
    # 現在の画像を新しいサイズで再読み込み
    new_tk_image = image_model.reload_image_for_canvas_size(new_width, new_height)
    if new_tk_image:
        # キャンバスに再表示
        canvas.create_image(0, 0, anchor="nw", image=new_tk_image)
        
        # 既存の座標マーカーを新しいスケールで再描画
        redraw_coordinate_markers()
```

### エラーハンドリング付きの使用例

```python
try:
    # 画像読み込み
    image_path = "/path/to/image.jpg"
    tk_image = image_model.load_image(image_path, 1024, 768)
    
    if tk_image is None:
        print(f"画像の読み込みに失敗しました: {image_path}")
        return
    
    # 画像情報を取得
    info = image_model.get_image_info()
    print(f"画像情報: {info}")
    
    # 座標変換
    display_coords = (300, 200)
    original_coords = image_model.convert_display_to_original_coords(*display_coords)
    print(f"座標変換: {display_coords} → {original_coords}")
    
except FileNotFoundError:
    print("画像ファイルが見つかりません")
except Exception as e:
    print(f"予期しないエラー: {e}")
```

## 特徴

### 画像処理

- **高品質リサイズ**: PIL.Image.Resampling.LANCZOSによる高品質なリサイズ
- **アスペクト比保持**: 元画像の縦横比を維持した表示
- **複数形式サポート**: JPEG、PNG、BMP、GIF、TIFFに対応

### 座標管理

- **正確な座標変換**: 表示座標と元画像座標の相互変換
- **スケール管理**: リサイズ倍率を正確に管理
- **座標精度**: 整数座標での正確な変換

### メモリ効率

- **Tkinter統合**: TkinterのPhotoImageオブジェクトとして管理
- **適切なリサイズ**: キャンバスサイズに合わせた効率的なリサイズ
- **ガベージコレクション**: 不要な画像オブジェクトの適切な解放

### ファイル管理

- **拡張子チェック**: サポートされている画像形式のみを処理
- **ディレクトリスキャン**: 指定ディレクトリ内の画像ファイルを自動検出
- **名前ベース検索**: ファイル名による画像検索機能

## 注意事項

1. **PILライブラリ**: Pillow（PIL）ライブラリが必要です
2. **メモリ使用量**: 大きな画像ファイルはメモリを多く消費します
3. **座標精度**: 座標変換は整数で行われます
4. **ファイル形式**: サポートされていない形式は読み込みエラーになります
5. **パス管理**: 画像パスは絶対パスでの管理を推奨します

## 依存関係

- `os`: ファイルシステム操作
- `PIL.Image`: 画像読み込み・処理
- `PIL.ImageTk`: Tkinter用画像変換
- `typing`: 型ヒント
  - `Dict`: 辞書型
  - `List`: リスト型
  - `Optional`: オプショナル型
  - `Tuple`: タプル型
  - `Any`: 任意の型
