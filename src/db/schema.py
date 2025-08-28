from typing import Optional
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid5, NAMESPACE_OID
from datetime import datetime
from pydantic import field_validator




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
    id: Optional[str] = Field(default="", description="ID")
    lot_number: Optional[str] = Field(default="", description="ロット番号")
    board_number: Optional[int] = Field(default=None, description="基板番号")
    count_number: Optional[int] = Field(default=None, description="アイテム番号")
    x: Optional[int] = Field(default=None, description="X座標")
    y: Optional[int] = Field(default=None, description="Y座標")
    reference: Optional[str] = Field(default="", description="リファレンス")
    defect: Optional[str] = Field(default="", description="不良名")
    comment: Optional[str] = Field(default="", description="コメント")

    @field_validator('board_number', mode='before')
    @classmethod
    def validate_board_number(cls, v):
        """board_numberの型変換"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v

    @field_validator('count_number', mode='before')
    @classmethod
    def validate_count_number(cls, v):
        """count_numberの型変換"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v

    @field_validator('x', mode='before')
    @classmethod
    def validate_x(cls, v):
        """xの型変換"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v

    @field_validator('y', mode='before')
    @classmethod
    def validate_y(cls, v):
        """yの型変換"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return None
        return v

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.generate_id()
    
    def generate_id(self) -> str:
        """決定論的なIDを生成"""
        identifier_string = f"{self.lot_number}_{self.board_number}_{self.count_number}"
        self.id = str(uuid5(NAMESPACE_OID, identifier_string))
        return self.id
    
    @classmethod
    def create_with_auto_id(cls, lot_number: Optional[str], board_number: Optional[int], count_number: Optional[int], **kwargs):
        """自動ID生成付きでインスタンスを作成"""
        instance = cls(lot_number=lot_number, count_number=count_number, **kwargs)
        instance.generate_id()
        return instance