# Image Coordinates App デプロイメントガイド

## 目次

1. [概要](#概要)
2. [本番環境の準備](#本番環境の準備)
3. [実行ファイルの作成](#実行ファイルの作成)
4. [配布パッケージの作成](#配布パッケージの作成)
5. [インストール手順](#インストール手順)
6. [設定管理](#設定管理)
7. [監視とメンテナンス](#監視とメンテナンス)
8. [トラブルシューティング](#トラブルシューティング)

## 概要

このガイドでは、Image Coordinates Appを本番環境にデプロイするための手順を説明します。Windowsスタンドアロン環境での配布を想定しています。

### デプロイメント方式

- **スタンドアロン実行ファイル**: PyInstallerを使用
- **ネットワーク配布**: 共有フォルダ経由
- **設定管理**: 外部設定ファイル
- **データ管理**: ローカルファイルシステム

## 本番環境の準備

### システム要件

#### ハードウェア要件

- **CPU**: Intel Core i3 以上 または AMD Ryzen 3 以上
- **メモリ**: 4GB以上（8GB推奨）
- **ストレージ**: 2GB以上の空き容量
- **ディスプレイ**: 1366x768以上（1920x1080推奨）

#### ソフトウェア要件

- **OS**: Windows 10 (1903以降) または Windows 11
- **Microsoft Visual C++ Redistributable**: 最新版
- **.NET Framework**: 4.7.2以上（オプション）

### ネットワーク環境

#### 共有フォルダ設定

```powershell
# 共有フォルダの作成（管理者権限）
New-Item -Path "C:\SharedData\ImageCoords" -ItemType Directory
New-SmbShare -Name "ImageCoords" -Path "C:\SharedData\ImageCoords" -FullAccess "Domain\Users"

# アクセス権限の設定
Grant-SmbShareAccess -Name "ImageCoords" -AccountName "Domain\Users" -AccessRight Full
```

#### ファイアウォール設定

```powershell
# SMBファイル共有の許可
New-NetFirewallRule -DisplayName "SMB File Sharing" -Direction Inbound -Protocol TCP -LocalPort 445 -Action Allow
```

## 実行ファイルの作成

### PyInstallerの設定

#### 1. 必要なパッケージのインストール

```bash
pip install pyinstaller
pip install --upgrade setuptools
```

#### 2. specファイルの作成

```python
# image_coords_app.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

block_cipher = None

# データファイルのリスト
datas = [
    ('assets/icons', 'assets/icons'),
    ('defects.txt', '.'),
    ('README.md', '.'),
    ('docs', 'docs'),
]

# 隠れたインポートの指定
hiddenimports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'json',
    'csv',
    'datetime',
    'typing',
]

a = Analysis(
    ['main.py'],
    pathex=[Path.cwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy'],  # 不要なライブラリを除外
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
    console=False,  # Windowsアプリケーションとして実行
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico',
    version='version_info.txt'  # バージョン情報ファイル
)
```

#### 3. バージョン情報ファイル

```python
# version_info.txt
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'041104B0',
        [StringStruct(u'CompanyName', u'Your Company'),
        StringStruct(u'FileDescription', u'Image Coordinates App'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'ImageCoordsApp'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2025'),
        StringStruct(u'OriginalFilename', u'ImageCoordsApp.exe'),
        StringStruct(u'ProductName', u'Image Coordinates App'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1041, 1200])])
  ]
)
```

#### 4. ビルドスクリプト

```python
# scripts/build_production.py
#!/usr/bin/env python3
"""本番用ビルドスクリプト"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

def clean_build_dirs():
    """ビルドディレクトリをクリーンアップ"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned {dir_name} directory")

def run_tests():
    """テストを実行"""
    print("Running tests...")
    result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("Tests failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    print("All tests passed!")
    return True

def build_executable():
    """実行ファイルをビルド"""
    print("Building executable...")
    result = subprocess.run(['pyinstaller', 'image_coords_app.spec'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("Build failed!")
        print(result.stdout)
        print(result.stderr)
        return False
    print("Build completed successfully!")
    return True

def create_deployment_package():
    """デプロイメントパッケージを作成"""
    print("Creating deployment package...")
    
    # パッケージディレクトリの作成
    package_dir = Path('deployment_package')
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # 実行ファイルをコピー
    shutil.copy('dist/ImageCoordsApp.exe', package_dir)
    
    # 設定ファイルをコピー
    config_files = ['defects.txt', 'image_coords_settings.ini']
    for config_file in config_files:
        if os.path.exists(config_file):
            shutil.copy(config_file, package_dir)
    
    # ドキュメントをコピー
    docs_dir = package_dir / 'docs'
    if Path('docs').exists():
        shutil.copytree('docs', docs_dir)
    
    # インストールスクリプトを作成
    create_install_script(package_dir)
    
    # ZIPファイルを作成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f'ImageCoordsApp_v1.0.0_{timestamp}.zip'
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, package_dir)
                zipf.write(file_path, arc_path)
    
    print(f"Deployment package created: {zip_name}")
    return zip_name

def create_install_script(package_dir):
    """インストールスクリプトを作成"""
    install_script = '''@echo off
echo Image Coordinates App インストーラー
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\ImageCoordsApp"
set "DESKTOP_DIR=%USERPROFILE%\\Desktop"
set "START_MENU_DIR=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs"

echo インストール先: %INSTALL_DIR%
echo.

REM 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo このインストーラーは管理者権限で実行する必要があります。
    echo 右クリックして「管理者として実行」を選択してください。
    pause
    exit /b 1
)

REM インストールディレクトリの作成
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM ファイルのコピー
echo ファイルをコピーしています...
copy /Y "ImageCoordsApp.exe" "%INSTALL_DIR%\\"
copy /Y "defects.txt" "%INSTALL_DIR%\\"
copy /Y "image_coords_settings.ini" "%INSTALL_DIR%\\"
if exist "docs" xcopy /E /I /Y "docs" "%INSTALL_DIR%\\docs"

REM ショートカットの作成
echo ショートカットを作成しています...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP_DIR%\\Image Coordinates App.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ImageCoordsApp.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU_DIR%\\Image Coordinates App.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\ImageCoordsApp.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"

echo.
echo インストールが完了しました！
echo デスクトップまたはスタートメニューからアプリケーションを起動できます。
echo.
pause
'''
    
    install_script_path = package_dir / 'install.bat'
    with open(install_script_path, 'w', encoding='shift_jis') as f:
        f.write(install_script)

def main():
    """メインビルドプロセス"""
    print("=== Image Coordinates App 本番ビルド ===")
    print()
    
    # ビルド前のクリーンアップ
    clean_build_dirs()
    
    # テストの実行
    if not run_tests():
        print("テストに失敗したため、ビルドを中止します。")
        sys.exit(1)
    
    # 実行ファイルのビルド
    if not build_executable():
        print("ビルドに失敗しました。")
        sys.exit(1)
    
    # デプロイメントパッケージの作成
    package_name = create_deployment_package()
    
    print()
    print("=== ビルド完了 ===")
    print(f"デプロイメントパッケージ: {package_name}")
    print("配布の準備が整いました！")

if __name__ == '__main__':
    main()
```

### ビルドの実行

```bash
# 本番用ビルドの実行
python scripts/build_production.py

# または手動でビルド
pyinstaller image_coords_app.spec
```

## 配布パッケージの作成

### パッケージ構成

```
ImageCoordsApp_v1.0.0_20250818_1200.zip
├── ImageCoordsApp.exe          # メイン実行ファイル
├── defects.txt                 # 不良項目設定
├── image_coords_settings.ini   # 初期設定ファイル
├── install.bat                 # インストールスクリプト
├── uninstall.bat              # アンインストールスクリプト
├── README.txt                  # 簡易説明書
└── docs/                       # 詳細ドキュメント
    ├── USER_MANUAL.md
    ├── SETUP_GUIDE.md
    └── TROUBLESHOOTING.md
```

### アンインストールスクリプト

```batch
@echo off
echo Image Coordinates App アンインストーラー
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\ImageCoordsApp"
set "DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\Image Coordinates App.lnk"
set "START_MENU_SHORTCUT=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Image Coordinates App.lnk"

REM 管理者権限チェック
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo このアンインストーラーは管理者権限で実行する必要があります。
    pause
    exit /b 1
)

echo アンインストールを実行しますか？ (Y/N)
set /p confirm=
if /i not "%confirm%"=="Y" goto :cancel

REM ショートカットの削除
if exist "%DESKTOP_SHORTCUT%" del "%DESKTOP_SHORTCUT%"
if exist "%START_MENU_SHORTCUT%" del "%START_MENU_SHORTCUT%"

REM アプリケーションフォルダの削除
if exist "%INSTALL_DIR%" (
    echo アプリケーションファイルを削除しています...
    rmdir /s /q "%INSTALL_DIR%"
)

echo.
echo アンインストールが完了しました。
goto :end

:cancel
echo アンインストールをキャンセルしました。

:end
pause
```

## インストール手順

### エンドユーザー向けインストール

#### 1. 配布パッケージの展開

```
1. ZIPファイルをダウンロード
2. 適当なフォルダに展開
3. install.batを右クリック→「管理者として実行」
```

#### 2. 初期設定

アプリケーション初回起動時：

1. **データディレクトリの設定**
   - 共有フォルダまたはローカルフォルダを指定
   - 例: `\\server\ImageCoords\Data` または `C:\ImageCoordsData`

2. **画像ディレクトリの設定**
   - モデル画像が保存されているフォルダを指定
   - 例: `\\server\ImageCoords\Images` または `C:\ImageCoordsImages`

3. **作業者情報の登録**
   - 作業者番号と名前を入力

### サイレントインストール

```batch
REM サイレントインストール用バッチファイル
@echo off

set "INSTALL_DIR=%PROGRAMFILES%\\ImageCoordsApp"
set "DATA_DIR=\\\\server\\ImageCoords\\Data"
set "IMAGE_DIR=\\\\server\\ImageCoords\\Images"

REM アプリケーションのインストール
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
copy /Y "ImageCoordsApp.exe" "%INSTALL_DIR%\\"
copy /Y "defects.txt" "%INSTALL_DIR%\\"

REM 設定ファイルの作成
echo [Directories] > "%INSTALL_DIR%\\image_coords_settings.ini"
echo data_directory=%DATA_DIR% >> "%INSTALL_DIR%\\image_coords_settings.ini"
echo image_directory=%IMAGE_DIR% >> "%INSTALL_DIR%\\image_coords_settings.ini"
echo [Application] >> "%INSTALL_DIR%\\image_coords_settings.ini"
echo default_mode=編集 >> "%INSTALL_DIR%\\image_coords_settings.ini"

echo サイレントインストールが完了しました。
```

## 設定管理

### 設定ファイルの構造

#### image_coords_settings.ini

```ini
[Directories]
data_directory=\\server\ImageCoords\Data
image_directory=\\server\ImageCoords\Images

[Application]
default_mode=編集
auto_save=true
max_undo_stack=50

[UI]
window_width=1400
window_height=900
canvas_width=800
canvas_height=600

[Network]
timeout=30
retry_count=3

[Logging]
log_level=INFO
log_file=app.log
max_log_size=10MB
```

### 一括設定配布

#### Group Policy による設定配布

```powershell
# GPO用PowerShellスクリプト
$configPath = "$env:PROGRAMFILES\ImageCoordsApp\image_coords_settings.ini"
$networkConfig = @"
[Directories]
data_directory=\\fileserver\ImageCoords\Data
image_directory=\\fileserver\ImageCoords\Images

[Application]
default_mode=編集
auto_save=true
"@

$networkConfig | Out-File -FilePath $configPath -Encoding UTF8
```

#### レジストリ設定

```batch
REM レジストリによる設定
reg add "HKLM\SOFTWARE\ImageCoordsApp" /v "DataDirectory" /t REG_SZ /d "\\\\server\\ImageCoords\\Data" /f
reg add "HKLM\SOFTWARE\ImageCoordsApp" /v "ImageDirectory" /t REG_SZ /d "\\\\server\\ImageCoords\\Images" /f
```

## 監視とメンテナンス

### ログ管理

#### ログ設定

```python
# src/utils/logger.py
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logger(log_level: str = "INFO", log_file: str = "app.log"):
    """ロガーの設定"""
    
    # ログディレクトリの作成
    log_dir = Path(os.getenv('APPDATA')) / 'ImageCoordsApp' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_path = log_dir / log_file
    
    # ロガーの設定
    logger = logging.getLogger('ImageCoordsApp')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # ファイルハンドラー（ローテーション付き）
    file_handler = logging.handlers.RotatingFileHandler(
        log_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### パフォーマンス監視

#### メトリクス収集

```python
# src/utils/metrics.py
import psutil
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class MetricsCollector:
    """パフォーマンスメトリクスの収集"""
    
    def __init__(self):
        self.start_time = time.time()
        self.metrics_file = Path(os.getenv('APPDATA')) / 'ImageCoordsApp' / 'metrics.json'
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスを収集"""
        process = psutil.Process()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - self.start_time,
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'open_files': len(process.open_files()),
            'threads': process.num_threads(),
        }
    
    def save_metrics(self, metrics: Dict[str, Any]):
        """メトリクスをファイルに保存"""
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"メトリクス保存エラー: {e}")
```

### 自動アップデート

#### アップデートチェック

```python
# src/utils/updater.py
import requests
import json
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

class AutoUpdater:
    """自動アップデート機能"""
    
    def __init__(self, current_version: str = "1.0.0"):
        self.current_version = current_version
        self.update_server = "https://your-server.com/updates"
        self.install_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent
    
    def check_for_updates(self) -> Optional[Dict[str, Any]]:
        """アップデートをチェック"""
        try:
            response = requests.get(f"{self.update_server}/version.json", timeout=10)
            if response.status_code == 200:
                update_info = response.json()
                latest_version = update_info.get('version')
                
                if self._is_newer_version(latest_version, self.current_version):
                    return update_info
                    
        except Exception as e:
            print(f"アップデートチェックエラー: {e}")
        
        return None
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """バージョン比較"""
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        return latest_parts > current_parts
    
    def download_and_install_update(self, update_info: Dict[str, Any]) -> bool:
        """アップデートをダウンロードしてインストール"""
        try:
            download_url = update_info.get('download_url')
            if not download_url:
                return False
            
            # アップデートファイルのダウンロード
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                return False
            
            update_file = self.install_dir / 'update.exe'
            with open(update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # アップデートの実行
            subprocess.Popen([str(update_file), '/SILENT'], cwd=str(self.install_dir))
            
            return True
            
        except Exception as e:
            print(f"アップデートエラー: {e}")
            return False
```

## トラブルシューティング

### 一般的な問題と解決策

#### 1. アプリケーションが起動しない

**症状**: 実行ファイルをダブルクリックしても何も起こらない

**診断手順**:

```batch
REM デバッグモードで起動
ImageCoordsApp.exe --debug --console

REM イベントログの確認
eventvwr.msc
```

**解決策**:
- Visual C++ Redistributableの再インストール
- 管理者権限での実行
- ウイルス対策ソフトの除外設定

#### 2. ネットワークドライブにアクセスできない

**症状**: 共有フォルダが見つからないエラー

**診断手順**:

```batch
REM ネットワーク接続の確認
ping fileserver

REM 共有フォルダのアクセステスト
net use \\fileserver\ImageCoords
```

**解決策**:
- ネットワーク認証情報の再設定
- ファイアウォール設定の確認
- SMBプロトコルの有効化

#### 3. パフォーマンスの問題

**症状**: アプリケーションの動作が遅い

**診断ツール**:

```python
# パフォーマンス診断スクリプト
import psutil
import time

def diagnose_performance():
    """パフォーマンス診断"""
    print("=== システム情報 ===")
    print(f"CPU使用率: {psutil.cpu_percent(interval=1):.1f}%")
    print(f"メモリ使用率: {psutil.virtual_memory().percent:.1f}%")
    print(f"ディスク使用率: {psutil.disk_usage('/').percent:.1f}%")
    
    print("\n=== プロセス情報 ===")
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        if 'ImageCoords' in proc.info['name']:
            print(f"PID: {proc.info['pid']}")
            print(f"CPU: {proc.info['cpu_percent']:.1f}%")
            print(f"メモリ: {proc.info['memory_percent']:.1f}%")

if __name__ == '__main__':
    diagnose_performance()
```

### エラーログの分析

#### ログレベル別の対応

**ERROR**: 即座に対応が必要
```
2025-08-18 10:30:15 - ERROR - ファイル読み込みエラー: permission denied
→ ファイル権限の確認と修正
```

**WARNING**: 注意が必要
```
2025-08-18 10:30:16 - WARNING - 大きな画像ファイル: 5.2MB
→ 画像サイズの最適化を推奨
```

**INFO**: 正常な動作
```
2025-08-18 10:30:17 - INFO - 座標データを保存しました: C:\Data\coords.json
→ 正常な処理記録
```

### サポートツール

#### 診断情報収集スクリプト

```python
# support/collect_diagnostics.py
import os
import sys
import json
import zipfile
import platform
import subprocess
from datetime import datetime
from pathlib import Path

def collect_system_info():
    """システム情報を収集"""
    return {
        'os': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'username': os.getenv('USERNAME'),
        'timestamp': datetime.now().isoformat()
    }

def collect_application_info():
    """アプリケーション情報を収集"""
    app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    
    info = {
        'install_directory': str(app_dir),
        'executable_exists': (app_dir / 'ImageCoordsApp.exe').exists(),
        'config_files': []
    }
    
    # 設定ファイルの確認
    config_files = ['image_coords_settings.ini', 'defects.txt']
    for config_file in config_files:
        file_path = app_dir / config_file
        info['config_files'].append({
            'name': config_file,
            'exists': file_path.exists(),
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'modified': file_path.stat().st_mtime if file_path.exists() else None
        })
    
    return info

def create_diagnostic_package():
    """診断パッケージを作成"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f'ImageCoordsApp_Diagnostics_{timestamp}.zip'
    
    with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # システム情報
        system_info = collect_system_info()
        zipf.writestr('system_info.json', json.dumps(system_info, indent=2))
        
        # アプリケーション情報
        app_info = collect_application_info()
        zipf.writestr('application_info.json', json.dumps(app_info, indent=2))
        
        # ログファイル
        log_dir = Path(os.getenv('APPDATA')) / 'ImageCoordsApp' / 'logs'
        if log_dir.exists():
            for log_file in log_dir.glob('*.log'):
                zipf.write(log_file, f'logs/{log_file.name}')
        
        # 設定ファイル
        app_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
        config_files = ['image_coords_settings.ini', 'defects.txt']
        for config_file in config_files:
            file_path = app_dir / config_file
            if file_path.exists():
                zipf.write(file_path, f'config/{config_file}')
    
    print(f"診断パッケージを作成しました: {package_name}")
    return package_name

if __name__ == '__main__':
    create_diagnostic_package()
```

---

## 補足情報

### セキュリティ考慮事項

- 実行ファイルのデジタル署名
- ウイルス対策ソフトの誤検知対策
- ネットワーク通信の暗号化
- 設定ファイルの保護

### 今後の拡張

- MSIインストーラーの作成
- 自動アップデート機能の実装
- 複数言語対応
- クラウドストレージ連携

---

**最終更新**: 2025年8月18日  
**バージョン**: 1.0.0  
**作成者**: GitHub Copilot
