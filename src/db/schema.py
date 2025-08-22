from typing import Any, Dict, List, Optional, Tuple

from sqlmodel import Field, SQLModel, JSON


class Lot(SQLModel):
    """ロットデータモデル"""

    model: str
    image_path: str
    lot_no: str
    worker_no: str


class Worker(SQLModel):
    """作業者データモデル"""

    name: str
    worker_no: str


class Coordinate(SQLModel):
    """座標データモデル"""

    id: int = Field(default=None, primary_key=True)
    coordinate_detail: Tuple[int, int]  = Field(default=None, sa_type=JSON, description="座標詳細情報")
    reference: Optional[str] = Field(default=None, description="リファレンス")
    defect_name: Optional[str] = Field(default=None, description="不具合名")
    serial: Optional[str] = Field(default=None, description="シリアル番号")
    comment: Optional[str] = Field(default=None, description="コメント")


class Detail(SQLModel):
    item_number: int
    reference: str
    defect: str
    repaired: str
    comment: str

class CoordinateList(SQLModel):
    """座標リストデータモデル"""

    total_count: int
    coordinates: List[Tuple[int,int]]
    details: List[Detail]
