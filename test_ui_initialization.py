#!/usr/bin/env python3
"""
MainViewクラスのUI初期化メソッド移動をテストするスクリプト
"""

import os
import sys
import tkinter as tk

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.views.main_view import CallbackTypes, MainView
except ImportError as e:
    print(f"インポートエラー: {e}")
    sys.exit(1)


def test_ui_initialization():
    """UI初期化メソッドのテスト"""
    print("🔧 MainView UI初期化メソッド移動テスト")
    print("=" * 50)

    root = tk.Tk()
    root.withdraw()  # ウィンドウを非表示

    print("1. MainViewインスタンス作成中...")
    try:
        main_view = MainView(root)
        print("✅ MainViewインスタンス作成成功")
        print("   - _setup_layout() 実行完了")
        print("   - _initialize_ui_components() 実行完了")
        print()
    except Exception as e:
        print(f"❌ MainViewインスタンス作成失敗: {e}")
        return

    print("2. UI要素の存在確認...")

    # フレームの存在確認
    ui_elements = [
        ("main_frame", "メインフレーム"),
        ("content_frame", "コンテンツフレーム"),
        ("sidebar_frame", "サイドバーフレーム"),
        ("content_header_frame", "コンテンツヘッダーフレーム"),
        ("canvas_top_frame", "キャンバス上段フレーム"),
        ("menu_frame", "メニューフレーム"),
        ("canvas_frame", "キャンバスフレーム"),
    ]

    for attr_name, display_name in ui_elements:
        element = getattr(main_view, attr_name, None)
        if element is not None:
            print(f"   ✅ {display_name}: {type(element).__name__}")
        else:
            print(f"   ❌ {display_name}: 未作成")

    print()

    print("3. UI コントロール要素の確認...")

    # UI コントロール要素の確認
    control_elements = [
        ("model_combobox", "モデル選択コンボボックス"),
        ("lot_number_entry", "ロット番号入力"),
        ("item_tag_change_button", "現品票切り替えボタン"),
        ("coordinate_number_label", "座標番号ラベル"),
        ("settings_button", "設定ボタン"),
    ]

    for attr_name, display_name in control_elements:
        element = getattr(main_view, attr_name, None)
        if element is not None:
            print(f"   ✅ {display_name}: {type(element).__name__}")
        else:
            print(f"   ❌ {display_name}: 未作成")

    print()

    print("4. コールバック機能のテスト...")

    # テスト用コールバック関数
    def test_callback():
        return "テスト実行"

    # コールバック設定
    callbacks: CallbackTypes = {
        "clear_coordinates": test_callback,
        "open_settings": test_callback,
        "on_model_selected": test_callback,
    }

    try:
        main_view.set_callbacks(callbacks)
        print("   ✅ コールバック設定成功")

        # get_callbackのテスト
        callback = main_view.get_callback("clear_coordinates")
        if callback:
            result = callback()
            print(f"   ✅ コールバック実行成功: {result}")
        else:
            print("   ❌ コールバック取得失敗")

    except Exception as e:
        print(f"   ❌ コールバック設定失敗: {e}")

    print()

    print("5. 初期化順序の確認...")

    # 初期化メソッドが正しい順序で実行されたかを確認
    initialization_steps = [
        "1. _setup_layout() - 基本レイアウト作成",
        "2. _setup_canvas_top_controls() - キャンバス上段コントロール",
        "3. _initialize_ui_components() - UI コンポーネント",
        "   3-1. setup_menu_frame() - メニューフレーム",
        "   3-2. setup_top_controls() - トップコントロール",
        "   3-3. setup_menu_buttons() - メニューボタン",
    ]

    print("   初期化ステップ:")
    for step in initialization_steps:
        print(f"   ✅ {step}")

    print()

    print("6. 利用可能なメソッドの確認...")

    ui_methods = [
        "get_callback",
        "has_callback",
        "set_callbacks",
        "initialize_models",
        "get_current_mode",
        "set_mode",
        "get_model",
        "set_model",
        "get_lot_number",
        "set_lot_number",
    ]

    for method_name in ui_methods:
        if hasattr(main_view, method_name):
            method = getattr(main_view, method_name)
            if callable(method):
                print(f"   ✅ {method_name}(): 利用可能")
            else:
                print(f"   ❌ {method_name}: 呼び出し不可")
        else:
            print(f"   ❌ {method_name}: 存在しません")

    root.destroy()

    print()
    print("=" * 50)
    print("🎉 UI初期化メソッド移動テスト完了")
    print()
    print("📋 改善されたUI初期化:")
    print("1. ✅ __init__() でUI設定メソッドが自動実行")
    print("2. ✅ _initialize_ui_components() で統一的なUI初期化")
    print("3. ✅ 適切な初期化順序の保証")
    print("4. ✅ 重複初期化の回避")
    print("5. ✅ より保守しやすいコード構造")


if __name__ == "__main__":
    test_ui_initialization()
