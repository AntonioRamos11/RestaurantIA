from pydantic import BaseModel
from typing import Optional

class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    unit: str
    cost_per_unit: float
    supplier: Optional[str] = None
    reorder_level: Optional[int] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryUpdate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int

    class Config:
        orm_mode = True