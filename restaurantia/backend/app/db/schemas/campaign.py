from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    discount_percentage: Optional[float] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int

    class Config:
        orm_mode = True