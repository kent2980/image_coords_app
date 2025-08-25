from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Field, SQLModel
from uuid import UUID, uuid5, NAMESPACE_OID
from datetime import datetime


class BaseModel(SQLModel):
    """ベースデータモデル"""

    insert_timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="挿入日時")
    update_timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="更新日時")


class Lot(BaseModel, table=True):
    """ロットデータモデル - テーブル定義"""
    __tablename__ = "lots"

    id: int = Field(default=None, primary_key=True, description="主キー")
    model: Optional[str] = Field(description="モデル名")
    image_path: Optional[str] = Field(description="画像パス")
    parent_lot_number: Optional[str] = Field(description="親ロット番号")
    lot_number: Optional[str] = Field(unique=True, description="ロット番号")
    worker_no: Optional[str] = Field(description="作業者番号")
    detail_count: Optional[int] = Field(default=0, description="座標詳細数")


class Worker(BaseModel, table=True):
    """作業者データモデル - テーブル定義"""
    __tablename__ = "workers"

    id: int = Field(default=None, primary_key=True, description="主キー")
    name: Optional[str] = Field(description="作業者名")
    worker_no: Optional[str] = Field(unique=True, description="作業者番号")


class Detail(BaseModel, table=True):
    """座標詳細データモデル - テーブル定義"""
    __tablename__ = "details"

    id: UUID = Field(default=None, primary_key=True, description="主キー")
    lot_number: Optional[str] = Field(foreign_key="lots.lot_number", description="ロット番号")
    count_number: Optional[int] = Field(description="アイテム番号")
    x: Optional[int] = Field(description="X座標")
    y: Optional[int] = Field(description="Y座標")
    reference: Optional[str] = Field(default="", description="リファレンス")
    defect: Optional[str] = Field(default="", description="不具合")
    repaired: Optional[str] = Field(default="いいえ", description="修理済み")
    comment: Optional[str] = Field(default="", description="コメント")

    def __init__(self, **data):
        super().__init__(**data)
        if self.id is None:
            self.generate_id()
    
    def generate_id(self) -> UUID:
        """決定論的なIDを生成"""
        identifier_string = f"{self.lot_number}_{self.count_number}"
        self.id = uuid5(NAMESPACE_OID, identifier_string)
        return self.id
    
    @classmethod
    def create_with_auto_id(cls, lot_number: Optional[str], count_number: Optional[int], **kwargs):
        """自動ID生成付きでインスタンスを作成"""
        instance = cls(lot_number=lot_number, count_number=count_number, **kwargs)
        instance.generate_id()
        return instance

    class Config:
        """SQLModelの設定"""
        # UUIDフィールドの設定
        arbitrary_types_allowed = True
