"""
アプリケーション設定モデル
アプリケーションの設定情報を管理
"""

import configparser
import os
from typing import Any, Dict, Optional


class AppSettingsModel:
    """アプリケーション設定を管理するモデル"""

    def __init__(self):
        self._config = configparser.ConfigParser()
        # プロジェクトルートディレクトリを取得
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self._settings_file = os.path.join(
            project_root, "settings/image_coords_settings.ini"
        )
        self._default_settings = {
            "image_directory": "未選択",
            "data_directory": "未選択",
            "default_mode": "編集",
        }
        self._load_settings()

    def _load_settings(self):
        """設定ファイルを読み込み"""
        try:
            if os.path.exists(self._settings_file):
                self._config.read(self._settings_file, encoding="utf-8")
            else:
                # 設定ファイルが存在しない場合はデフォルト値で作成
                self._create_default_settings()
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            self._create_default_settings()

    def _create_default_settings(self):
        """デフォルト設定を作成"""
        if "Settings" not in self._config:
            self._config.add_section("Settings")

        for key, value in self._default_settings.items():
            self._config.set("Settings", key, str(value))

        self.save_settings()

    def get_setting(self, key: str, default: str = "") -> str:
        """設定値を取得"""
        try:
            return self._config.get("Settings", key, fallback=default)
        except Exception:
            return default

    def set_setting(self, key: str, value: str):
        """設定値を設定"""
        if "Settings" not in self._config:
            self._config.add_section("Settings")

        self._config.set("Settings", key, str(value))

    def get_all_settings(self) -> Dict[str, str]:
        """全設定を辞書で取得"""
        settings = {}
        if "Settings" in self._config:
            for key in self._config["Settings"]:
                settings[key] = self._config.get("Settings", key)
        return settings

    def update_settings(self, settings: Dict[str, str]):
        """複数の設定を一括更新"""
        if "Settings" not in self._config:
            self._config.add_section("Settings")

        for key, value in settings.items():
            self._config.set("Settings", key, str(value))

    def save_settings(self) -> bool:
        """設定をファイルに保存"""
        try:
            with open(self._settings_file, "w", encoding="utf-8") as configfile:
                self._config.write(configfile)
            return True
        except Exception as e:
            print(f"設定保存エラー: {e}")
            return False

    def reset_to_defaults(self):
        """設定をデフォルトに戻す"""
        self._config.clear()
        self._create_default_settings()

    @property
    def image_directory(self) -> str:
        """画像ディレクトリ"""
        return self.get_setting("image_directory", "未選択")

    @image_directory.setter
    def image_directory(self, value: str):
        """画像ディレクトリを設定"""
        self.set_setting("image_directory", value)

    @property
    def data_directory(self) -> str:
        """データディレクトリ"""
        return self.get_setting("data_directory", "未選択")

    @data_directory.setter
    def data_directory(self, value: str):
        """データディレクトリを設定"""
        self.set_setting("data_directory", value)

    @property
    def default_mode(self) -> str:
        """デフォルトモード"""
        return self.get_setting("default_mode", "編集")

    @default_mode.setter
    def default_mode(self, value: str):
        """デフォルトモードを設定"""
        self.set_setting("default_mode", value)

    @property
    def settings_file_path(self) -> str:
        """設定ファイルのパス"""
        return self._settings_file
