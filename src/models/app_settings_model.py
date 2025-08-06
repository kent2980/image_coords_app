"""
App Settings Model
アプリケーション設定を管理するモデル
"""

import os
import configparser
from typing import Dict, Any, Optional
from pathlib import Path


class AppSettingsModel:
    """アプリケーション設定モデル"""
    
    def __init__(self):
        self._settings_file = os.path.join(os.path.expanduser("~"), "image_coords_settings.ini")
        self._default_settings = {
            'image_directory': '',
            'data_directory': '',
            'default_mode': '編集'
        }
        self._current_settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, str]:
        """設定ファイルから設定を読み込み"""
        try:
            if os.path.exists(self._settings_file):
                config = configparser.ConfigParser()
                config.read(self._settings_file, encoding='utf-8')
                
                settings = {}
                if config.has_section('Settings'):
                    for key in self._default_settings:
                        settings[key] = config.get('Settings', key, fallback=self._default_settings[key])
                else:
                    settings = self._default_settings.copy()
                
                return settings
            else:
                return self._default_settings.copy()
                
        except Exception as e:
            print(f"設定ファイル読み込みエラー: {e}")
            return self._default_settings.copy()
    
    def save_settings(self) -> bool:
        """設定ファイルに設定を保存"""
        try:
            config = configparser.ConfigParser()
            config.add_section('Settings')
            
            for key, value in self._current_settings.items():
                config.set('Settings', key, str(value))
            
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                config.write(f)
            
            return True
            
        except Exception as e:
            print(f"設定ファイル保存エラー: {e}")
            return False
    
    def get_setting(self, key: str) -> str:
        """設定値を取得"""
        return self._current_settings.get(key, self._default_settings.get(key, ''))
    
    def set_setting(self, key: str, value: str):
        """設定値を設定"""
        if key in self._default_settings:
            self._current_settings[key] = value
    
    def get_all_settings(self) -> Dict[str, str]:
        """全設定を取得"""
        return self._current_settings.copy()
    
    def update_settings(self, settings: Dict[str, str]):
        """設定を一括更新"""
        for key, value in settings.items():
            if key in self._default_settings:
                self._current_settings[key] = value
    
    def reset_to_defaults(self):
        """設定をデフォルトに戻す"""
        self._current_settings = self._default_settings.copy()
    
    def get_image_directory(self) -> str:
        """画像ディレクトリを取得"""
        return self.get_setting('image_directory')
    
    def set_image_directory(self, directory: str):
        """画像ディレクトリを設定"""
        self.set_setting('image_directory', directory)
    
    def get_data_directory(self) -> str:
        """データディレクトリを取得"""
        return self.get_setting('data_directory')
    
    def set_data_directory(self, directory: str):
        """データディレクトリを設定"""
        self.set_setting('data_directory', directory)
    
    def get_default_mode(self) -> str:
        """デフォルトモードを取得"""
        return self.get_setting('default_mode')
    
    def set_default_mode(self, mode: str):
        """デフォルトモードを設定"""
        if mode in ['編集', '閲覧']:
            self.set_setting('default_mode', mode)
    
    def is_image_directory_valid(self) -> bool:
        """画像ディレクトリが有効かチェック"""
        directory = self.get_image_directory()
        return directory and directory != "未選択" and os.path.exists(directory)
    
    def is_data_directory_valid(self) -> bool:
        """データディレクトリが有効かチェック"""
        directory = self.get_data_directory()
        return directory and directory != "未選択" and os.path.exists(directory)
    
    def ensure_data_directory_exists(self) -> bool:
        """データディレクトリの存在を確認し、必要に応じて作成"""
        directory = self.get_data_directory()
        
        if not directory or directory == "未選択":
            return False
        
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"データディレクトリの作成に失敗: {e}")
            return False
