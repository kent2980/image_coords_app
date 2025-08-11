#!/usr/bin/env python3
"""
型推定の実際の使用例とメリットを示すスクリプト
"""

import os
import sys

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk

    from src.views.main_view import CallbackProtocol, CallbackTypes, MainView
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)


def demonstrate_type_benefits():
    """型推定改善のメリットを実演"""
    print("🎯 MainView 型推定改善のメリット実演")
    print("=" * 60)

    root = tk.Tk()
    root.withdraw()

    main_view = MainView(root)

    print("📋 改善前と改善後の比較:")
    print()

    print("【改善前】")
    print("❌ callbacks.get('clear_coordinates')  # 型: Optional[Any]")
    print("❌ 戻り値の型が不明")
    print("❌ IDEで自動補完が効かない")
    print("❌ None チェックの必要性が不明")
    print("❌ 実行時エラーのリスク")
    print()

    print("【改善後】")
    print("✅ get_callback('clear_coordinates')    # 型: Optional[CallbackProtocol]")
    print("✅ 戻り値の型が明確")
    print("✅ IDEで自動補完が利用可能")
    print("✅ None チェックが型推定で強制")
    print("✅ コンパイル時のエラー検出")
    print()

    # 実際のコード例
    def safe_callback() -> None:
        print("安全なコールバック実行")

    def unsafe_callback() -> str:
        return "戻り値あり"

    callbacks: CallbackTypes = {
        "clear_coordinates": safe_callback,
        "delete_coordinate": unsafe_callback,  # 型: ignore が必要になる場合
    }

    main_view.set_callbacks(callbacks)

    print("💡 実際のコード例:")
    print()

    print("# 型安全なコールバック取得")
    print("callback = main_view.get_callback('clear_coordinates')")
    callback = main_view.get_callback("clear_coordinates")
    print(f"# 型推定結果: {type(callback).__name__}")
    print()

    print("# None チェックが型推定で強制される")
    print("if callback:")
    print("    callback()  # ここで安全に実行可能")
    if callback:
        callback()
        print("    # ✅ 実行成功")
    print()

    print("# has_callback で存在確認")
    print("if main_view.has_callback('clear_coordinates'):")
    if main_view.has_callback("clear_coordinates"):
        print("    # ✅ コールバックが存在します")
        callback = main_view.get_callback("clear_coordinates")
        if callback:
            callback()
            print("    # ✅ 安全に実行完了")
    print()

    print("🔧 開発者向けメリット:")
    print("1. ✅ VS Code/PyCharm で自動補完が利用可能")
    print("2. ✅ 型チェッカー (mypy, Pylance) でエラー検出")
    print("3. ✅ リファクタリング時の安全性向上")
    print("4. ✅ ドキュメント生成での型情報表示")
    print("5. ✅ チーム開発でのコード理解容易性")
    print()

    print("🚀 パフォーマンスメリット:")
    print("1. ✅ 実行前の型チェックによるバグ削減")
    print("2. ✅ None チェック忘れの防止")
    print("3. ✅ 実行時エラーの大幅削減")
    print("4. ✅ デバッグ時間の短縮")
    print()

    # 実際のUIでの使用例
    print("🖥️  実際のUI要素での型推定効果:")
    print()

    print("# ボタンクリック時のコールバック設定")
    print("button = tk.Button(")
    print("    text='全削除',")
    print("    command=main_view.get_callback('clear_coordinates')  # 型安全")
    print(")")
    print()

    print("# メニュー項目でのコールバック設定")
    print("menu.add_command(")
    print("    label='座標をクリア',")
    print("    command=main_view.get_callback('clear_coordinates')  # 型安全")
    print(")")
    print()

    root.destroy()

    print("=" * 60)
    print("🎉 型推定改善により、より安全で保守しやすいコードが実現されました！")


if __name__ == "__main__":
    demonstrate_type_benefits()
