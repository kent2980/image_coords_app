from typing import Optional

from sqlmodel import Field, SQLModel


class Lot(SQLModel, table=True):
    """ロットデータモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    model: str
    image_path: str
    lot_no: str
    worker_no: str


class Worker(SQLModel, table=True):
    """作業者データモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    worker_no: str


class Coordinate(SQLModel, table=True):
    """座標データモデル"""

    id: Optional[int] = Field(default=None, primary_key=True)
    lot_id: int
    x: int
    y: int
    reference: Optional[str] = Field(default=None, description="リファレンス")
    defect_name: Optional[str] = Field(default=None, description="不具合名")
    serial: Optional[str] = Field(default=None, description="シリアル番号")
    comment: Optional[str] = Field(default=None, description="コメント")
