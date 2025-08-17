# MainController クラス ドキュメント

## 概要

`MainController`クラスは、アプリケーション全体の制御と他のコントローラーとの連携を管理するメインコントローラーです。MVC（Model-View-Controller）パターンにおいて、アプリケーション全体の制御フローを担当します。

## クラス定義

```python
class MainController:
    """メインアプリケーションコントローラー"""
```

## 初期化

### `__init__(coordinate_model, settings_model, worker_model, image_model, board_model, main_view, canvas_view, sidebar_view, dialogs, coordinate_controller, file_controller, board_controller)`

MainControllerインスタンスを初期化します。

#### パラメータ

| パラメータ | 型 | 説明 |
|-----------|---|-----|
| `coordinate_model` | `CoordinateModel` | 座標データモデル |
| `settings_model` | `AppSettingsModel` | アプリケーション設定モデル |
| `worker_model` | `WorkerModel` | 作業者データモデル |
| `image_model` | `ImageModel` | 画像データモデル |
| `board_model` | `BoardModel` | 基盤データモデル |
| `main_view` | `MainView` | メインビュー |
| `canvas_view` | `CoordinateCanvasView` | キャンバスビュー |
| `sidebar_view` | `SidebarView` | サイドバービュー |
| `dialogs` | `Dict[str, Any]` | ダイアログクラス辞書 |
| `coordinate_controller` | `CoordinateController` | 座標コントローラー |
| `file_controller` | `FileController` | ファイルコントローラー |
| `board_controller` | `BoardController` | 基盤コントローラー |

#### 初期化される属性

| 属性名 | 型 | 説明 |
|-------|---|-----|
| `current_date` | `date` | 現在の日付 |
| `current_worker_no` | `Optional[str]` | 現在の作業者番号 |
| `current_worker_name` | `Optional[str]` | 現在の作業者名 |
| `current_lot_number` | `Optional[str]` | 現在のロット番号 |
| `previous_model` | `Optional[str]` | 前回選択されたモデル |
| `model_data` | `List[Any]` | モデルデータ |
| `is_initialized` | `bool` | 初期化フラグ |
| `debug_mode` | `bool` | デバッグモードフラグ |

## 主要メソッド

### アプリケーション初期化

#### `initialize_application()`

アプリケーションを初期化します。

- **処理内容**:
  - 作業者入力ダイアログの表示
  - コントローラー間の連携設定
  - ビューのコールバック設定
  - UI要素の初期化
  - 設定の適用

```python
# 使用例
main_controller.initialize_application()
```

#### `set_debug_mode(debug: bool = True)`

デバッグモードを設定します。

- **パラメータ**: `debug` - デバッグモードの有効/無効
- **機能**: デバッグモード時は作業者入力をスキップ

```python
# 使用例
main_controller.set_debug_mode(True)  # デバッグモード有効
```

### モード管理

#### `on_mode_change()`

モード変更時の処理を行います。

- **編集モード**: 座標の追加・編集が可能
- **閲覧モード**: 座標の表示・選択のみ可能

```python
# 使用例
# モード変更時に自動的に呼び出される
main_controller.on_mode_change()
```

### イベントハンドラー

#### `on_canvas_left_click(event)`

キャンバス左クリック時の処理（編集モード）。

- **機能**: 新しい座標を追加
- **前提条件**: 整番（モデル）とロット番号が設定されている

#### `on_canvas_right_click(event)`

キャンバス右クリック時の処理（編集モード）。

- **機能**: 既存座標の選択

#### `on_canvas_view_click(event)`

キャンバスクリック時の処理（閲覧モード）。

- **機能**: 座標の選択と詳細表示

### モデル管理

#### `on_model_selected()`

モデル選択時の処理を行います。

- **処理内容**:
  - モデル画像の読み込み
  - ロット番号のリセット（モデル変更時）
  - 基盤セッションの自動読み込み
  - 保存名の自動設定

```python
# 使用例
# モデル選択時に自動的に呼び出される
main_controller.on_model_selected()
```

### ロット番号管理

#### `on_lot_number_save()`

ロット番号保存処理を行います。

- **処理内容**:
  - ロット番号の形式チェック
  - サイドバーのモデル名更新
  - 基盤データの保存
  - 保存名の自動更新
  - 最新JSONファイルの自動読み込み

```python
# 使用例
main_controller.on_lot_number_save()
```

#### `on_save_button_click()`

保存ボタンクリック時の処理を行います。

- **処理内容**:
  - ロット番号入力チェック
  - ロット番号保存または座標保存の実行

```python
# 使用例
main_controller.on_save_button_click()
```

### ファイル操作

#### `select_image()`

画像ファイルを選択して読み込みます。

```python
# 使用例
main_controller.select_image()
```

#### `load_json(file_path=None)`

JSONファイルを読み込みます。

- **パラメータ**: `file_path` - JSONファイルパス（Noneの場合はダイアログで選択）

```python
# 使用例
main_controller.load_json()  # ダイアログで選択
main_controller.load_json("/path/to/file.json")  # 直接指定
```

#### `save_coordinates()`

座標をJSONファイルに保存します。

- **処理内容**:
  - 座標データの検証
  - 保存ディレクトリの作成
  - JSONファイルの保存
  - 基盤データの保存

```python
# 使用例
main_controller.save_coordinates()
```

### 座標操作

#### `clear_coordinates()`

全座標をクリアします。

```python
# 使用例
main_controller.clear_coordinates()
```

#### `delete_coordinate()`

現在選択中の座標を削除します。

```python
# 使用例
main_controller.delete_coordinate()
```

#### `prev_coordinate()`

前の座標に移動します。

```python
# 使用例
main_controller.prev_coordinate()
```

#### `next_coordinate()`

次の座標に移動します。

```python
# 使用例
main_controller.next_coordinate()
```

### アンドゥ/リドゥ

#### `undo_action()`

最後の操作を元に戻します。

```python
# 使用例
main_controller.undo_action()
```

#### `redo_action()`

アンドゥした操作をやり直します。

```python
# 使用例
main_controller.redo_action()
```

### 現品票切り替え

#### `on_item_tag_change()`

現品票切り替えボタンが押された時の処理を行います。

- **編集モード**: 製番と指図入力ダイアログ
- **閲覧モード**: 指図入力のみのダイアログ

```python
# 使用例
main_controller.on_item_tag_change()
```

### 基盤管理

#### `prev_board()`

前の基盤を選択します。

```python
# 使用例
main_controller.prev_board()
```

#### `next_board()`

次の基盤を選択します。

- **前提条件**: 現在の基盤に座標データが存在する

```python
# 使用例
main_controller.next_board()
```

#### `delete_board()`

現在の基盤を削除します。

- **確認ダイアログ**: 削除前に確認ダイアログを表示

```python
# 使用例
main_controller.delete_board()
```

#### `save_all_boards()`

全基盤をJSONファイルに保存します。

```python
# 使用例
main_controller.save_all_boards()
```

#### `load_board_session()`

基盤セッションを読み込みます。

```python
# 使用例
main_controller.load_board_session()
```

### メニュー操作

#### `new_project()`

新しいプロジェクトを作成します（実装予定）。

#### `new_file()`

新しいファイルを作成します（実装予定）。

#### `open_file()`

ファイルを開きます（JSON読み込み）。

#### `save_file()`

ファイルを保存します（座標保存）。

#### `exit_app()`

アプリケーションを終了します。

### 設定管理

#### `open_settings()`

設定ダイアログを開きます。

```python
# 使用例
main_controller.open_settings()
```

#### `on_settings_changed()`

設定変更時のコールバック処理を行います。

- **処理内容**: モデル選択リストの更新

### キャンバスイベント

#### `on_canvas_resize(new_width: int, new_height: int)`

キャンバスサイズ変更時の処理を行います。

- **処理内容**:
  - 画像の再読み込み
  - 座標マーカーの再描画

```python
# 使用例
main_controller.on_canvas_resize(1024, 768)
```

### フォームデータ管理

#### `on_form_data_changed()`

フォームデータ変更時の処理を行います。

- **処理内容**:
  - 座標詳細情報の更新
  - JSONファイルの自動更新

```python
# 使用例
# フォーム変更時に自動的に呼び出される
main_controller.on_form_data_changed()
```

### 日付管理

#### `select_date()`

日付選択ダイアログを表示します。

```python
# 使用例
main_controller.select_date()
```

## 使用例

### 基本的な初期化と使用

```python
# MainControllerの初期化
main_controller = MainController(
    coordinate_model=coordinate_model,
    settings_model=settings_model,
    worker_model=worker_model,
    image_model=image_model,
    board_model=board_model,
    main_view=main_view,
    canvas_view=canvas_view,
    sidebar_view=sidebar_view,
    dialogs=dialogs,
    coordinate_controller=coordinate_controller,
    file_controller=file_controller,
    board_controller=board_controller
)

# アプリケーションの初期化
main_controller.initialize_application()

# デバッグモードの設定（開発時）
main_controller.set_debug_mode(True)
```

### イベント駆動の処理

```python
# キャンバスクリックイベントの処理
def handle_canvas_click(event):
    if current_mode == "編集":
        main_controller.on_canvas_left_click(event)
    else:
        main_controller.on_canvas_view_click(event)

# モデル選択イベントの処理
def handle_model_selection():
    main_controller.on_model_selected()
```

### ファイル操作の例

```python
# 画像とJSONファイルの読み込み
main_controller.select_image()
main_controller.load_json()

# 座標データの保存
main_controller.save_coordinates()
```

## 特徴

### アーキテクチャ

- **MVCパターン**: Model-View-Controller設計パターンの実装
- **コントローラー連携**: 複数のコントローラーとの協調動作
- **イベント駆動**: ユーザーインタラクションに基づく処理

### ユーザビリティ

- **作業者管理**: 作業者情報の入力と管理
- **モード切り替え**: 編集モードと閲覧モードの切り替え
- **自動保存**: フォーム変更時の自動更新機能

### データ管理

- **座標管理**: 座標データと詳細情報の統合管理
- **基盤管理**: 複数基盤の切り替えと管理
- **ファイル管理**: JSONファイルの読み込み・保存

### 品質保証

- **バリデーション**: ロット番号形式等の入力チェック
- **エラーハンドリング**: 適切なエラー処理と表示
- **デバッグサポート**: デバッグモードでの開発支援

## 注意事項

1. **初期化順序**: `initialize_application()`を呼び出してから使用
2. **デバッグモード**: 環境変数`DEBUG=1`でデバッグモードが有効
3. **ロット番号形式**: `1234567-10`または`1234567-20`の形式が必要
4. **基盤切り替え**: 座標データが存在しない場合は次の基盤に切り替え不可
5. **メモリ管理**: 大量の画像データ使用時はメモリ使用量に注意

## 依存関係

- **標準ライブラリ**:
  - `os`: ファイルシステム操作
  - `tkinter`: GUI関連操作
  - `datetime`: 日付処理
  - `json`: JSON操作
  - `re`: 正規表現（ロット番号検証）

- **プロジェクト内依存**:
  - `models`: 各種データモデル
  - `views`: 各種ビュークラス
  - `controllers`: 各種コントローラー
  - `dialogs`: ダイアログクラス
