# Image Coordinates App 開発ガイド

## 目次

1. [開発環境の構築](#開発環境の構築)
2. [プロジェクト構造](#プロジェクト構造)
3. [アーキテクチャ](#アーキテクチャ)
4. [開発規約](#開発規約)
5. [テスト](#テスト)
6. [デバッグ](#デバッグ)
7. [ビルドとデプロイ](#ビルドとデプロイ)
8. [コントリビューション](#コントリビューション)

## 開発環境の構築

### 必要なツール

- **Python 3.8+**
- **Git**
- **VS Code** (推奨エディタ)
- **mypy** (型チェック)
- **pylint** (コード品質)
- **black** (コードフォーマッター)

### セットアップ手順

1. **リポジトリのクローン**
```bash
git clone https://github.com/kent2980/image_coords_app.git
cd image_coords_app
```

2. **仮想環境の作成と有効化**
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

3. **開発用依存関係のインストール**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. **VS Code設定**
```bash
# VS Code拡張機能をインストール
code --install-extension ms-python.python
code --install-extension ms-python.mypy-type-checker
code --install-extension ms-python.pylint
```

### 推奨VS Code拡張機能

- **Python** - 基本的なPython開発支援
- **Pylance** - 高機能な型チェック・補完
- **Python Docstring Generator** - docstring自動生成
- **GitLens** - Git統合機能
- **Bracket Pair Colorizer** - ブラケットの色分け

## プロジェクト構造

```
image_coords_app/
├── main.py                 # アプリケーションエントリーポイント
├── requirements.txt        # 本番用依存関係
├── requirements-dev.txt    # 開発用依存関係
├── setup.py               # パッケージ設定
├── README.md              # プロジェクト概要
├── .gitignore             # Git除外設定
├── .vscode/               # VS Code設定
│   ├── settings.json      # エディタ設定
│   ├── launch.json        # デバッグ設定
│   └── tasks.json         # タスク設定
├── src/                   # ソースコード
│   ├── __init__.py
│   ├── controllers/       # コントローラー層
│   │   ├── __init__.py
│   │   ├── main_controller.py
│   │   ├── coordinate_controller.py
│   │   ├── file_controller.py
│   │   └── board_controller.py
│   ├── models/            # モデル層
│   │   ├── __init__.py
│   │   ├── coordinate_model.py
│   │   ├── image_model.py
│   │   ├── worker_model.py
│   │   ├── board_model.py
│   │   └── app_settings_model.py
│   ├── views/             # ビュー層
│   │   ├── __init__.py
│   │   ├── main_view.py
│   │   ├── coordinate_canvas_view.py
│   │   ├── sidebar_view.py
│   │   └── dialogs/       # ダイアログ
│   │       ├── __init__.py
│   │       ├── worker_input_dialog.py
│   │       ├── settings_dialog.py
│   │       └── date_select_dialog.py
│   └── utils/             # ユーティリティ
│       ├── __init__.py
│       └── file_manager_class.py
├── tests/                 # テストコード
│   ├── __init__.py
│   ├── unit/              # ユニットテスト
│   ├── integration/       # 統合テスト
│   └── fixtures/          # テストデータ
├── docs/                  # ドキュメント
│   ├── README.md
│   ├── USER_MANUAL.md
│   ├── DEVELOPMENT.md
│   └── API/               # API文書
├── assets/                # 静的リソース
│   └── icons/             # アプリケーションアイコン
├── sample_data/           # サンプルデータ
└── scripts/               # 開発スクリプト
    ├── build.py           # ビルドスクリプト
    ├── test.py            # テスト実行
    └── lint.py            # コード品質チェック
```

## アーキテクチャ

### MVC パターン

本プロジェクトは **MVC (Model-View-Controller)** パターンを採用しています。

#### Model (モデル層)
- **責任**: データの管理と操作
- **場所**: `src/models/`
- **主要クラス**:
  - `CoordinateModel`: 座標データ管理
  - `ImageModel`: 画像データ管理
  - `WorkerModel`: 作業者データ管理
  - `BoardModel`: 基盤セッション管理
  - `AppSettingsModel`: アプリケーション設定

#### View (ビュー層)
- **責任**: ユーザーインターフェースの表示
- **場所**: `src/views/`
- **主要クラス**:
  - `MainView`: メインウィンドウ
  - `CoordinateCanvasView`: 座標表示キャンバス
  - `SidebarView`: サイドバー
  - `*Dialog`: 各種ダイアログ

#### Controller (コントローラー層)
- **責任**: ビジネスロジックと制御
- **場所**: `src/controllers/`
- **主要クラス**:
  - `MainController`: アプリケーション全体の制御
  - `CoordinateController`: 座標操作制御
  - `FileController`: ファイル操作制御
  - `BoardController`: 基盤操作制御

### 依存関係の管理

#### TYPE_CHECKING パターン

循環インポートを避けるため、型注釈には`TYPE_CHECKING`を使用：

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.coordinate_model import CoordinateModel
    from ..views.main_view import MainView

class SomeController:
    def __init__(self, model: "CoordinateModel", view: "MainView"):
        self.model = model
        self.view = view
```

#### プロトコルパターン

柔軟性を向上させるため、プロトコル（インターフェース）を活用：

```python
from typing import Protocol

class CallbackProtocol(Protocol):
    def __call__(self) -> Any: ...

class ViewInterface:
    def set_callbacks(self, callbacks: Dict[str, CallbackProtocol]) -> None:
        """コールバック関数を設定"""
        pass
```

## 開発規約

### コーディング規約

#### 1. PEP 8 準拠

- 行の長さ: 最大88文字 (black デフォルト)
- インデント: スペース4文字
- インポート順序: 標準ライブラリ → サードパーティ → ローカル

#### 2. 命名規約

```python
# クラス名: PascalCase
class CoordinateModel:
    pass

# 関数・変数名: snake_case
def add_coordinate(x: int, y: int) -> int:
    coordinate_count = len(coordinates)
    return coordinate_count

# 定数: UPPER_SNAKE_CASE
MAX_UNDO_STACK_SIZE = 50
DEFAULT_CANVAS_WIDTH = 800

# プライベートメソッド: _で開始
def _update_display(self) -> None:
    pass
```

#### 3. 型注釈

すべての公開メソッドで型注釈を使用：

```python
from typing import List, Dict, Optional, Tuple, Any

def process_coordinates(
    coordinates: List[Tuple[int, int]], 
    details: Dict[str, Any]
) -> Optional[bool]:
    """座標データを処理する
    
    Args:
        coordinates: 座標のリスト
        details: 詳細情報の辞書
        
    Returns:
        処理成功時はTrue、失敗時はFalse、エラー時はNone
    """
    pass
```

#### 4. docstring 規約

Google スタイルのdocstringを使用：

```python
def calculate_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
    """2点間の距離を計算する
    
    Args:
        point1: 開始点の座標 (x, y)
        point2: 終了点の座標 (x, y)
        
    Returns:
        2点間のユークリッド距離
        
    Raises:
        ValueError: 座標が不正な場合
        
    Example:
        >>> calculate_distance((0, 0), (3, 4))
        5.0
    """
    import math
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx*dx + dy*dy)
```

### コミット規約

#### Conventional Commits 形式

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### コミットタイプ

- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメントのみの変更
- `style`: コードの意味に影響しない変更（空白、フォーマット等）
- `refactor`: バグ修正や機能追加ではないコード変更
- `test`: テストの追加や修正
- `chore`: ビルドプロセスやツールの変更

#### 例

```bash
feat(coordinate): 座標のアンドゥ・リドゥ機能を追加

- CoordinateModelにアンドゥスタックを実装
- 最大50件の操作履歴を保持
- MainControllerでCtrl+Z/Ctrl+Yをバインド

Closes #123
```

### ブランチ戦略

#### Git Flow

- `main`: 本番リリースブランチ
- `develop`: 開発統合ブランチ
- `feature/*`: 機能開発ブランチ
- `release/*`: リリース準備ブランチ
- `hotfix/*`: 緊急修正ブランチ

#### 例

```bash
# 新機能開発
git checkout develop
git pull origin develop
git checkout -b feature/coordinate-search
# 開発作業...
git push origin feature/coordinate-search
# プルリクエスト作成

# 緊急修正
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix
# 修正作業...
git push origin hotfix/critical-bug-fix
```

## テスト

### テスト構造

```
tests/
├── unit/                  # ユニットテスト
│   ├── test_models/       # モデルのテスト
│   ├── test_controllers/  # コントローラーのテスト
│   └── test_utils/        # ユーティリティのテスト
├── integration/           # 統合テスト
│   ├── test_workflows/    # ワークフローテスト
│   └── test_apis/         # API統合テスト
├── fixtures/              # テストデータ
│   ├── sample_images/     # サンプル画像
│   ├── sample_json/       # サンプルJSONファイル
│   └── test_data.py       # テストデータ定義
└── conftest.py           # pytest設定
```

### テストの実行

```bash
# すべてのテストを実行
python -m pytest

# 特定のテストファイルを実行
python -m pytest tests/unit/test_models/test_coordinate_model.py

# カバレッジを含めて実行
python -m pytest --cov=src --cov-report=html

# 詳細な出力
python -m pytest -v -s
```

### テストの書き方

#### ユニットテストの例

```python
import pytest
from unittest.mock import Mock, patch
from src.models.coordinate_model import CoordinateModel

class TestCoordinateModel:
    """CoordinateModelのテストクラス"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.model = CoordinateModel()
    
    def test_add_coordinate(self):
        """座標追加のテスト"""
        # Arrange
        x, y = 100, 200
        
        # Act
        index = self.model.add_coordinate(x, y)
        
        # Assert
        assert index == 0
        assert len(self.model.coordinates) == 1
        assert self.model.coordinates[0] == (x, y)
    
    def test_add_coordinate_with_invalid_params(self):
        """不正なパラメータでの座標追加テスト"""
        # Act & Assert
        with pytest.raises(ValueError):
            self.model.add_coordinate(-1, -1)
    
    @patch('src.models.coordinate_model.datetime')
    def test_undo_functionality(self, mock_datetime):
        """アンドゥ機能のテスト"""
        # Arrange
        mock_datetime.now.return_value = "2025-01-01 12:00:00"
        self.model.add_coordinate(100, 200)
        self.model.add_coordinate(300, 400)
        
        # Act
        result = self.model.undo()
        
        # Assert
        assert result is True
        assert len(self.model.coordinates) == 1
        assert self.model.coordinates[0] == (100, 200)
```

#### 統合テストの例

```python
import pytest
import tempfile
import os
from src.controllers.main_controller import MainController
from src.models.coordinate_model import CoordinateModel

class TestMainControllerIntegration:
    """MainControllerの統合テスト"""
    
    def setup_method(self):
        """テスト用の一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test.jpg")
        # テスト用画像を作成...
    
    def teardown_method(self):
        """一時ファイルをクリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_coordinate_workflow(self):
        """座標追加から保存までのワークフロー"""
        # テスト実装...
        pass
```

### テストデータの管理

#### fixtures/test_data.py

```python
"""テストデータの定義"""

SAMPLE_COORDINATES = [
    (100, 200),
    (300, 400),
    (500, 600)
]

SAMPLE_COORDINATE_DETAILS = [
    {"reference": "R1", "defect": "ズレ", "comment": "テスト1"},
    {"reference": "R2", "defect": "傷", "comment": "テスト2"},
    {"reference": "R3", "defect": "汚れ", "comment": "テスト3"}
]

SAMPLE_JSON_DATA = {
    "model": "TEST_MODEL",
    "coordinates": SAMPLE_COORDINATES,
    "coordinate_details": SAMPLE_COORDINATE_DETAILS,
    "lot_number": "1234567-10",
    "worker_no": "TEST001",
    "created_at": "2025-01-01T12:00:00"
}
```

## デバッグ

### デバッグ設定

#### launch.json (VS Code)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Main App",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "DEBUG": "1"
            }
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Python: Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${workspaceFolder}/tests"],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

### ログ出力

#### ロギング設定

```python
import logging
import os

# デバッグモードの設定
DEBUG = os.getenv('DEBUG', '0') == '1'

# ログレベルの設定
log_level = logging.DEBUG if DEBUG else logging.INFO

# ロガーの設定
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

#### デバッグ用の便利関数

```python
def debug_print(func):
    """デコレータ: 関数の入出力をログ出力"""
    def wrapper(*args, **kwargs):
        if DEBUG:
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        if DEBUG:
            logger.debug(f"{func.__name__} returned {result}")
        return result
    return wrapper

@debug_print
def add_coordinate(self, x: int, y: int) -> int:
    """座標を追加（デバッグ情報付き）"""
    # 実装...
```

### パフォーマンス分析

#### プロファイリング

```python
import cProfile
import pstats

def profile_function(func):
    """関数のプロファイルを取得"""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 上位10件を表示
    
    return result
```

#### メモリ使用量の監視

```python
import tracemalloc

def monitor_memory():
    """メモリ使用量を監視"""
    tracemalloc.start()
    
    # アプリケーション実行...
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    tracemalloc.stop()
```

## ビルドとデプロイ

### ビルドスクリプト

#### scripts/build.py

```python
#!/usr/bin/env python3
"""ビルドスクリプト"""

import os
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """ビルドディレクトリをクリーンアップ"""
    build_dirs = ['build', 'dist', '*.egg-info']
    for pattern in build_dirs:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

def run_tests():
    """テストを実行"""
    result = subprocess.run(['python', '-m', 'pytest'], capture_output=True)
    if result.returncode != 0:
        print("Tests failed!")
        return False
    return True

def build_executable():
    """実行ファイルをビルド"""
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--icon=assets/icons/app_icon.ico',
        'main.py'
    ]
    subprocess.run(cmd)

def main():
    """メインビルドプロセス"""
    print("Starting build process...")
    
    clean_build()
    
    if not run_tests():
        exit(1)
    
    build_executable()
    
    print("Build completed successfully!")

if __name__ == '__main__':
    main()
```

### PyInstaller設定

#### main.spec

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icons', 'assets/icons'),
        ('defects.txt', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ImageCoordsApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico'
)
```

### 継続的インテグレーション

#### .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with pylint
      run: |
        pylint src/
    
    - name: Type check with mypy
      run: |
        mypy src/
    
    - name: Test with pytest
      run: |
        pytest --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## コントリビューション

### プルリクエストのプロセス

1. **Issue作成**: 機能要望やバグ報告のIssueを作成
2. **ブランチ作成**: `feature/issue-番号-簡潔な説明`形式
3. **開発**: 規約に従って実装
4. **テスト**: 新機能のテストを追加
5. **プルリクエスト**: テンプレートに従って作成
6. **レビュー**: コードレビューを実施
7. **マージ**: 承認後にマージ

### プルリクエストテンプレート

```markdown
## 概要
<!-- 変更内容の簡潔な説明 -->

## 関連Issue
<!-- Closes #123 -->

## 変更内容
- [ ] 新機能の追加
- [ ] バグ修正
- [ ] リファクタリング
- [ ] ドキュメント更新
- [ ] テスト追加

## テスト
- [ ] ユニットテストを追加/更新
- [ ] 統合テストを追加/更新
- [ ] 手動テストを実施

## チェックリスト
- [ ] コードがプロジェクトの規約に従っている
- [ ] 新機能にはテストが含まれている
- [ ] ドキュメントが更新されている
- [ ] Breaking changeがある場合は明記している

## スクリーンショット
<!-- UIの変更がある場合は画像を添付 -->
```

### コードレビューガイドライン

#### レビュワー向け

- **機能性**: 仕様を満たしているか
- **コード品質**: 読みやすく保守しやすいか
- **パフォーマンス**: 性能上の問題はないか
- **セキュリティ**: セキュリティ上の問題はないか
- **テスト**: 適切なテストが含まれているか

#### レビュー時のチェックポイント

```python
# ❌ 悪い例
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result

# ✅ 良い例
def process_positive_numbers(numbers: List[int]) -> List[int]:
    """正の数を2倍にして返す
    
    Args:
        numbers: 整数のリスト
        
    Returns:
        正の数を2倍にしたリスト
    """
    return [num * 2 for num in numbers if num > 0]
```

---

## 追加リソース

### 参考資料

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

### 開発ツール

- **Black**: コードフォーマッター
- **isort**: インポート文の整理
- **mypy**: 静的型チェック
- **pylint**: コード品質チェック
- **pytest**: テストフレームワーク
- **coverage.py**: テストカバレッジ

### コミュニティ

- **GitHub Discussions**: 質問や議論
- **Issues**: バグ報告や機能要望
- **Wiki**: 詳細なドキュメント

---

**最終更新**: 2025年8月18日  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot
