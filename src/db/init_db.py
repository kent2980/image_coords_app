from sqlmodel import SQLModel, create_engine
from .models import Lot, Worker, Coordinate

DB_URL = "sqlite:///app_data.db"
engine = create_engine(DB_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    print("DB初期化完了")
