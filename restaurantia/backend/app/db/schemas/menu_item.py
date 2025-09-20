from pydantic import BaseModel
from typing import List, Optional

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tags: List[str] = []
    allergens: List[str] = []

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(MenuItemBase):
    pass

class MenuItem(MenuItemBase):
    id: int

    class Config:
        orm_mode = True