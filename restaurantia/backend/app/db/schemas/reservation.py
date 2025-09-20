from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReservationBase(BaseModel):
    party_size: int
    table_id: int
    reservation_time: datetime
    customer_id: Optional[int] = None

class ReservationCreate(ReservationBase):
    pass

class Reservation(ReservationBase):
    id: int

    class Config:
        orm_mode = True