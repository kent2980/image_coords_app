# Tkinter ウィジェット一覧表

## 🔷 ウィジェットの種類と基本プロパティ

| ウィジェット名         | クラス名            | よく使われるプロパティ                                      |
|----------------------|-------------------|----------------------------------------------------------|
| ラベル               | `Label`           | `text`, `image`, `bg`, `fg`, `font`, `anchor`, `justify`, `width`, `height` |
| ボタン               | `Button`          | `text`, `command`, `image`, `bg`, `fg`, `font`, `state`, `width`, `height` |
| チェックボックス       | `Checkbutton`     | `text`, `variable`, `onvalue`, `offvalue`, `command`, `bg`, `fg` |
| ラジオボタン           | `Radiobutton`     | `text`, `variable`, `value`, `command`, `bg`, `fg`, `font` |
| エントリー             | `Entry`           | `textvariable`, `show`, `width`, `state`, `bg`, `fg`, `font` |
| テキスト               | `Text`            | `height`, `width`, `wrap`, `bg`, `fg`, `font`, `state`, `insertbackground` |
| スケール               | `Scale`           | `from_`, `to`, `orient`, `length`, `tickinterval`, `command` |
| スピンボックス         | `Spinbox`         | `from_`, `to`, `increment`, `values`, `textvariable`, `width`, `command` |
| リストボックス         | `Listbox`         | `selectmode`, `height`, `width`, `bg`, `fg`, `font`, `exportselection` |
| コンボボックス         | `ttk.Combobox`    | `values`, `textvariable`, `state`, `width`, `postcommand` |
| フレーム               | `Frame`           | `bg`, `width`, `height`, `borderwidth`, `relief` |
| ラベルフレーム         | `LabelFrame`      | `text`, `labelanchor`, `bg`, `width`, `height`, `padx`, `pady` |
| パンウィンドウ         | `PanedWindow`     | `orient`, `bg`, `sashrelief`, `sashwidth` |
| キャンバス             | `Canvas`          | `bg`, `width`, `height`, `scrollregion`, `highlightthickness` |
| メニュー               | `Menu`            | `tearoff`, `bg`, `fg`, `activebackground`, `activeforeground` |
| メニューボタン         | `Menubutton`      | `text`, `menu`, `bg`, `fg`, `font`, `indicatoron` |
| メッセージ             | `Message`         | `text`, `bg`, `fg`, `font`, `width`, `justify` |
| プログレスバー         | `ttk.Progressbar` | `orient`, `length`, `mode`, `maximum`, `value` |
| ノートブック（タブ）   | `ttk.Notebook`    | `width`, `height` |
| セパレーター           | `ttk.Separator`   | `orient`, `style` |
| ツリービュー           | `ttk.Treeview`    | `columns`, `show`, `selectmode`, `height` |
| スクロールバー         | `Scrollbar`       | `orient`, `command`, `bg`, `activebackground`, `troughcolor` |
| ダイアログボックス系   | `filedialog`, `messagebox`, `colorchooser` | `initialdir`, `filetypes`, `title` などの関数引数 |

---

## 🔶 各プロパティの詳細説明

| プロパティ名         | 説明 |
|----------------------|------|
| `text`               | ウィジェットに表示する文字列（ラベル、ボタンなど） |
| `image`              | 画像オブジェクト（`PhotoImage`など）を表示 |
| `bg` / `fg`          | 背景色／文字色（背景 = background、前景 = foreground） |
| `font`               | フォント指定（例：`("Arial", 12, "bold")`） |
| `anchor`             | 内容の配置方向（`"n"`, `"w"`, `"center"`など） |
| `justify`            | 複数行テキストの配置（`"left"`, `"center"`, `"right"`） |
| `width` / `height`   | 幅／高さ（文字数またはピクセルで指定） |
| `command`            | ボタンなどのクリック時に実行する関数 |
| `variable`           | 値をバインドする変数（`IntVar`, `StringVar`など） |
| `onvalue` / `offvalue` | チェックボックスのON/OFFで保持される値 |
| `state`              | `"normal"`, `"disabled"`, `"readonly"` などの状態 |
| `show`               | 入力テキストの表示制御（`'*'` などでマスク） |
| `textvariable`       | 入力欄やラベルと `StringVar` などをバインド |
| `wrap`               | テキストの折り返し（`"word"` / `"char"` / `"none"`） |
| `from_` / `to`       | スケール・スピンボックスの最小／最大値 |
| `increment`          | 数値の増加幅（スピンボックスなど） |
| `values`             | 選択肢リスト（コンボボックスなど） |
| `selectmode`         | 選択モード（`"single"`, `"multiple"`, `"browse"`） |
| `exportselection`    | 他ウィジェットとの選択共有（`True` / `False`） |
| `menu`               | `Menubutton` に関連付ける `Menu` オブジェクト |
| `tearoff`            | メニューを切り離せるかどうか（`0` で無効） |
| `mode`               | プログレスバーの表示モード（`"determinate"`, `"indeterminate"`） |
| `maximum` / `value`  | プログレスバーの最大値・現在値 |
| `columns`            | `Treeview` の列定義 |
| `show`（Treeview用） | `"tree"`, `"headings"`, `"both"` で表示制御 |
| `orient`             | `"horizontal"` または `"vertical"` |
| `scrollregion`       | `Canvas` のスクロール対象範囲 |
| `highlightthickness` | キャンバスやエントリーの枠線の太さ |
| `postcommand`        | ドロップダウン表示直前に実行される関数 |

---

> 💡 `ttk` ウィジェットはテーマ対応でよりモダンな見た目になります。`from tkinter import ttk` で使用可能です。