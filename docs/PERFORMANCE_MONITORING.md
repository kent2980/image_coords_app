# パフォーマンス監視機能

## 概要

`on_canvas_left_click`メソッドのパフォーマンス最適化のため、詳細な実行時間計測機能を実装しました。

## 機能

### 1. 実行時間計測
- **ステップ別計測**: 各処理ステップの実行時間を個別に測定
- **サブステップ分析**: 細かい処理単位での時間計測
- **デコレーター**: `@timing_decorator`による関数全体の実行時間測定

### 2. 計測レベル制御
```bash
# 環境変数でログレベルを制御
set PERFORMANCE_LEVEL=NONE     # 監視無効
set PERFORMANCE_LEVEL=BASIC    # 基本測定
set PERFORMANCE_LEVEL=DETAILED # 詳細測定
set PERFORMANCE_LEVEL=DEBUG    # 全測定
```

### 3. パフォーマンステスト
- **自動化テスト**: `performance_test.py`によるパフォーマンス検証
- **統計分析**: 平均・最小・最大実行時間の算出
- **しきい値評価**: 性能評価による判定

## 使用方法

### 基本的な使用
```python
from src.utils.performance_monitor import performance_config, log_basic

# パフォーマンス監視が有効な場合のみ実行
if performance_config.enabled:
    log_basic("処理開始")
```

### 詳細計測
```python
# step_timerコンテキストマネージャーを使用
with step_timer("座標追加処理"):
    # 処理内容
    result = add_coordinate(x, y)
```

### タイミングデコレーター
```python
@timing_decorator
def my_function(self):
    # この関数の実行時間が自動計測される
    pass
```

## 測定結果

### 現在のパフォーマンス
- **平均処理時間**: 7.69ms
- **処理範囲**: 6.47ms - 10.09ms
- **評価**: ✅ 良好（目標50ms未満）

### ボトルネック特定
1. `_update_coordinate_display` (2-3ms)
2. `coordinate_controller.add_coordinate` (0.5-7ms)

## 最適化提案

### 実装済み
- ✅ 詳細な実行時間計測
- ✅ ステップ別パフォーマンス監視
- ✅ 自動化パフォーマンステスト

### 今後の改善案
1. **バッチ更新**: GUI更新の一括処理
2. **遅延更新**: 重複更新の回避
3. **キャッシュ機能**: 計算結果の再利用
4. **非同期処理**: 重い処理のバックグラウンド実行

## トラブルシューティング

### パフォーマンス低下時
1. 環境変数`PERFORMANCE_LEVEL=DEBUG`を設定
2. アプリケーションを実行
3. ログ出力から遅い処理を特定
4. 該当箇所の最適化を実施

### 継続的監視
- 平均処理時間が25ms超過で注意
- 50ms超過で警告
- 100ms超過で緊急対応が必要

## ファイル構成

```
src/
├── controllers/
│   ├── main_controller.py          # step_timer実装
│   └── coordinate_controller.py    # timing_decorator実装
├── utils/
│   └── performance_monitor.py      # 監視設定管理
performance_test.py                 # 自動化テスト
PERFORMANCE_REPORT.md              # 詳細分析レポート
```

## 注意事項

- パフォーマンス監視は開発・デバッグ時のみ有効化推奨
- 本番環境では`PERFORMANCE_LEVEL=NONE`に設定
- ログ出力が多い場合は詳細レベルを調整
