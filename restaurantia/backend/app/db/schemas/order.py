from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class OrderItem(BaseModel):
    item_id: int
    quantity: int
    price: float

class OrderBase(BaseModel):
    customer_id: int
    items: List[OrderItem]
    total_amount: float
    order_time: datetime

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int

    class Config:
        orm_mode = True