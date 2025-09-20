from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime = datetime.now()

class CustomerCreate(CustomerBase):
    password: str

class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True