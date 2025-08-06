# 💪 画像座標管理アプリケーション (MVC アーキテクチャ版)

## 🏗️ アーキテクチャ概要

このアプリケーションは **MVC (Model-View-Controller)** パターンで設計されており、保守性と拡張性を向上させています。

### 📁 プロジェクト構造
```
src/
├── models/          # データモデル
│   ├── coordinate_model.py    # 座標データ管理
│   ├── app_settings_model.py  # アプリケーション設定
│   ├── worker_model.py        # 作業者情報管理
│   └── image_model.py         # 画像処理・変換
├── views/           # UI コンポーネント
│   ├── main_view.py           # メインウィンドウ
│   ├── coordinate_canvas_view.py # 座標表示キャンバス
│   ├── sidebar_view.py        # サイドバー
│   └── dialogs.py             # ダイアログ
└── controllers/     # ビジネスロジック
    ├── main_controller.py     # メインコントローラー
    ├── coordinate_controller.py # 座標操作
    └── file_controller.py     # ファイル操作
```

## 🚀 実行方法

### MVC版（推奨）
```bash
python main_mvc.py
```

### レガシー版
```bash
python main.py
```

## 📁 前提条件

- Python 3.12+ インストール済み
- 必要ライブラリ：`tkinter`, `Pillow`, `PyInstaller`

## 🔧 ビルド手順（macOS & Windows）

## 📋 設定ファイル

### アプリケーション設定（自動生成）
アプリケーションの設定は、ユーザーのホームディレクトリに自動的に保存されます：
- **ファイル名**: `image_coords_settings.ini`
- **場所**: `%USERPROFILE%\image_coords_settings.ini` (Windows) / `~/image_coords_settings.ini` (Mac/Linux)

**設定項目**:
```ini
[Settings]
image_directory = C:\path\to\images
data_directory = C:\path\to\data
default_mode = 編集
```

### ドロップダウンリスト設定
アプリケーションの動作をカスタマイズするため、実行ファイルと同じディレクトリに以下のテキストファイルを配置してください：

### models.txt (不要 - 現在は画像ディレクトリから自動読み込み)
~~モデル選択のドロップダウンに表示される項目を定義します。~~
現在は設定ウィンドウで指定した画像ディレクトリ内の画像ファイル名が自動的に読み込まれます。

### defects.txt
不良名選択のドロップダウンに表示される項目を定義します。
```
ズレ
裏
飛び
傷
汚れ
欠け
変色
寸法不良
形状不良
その他
```

**注意**: ファイルが存在しない場合は、デフォルト値が使用されます。

---

## 📦 アプリのコード（共通）

```
# image_coords_app.py

import sys
import os
import tkinter as tk
from PIL import Image, ImageTk

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

coordinates = []

def on_click(event):
    x, y = event.x, event.y
    coordinates.append((x, y))
    canvas.create_oval(x-3, y-3, x+3, y+3, fill='red')

def save_coordinates():
    with open('coords.txt', 'w') as f:
        for x, y in coordinates:
            f.write(f'{x},{y}\n')

image_path = resource_path("your_image.jpg")
img = Image.open(image_path)
tk_img = ImageTk.PhotoImage(img)

root = tk.Tk()
canvas = tk.Canvas(root, width=img.width, height=img.height)
canvas.pack()
canvas.create_image(0, 0, anchor='nw', image=tk_img)
canvas.bind('<Button-1>', on_click)

btn = tk.Button(root, text="Save Coordinates", command=save_coordinates)
btn.pack()

root.mainloop()
```

---

## 🍎 macOSでのビルド手順（.app）

### 1. ライブラリをインストール

```bash
pip install pillow pyinstaller
```

### 2. ビルドコマンド（画像同格）

```bash
pyinstaller --onefile --windowed --name image_coords_app main.py
```

> ✅ `:`（コロン）で区切ること（macOS）

### 3. 実行ファイルの確認

- 出力先: `dist/image_coords_app`
- 実行コマンド:

```bash
./dist/image_coords_app.app/Contents/MacOS/image_coords_app
```

### 4. セキュリティ設定の解除（初回のみ）

```bash
xattr -d com.apple.quarantine dist/image_coords_app.app
```

---

## 🪟 Windowsでのビルド手順（.exe）

### 1. ライブラリをインストール（cmd または PowerShell）

```bash
pip install pillow pyinstaller
```

### 2. ビルドコマンド（画像同格）

```bash
pyinstaller --onefile --windowed --name image_coords_app main.py
```

> ✅ `;`（セミコロン）で区切ること（Windows）

### 3. 実行ファイルの確認

- 出力先: `dist/image_coords_app.exe`
- ダブルクリックで起動可能

---

## ✅ 備考

| 内容                 | 詳細                                        |
| -------------------- | ------------------------------------------- |
| 座標保存先           | アプリと同じディレクトリの `coords.txt`   |
| 複数OSでビルドしたい | 各OS上で `pyinstaller` を実行する必要あり |
| アイコン設定         | `--icon your_icon.ico` オプションを追加   |

---

## ❓ よくあるエラーと対策

| エラー                     | 原因                             | 対策                                                    |
| -------------------------- | -------------------------------- | ------------------------------------------------------- |
| `FileNotFoundError`      | 画像ファイルのパスが見つからない | `--add-data` で画像を含め、`resource_path()` を使用 |
| GUIが起動しない            | `tk` が使えない                | macでは `brew install tcl-tk` で対処                  |
| セキュリティ警告で開けない | macOSのGatekeeper                | `xattr` で署名解除 or セキュリティ設定で許可          |

---

必要であれば `.dmg` や `.msi` インストーラの作成手順もまとめますので、お気軽にどうぞ！
