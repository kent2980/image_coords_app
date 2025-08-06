"""
MVCアーキテクチャのテスト
基本的な機能の動作確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """モデル層のテスト"""
    print("=== モデル層テスト ===")
    
    # 座標モデルのテスト
    from src.models import CoordinateModel
    coord_model = CoordinateModel()
    
    # 座標追加テスト
    index1 = coord_model.add_coordinate(100, 200)
    index2 = coord_model.add_coordinate(300, 400)
    
    print(f"座標追加: 座標1={coord_model.coordinates[0]}, 座標2={coord_model.coordinates[1]}")
    
    # 詳細情報設定テスト
    detail = {'reference': 'TEST-001', 'defect': '傷'}
    coord_model.set_coordinate_detail(index1, detail)
    
    retrieved_detail = coord_model.get_coordinate_detail(index1)
    print(f"詳細情報: {retrieved_detail}")
    
    # アンドゥテスト
    coord_model.add_coordinate(500, 600)
    print(f"座標数（追加後）: {len(coord_model.coordinates)}")
    
    coord_model.undo()
    print(f"座標数（アンドゥ後）: {len(coord_model.coordinates)}")
    
    print("モデル層テスト完了\n")

def test_settings():
    """設定モデルのテスト"""
    print("=== 設定モデルテスト ===")
    
    from src.models import AppSettingsModel
    settings = AppSettingsModel()
    
    print(f"デフォルトモード: {settings.default_mode}")
    print(f"画像ディレクトリ: {settings.image_directory}")
    print(f"データディレクトリ: {settings.data_directory}")
    
    # 設定変更テスト
    settings.default_mode = "閲覧"
    settings.image_directory = "C:/test/images"
    
    print(f"変更後デフォルトモード: {settings.default_mode}")
    print(f"変更後画像ディレクトリ: {settings.image_directory}")
    
    print("設定モデルテスト完了\n")

def test_worker():
    """作業者モデルのテスト"""
    print("=== 作業者モデルテスト ===")
    
    from src.models import WorkerModel
    worker_model = WorkerModel()
    
    # 作業者追加テスト
    worker_model.add_worker("001", "田中太郎")
    worker_model.add_worker("002", "佐藤花子")
    
    print(f"作業者一覧: {worker_model.get_all_workers()}")
    
    # 検証テスト
    validation = worker_model.validate_worker_input("001")
    print(f"作業者001の検証: {validation}")
    
    validation = worker_model.validate_worker_input("999")
    print(f"新規作業者999の検証: {validation}")
    
    print("作業者モデルテスト完了\n")

def test_image():
    """画像モデルのテスト"""
    print("=== 画像モデルテスト ===")
    
    from src.models import ImageModel
    image_model = ImageModel()
    
    # サイズ計算テスト
    original_size = (1920, 1080)
    canvas_size = (800, 600)
    
    display_size, scale_factor = image_model._calculate_display_size(original_size, canvas_size)
    print(f"元サイズ: {original_size}")
    print(f"表示サイズ: {display_size}")
    print(f"スケールファクター: {scale_factor}")
    
    # 座標変換テスト
    image_model._scale_factor = scale_factor
    orig_coords = image_model.convert_display_to_original_coords(400, 300)
    display_coords = image_model.convert_original_to_display_coords(orig_coords[0], orig_coords[1])
    
    print(f"表示座標(400, 300) → 元座標{orig_coords} → 表示座標{display_coords}")
    
    print("画像モデルテスト完了\n")

if __name__ == "__main__":
    print("MVCアーキテクチャ テストプログラム")
    print("=" * 50)
    
    test_models()
    test_settings()
    test_worker()
    test_image()
    
    print("=" * 50)
    print("全テスト完了")
