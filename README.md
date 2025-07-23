# 💪 Python GUI アプリのビルド手順（macOS & Windows）

## 📁 前提条件

- Python 3.x インストール済み
- アプリファイル：`image_coords_app.py`
- 使用ライブラリ：`tkinter`, `Pillow`, `PyInstaller`
- 表示画像：`your_image.jpg`（例：`sg180306_01-thumb-570xauto-21122.jpg`）

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
pyinstaller --onefile --windowed main.py
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
pyinstaller --onefile --windowed main.py
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
