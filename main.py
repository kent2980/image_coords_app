"""
画像座標アプリケーション - メインエントリーポイント
MVCアーキテクチャ版を標準として使用
"""

# レガシー版の実行
# from src.image_coords_app import CoordinateApp

# if __name__ == "__main__":
#     app = CoordinateApp()
#     app.run_app()

# MVC版の実行（推奨）
from main_mvc import main

if __name__ == "__main__":
    main()
