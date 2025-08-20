from sqlmodel import SQLModel, Field
from typing import Optional

class Lot(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model: str
    image_path: str
    lot_no: str
    worker_no: str

class Worker(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    worker_no: str

class Coordinate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lot_id: int
    x: int
    y: int
    detail: Optional[str] = None

# 必要に応じて他のモデルも追加可能
