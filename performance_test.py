#!/usr/bin/env python
"""
パフォーマンステスト用スクリプト
on_canvas_left_clickの性能を測定
"""

import time
import tkinter as tk
from unittest.mock import Mock, MagicMock

# アプリケーションの初期化をシミュレート
def create_mock_app():
    """モックアプリケーションを作成"""
    print("[SETUP] モックアプリケーション作成中...")
    
    # モック設定
    coordinate_model = Mock()
    coordinate_model.add_coordinate.return_value = 0
    coordinate_model.coordinates = []
    coordinate_model.current_index = 0
    
    settings_model = Mock()
    worker_model = Mock()
    image_model = Mock()
    image_model.convert_display_to_original_coords.return_value = (100, 200)
    
    board_model = Mock()
    lot_model = Mock()
    
    main_view = Mock()
    main_view.show_error = Mock()
    
    sidebar_view = Mock()
    sidebar_view.clear_form = Mock()
    sidebar_view.set_coordinate_detail = Mock()
    sidebar_view.focus_reference_entry = Mock()
    
    canvas_view = Mock()
    canvas_view.add_coordinate_marker = Mock()
    
    # コントローラーの作成
    from src.controllers.coordinate_controller import CoordinateController
    from src.controllers.main_controller import MainController
    
    coordinate_controller = CoordinateController(coordinate_model, image_model)
    coordinate_controller.canvas_view = canvas_view
    coordinate_controller.main_view = main_view
    
    main_controller = MainController(
        coordinate_model=coordinate_model,
        settings_model=settings_model,
        worker_model=worker_model,
        image_model=image_model,
        board_model=board_model,
        lot_model=lot_model,
        main_view=main_view,
        sidebar_view=sidebar_view,
        canvas_view=canvas_view,
        dialogs={},  # 空の辞書を追加
        coordinate_controller=coordinate_controller,
        file_controller=Mock(),
        board_controller=Mock()
    )
    
    # 必要な状態設定
    main_controller._current_model = "TEST_MODEL"
    main_controller.current_lot_number = "TEST_LOT"
    
    return main_controller


def simulate_click_events(controller, num_clicks=10):
    """クリックイベントをシミュレート"""
    print(f"[TEST] {num_clicks}回のクリックイベントをシミュレート開始")
    
    times = []
    
    for i in range(num_clicks):
        # モックイベント作成
        event = Mock()
        event.x = 100 + i * 10
        event.y = 200 + i * 5
        
        # 実行時間測定
        start_time = time.time()
        controller.on_canvas_left_click(event)
        elapsed = (time.time() - start_time) * 1000
        times.append(elapsed)
        
        print(f"クリック {i+1}: {elapsed:.2f}ms")
    
    # 統計情報
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n[RESULTS] パフォーマンス統計:")
    print(f"平均: {avg_time:.2f}ms")
    print(f"最小: {min_time:.2f}ms") 
    print(f"最大: {max_time:.2f}ms")
    print(f"総回数: {len(times)}回")
    
    # パフォーマンス評価
    if avg_time > 100:
        print("⚠️  警告: 平均処理時間が100msを超えています")
    elif avg_time > 50:
        print("⚡ 注意: 平均処理時間が50msを超えています")
    else:
        print("✅ 良好: パフォーマンスは良好です")


def main():
    """メイン実行関数"""
    print("=" * 60)
    print("パフォーマンステスト開始")
    print("=" * 60)
    
    try:
        # モックアプリケーション作成
        controller = create_mock_app()
        
        # パフォーマンステスト実行
        simulate_click_events(controller, 5)
        
        print("\n" + "=" * 60)
        print("パフォーマンステスト完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
