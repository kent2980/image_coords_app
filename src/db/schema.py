from typing import Optional

from sqlmodel import Field, SQLModel
from uuid import UUID, uuid5, NAMESPACE_OID
from datetime import datetime



class BaseModel(SQLModel):
    """ベースデータモデル"""

    insert_timestamp: Optional[str] = Field(default_factory=lambda: str(datetime.now()), description="挿入日時")
    update_timestamp: Optional[str] = Field(default_factory=lambda: str(datetime.now()), description="更新日時")

class Lot(BaseModel):
    """ロットデータモデル"""

    model: Optional[str] = Field(description="モデル名")
    image_path: Optional[str] = Field(description="画像パス")
    parent_lot_number: Optional[str] = Field(description="親ロット番号")
    lot_number: Optional[str] = Field(description="ロット番号")
    worker_number: Optional[str] = Field(description="作業者番号")
    detail_count: Optional[int] = Field(description="座標詳細数")


class Worker(BaseModel):
    """作業者データモデル"""

    name: Optional[str] = Field(description="作業者名")
    number: Optional[str] = Field(description="作業者番号")


class Detail(BaseModel):
    """座標詳細データモデル"""
    id: Optional[UUID] = Field(default=None, description="ID")
    lot_number: Optional[str] = Field(description="ロット番号")
    count_number: Optional[int] = Field(description="アイテム番号")
    x: Optional[int] = Field(description="X座標")
    y: Optional[int] = Field(description="Y座標")
    reference: Optional[str] = Field(description="リファレンス")
    defect: Optional[str] = Field(description="不良名")
    comment: Optional[str] = Field(description="コメント")

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

