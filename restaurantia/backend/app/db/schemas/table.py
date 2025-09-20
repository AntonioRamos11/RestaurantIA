from pydantic import BaseModel
from typing import Optional

class TableBase(BaseModel):
    number: int
    seats: int
    location_id: int

class TableCreate(TableBase):
    pass

class TableUpdate(TableBase):
    is_available: Optional[bool] = None

class Table(TableBase):
    id: int
    is_available: bool

    class Config:
        orm_mode = True