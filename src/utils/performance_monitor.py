"""
パフォーマンス監視設定
アプリケーションのパフォーマンス計測レベルを制御
"""

import os
from enum import Enum
from typing import Optional


class PerformanceLevel(Enum):
    """パフォーマンス監視レベル"""
    NONE = 0      # 監視無効
    BASIC = 1     # 基本的な測定のみ
    DETAILED = 2  # 詳細な測定
    DEBUG = 3     # デバッグレベル（全ての測定）


class PerformanceConfig:
    """パフォーマンス設定管理"""
    
    def __init__(self):
        self._level = self._get_level_from_env()
        self._enabled = self._level != PerformanceLevel.NONE
    
    def _get_level_from_env(self) -> PerformanceLevel:
        """環境変数からパフォーマンスレベルを取得"""
        level_str = os.getenv('PERFORMANCE_LEVEL', 'BASIC').upper()
        try:
            return PerformanceLevel[level_str]
        except KeyError:
            return PerformanceLevel.BASIC
    
    @property
    def enabled(self) -> bool:
        """パフォーマンス監視が有効かどうか"""
        return self._enabled
    
    @property
    def level(self) -> PerformanceLevel:
        """現在のパフォーマンス監視レベル"""
        return self._level
    
    def should_log_basic(self) -> bool:
        """基本ログを出力するかどうか"""
        return self._level.value >= PerformanceLevel.BASIC.value
    
    def should_log_detailed(self) -> bool:
        """詳細ログを出力するかどうか"""
        return self._level.value >= PerformanceLevel.DETAILED.value
    
    def should_log_debug(self) -> bool:
        """デバッグログを出力するかどうか"""
        return self._level.value >= PerformanceLevel.DEBUG.value
    
    def set_level(self, level: PerformanceLevel):
        """パフォーマンスレベルを設定"""
        self._level = level
        self._enabled = level != PerformanceLevel.NONE


# グローバル設定インスタンス
performance_config = PerformanceConfig()


def log_timing(level: PerformanceLevel, message: str):
    """レベルに応じてタイミングログを出力"""
    if performance_config.level.value >= level.value:
        print(message)


def log_basic(message: str):
    """基本レベルのログ出力"""
    if performance_config.should_log_basic():
        print(f"[PERF] {message}")


def log_detailed(message: str):
    """詳細レベルのログ出力"""
    if performance_config.should_log_detailed():
        print(f"[DETAIL] {message}")


def log_debug(message: str):
    """デバッグレベルのログ出力"""
    if performance_config.should_log_debug():
        print(f"[DEBUG] {message}")
