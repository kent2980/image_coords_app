# MVCアーキテクチャ移行ガイド

## 📋 移行概要

従来のモノリシックなアーキテクチャから、保守性と拡張性に優れたMVC（Model-View-Controller）パターンに移行しました。

## 🏗️ アーキテクチャ構成

### Models（データレイヤー）
- **CoordinateModel**: 座標データの管理とビジネスロジック
- **AppSettingsModel**: アプリケーション設定の管理
- **WorkerModel**: 作業者情報の管理
- **ImageModel**: 画像処理と座標変換

### Views（プレゼンテーションレイヤー）
- **MainView**: メインウィンドウとレイアウト
- **CoordinateCanvasView**: 座標表示とマーカー描画
- **SidebarView**: 詳細情報の表示・編集
- **dialogs**: 各種ダイアログウィンドウ

### Controllers（ビジネスロジックレイヤー）
- **MainController**: アプリケーション全体の制御
- **CoordinateController**: 座標操作の制御
- **FileController**: ファイル入出力の制御

## 🔄 データフロー

```
User Input → View → Controller → Model → Controller → View → User Display
```

1. ユーザーがViewで操作を行う
2. ViewがControllerに操作を通知
3. ControllerがModelのデータを更新
4. ModelがControllerに変更を通知
5. ControllerがViewに更新を指示
6. Viewが最新のデータを表示

## 🚀 実行方法

### 新しいMVC版（推奨）
```bash
python main_mvc.py
```

### 従来版（互換性のため保持）
```bash
python main.py
```

## 📂 ファイル構成

```
├── main_mvc.py              # MVC版メインエントリーポイント
├── main.py                  # 従来版（レガシー）
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── coordinate_model.py
│   │   ├── app_settings_model.py
│   │   ├── worker_model.py
│   │   └── image_model.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── main_view.py
│   │   ├── coordinate_canvas_view.py
│   │   ├── sidebar_view.py
│   │   └── dialogs.py
│   └── controllers/
│       ├── __init__.py
│       ├── main_controller.py
│       ├── coordinate_controller.py
│       └── file_controller.py
└── README.md
```

## 🎯 MVCパターンの利点

### 1. 分離された責任
- 各コンポーネントが明確な役割を持つ
- コードの理解しやすさが向上
- バグの特定が容易

### 2. 再利用性
- Modelは複数のViewで利用可能
- Viewは異なるControllerで制御可能
- 各コンポーネントが独立している

### 3. テスタビリティ
- 各レイヤーを個別にテスト可能
- モックオブジェクトによる単体テストが容易
- 統合テストの実装が簡単

### 4. 保守性
- 機能追加や変更が局所化される
- 他のコンポーネントへの影響を最小化
- リファクタリングが安全

## 🔧 機能対応表

| 機能 | 従来版 | MVC版 | 状態 |
|------|--------|-------|------|
| 座標追加 | ✅ | ✅ | 移行完了 |
| 座標削除 | ✅ | ✅ | 移行完了 |
| 座標編集 | ✅ | ✅ | 移行完了 |
| ファイル保存 | ✅ | ✅ | 移行完了 |
| ファイル読み込み | ✅ | ✅ | 移行完了 |
| 設定管理 | ✅ | ✅ | 移行完了 |
| 作業者管理 | ✅ | ✅ | 移行完了 |
| CSV出力 | ✅ | ✅ | 移行完了 |
| アンドゥ・リドゥ | ✅ | ✅ | 移行完了 |

## 🐛 トラブルシューティング

### Q: アプリケーションが起動しない
A: 以下を確認してください：
- Python 3.12以上がインストールされているか
- 必要なライブラリ（Pillow）がインストールされているか
- `src`ディレクトリと必要なファイルが存在するか

### Q: 画像が表示されない
A: 以下を確認してください：
- Pillowライブラリが正しくインストールされているか
- 画像ファイルが対応形式（JPEG, PNG, BMPなど）か
- ファイルパスが正しいか

### Q: 設定が保存されない
A: 以下を確認してください：
- ホームディレクトリへの書き込み権限があるか
- ディスクに十分な空き容量があるか

## 📝 今後の拡張予定

1. **プラグインシステム**: 新しい機能を動的に追加
2. **データベース対応**: SQLiteやPostgreSQLでのデータ管理
3. **ネットワーク機能**: リモートデータベースとの連携
4. **マルチ言語対応**: 国際化（i18n）への対応
5. **テーマシステム**: UIテーマのカスタマイズ

## 📚 参考資料

- [MVCパターンについて](https://ja.wikipedia.org/wiki/Model-View-Controller)
- [Tkinter公式ドキュメント](https://docs.python.org/ja/3/library/tkinter.html)
- [Pillow公式ドキュメント](https://pillow.readthedocs.io/)
