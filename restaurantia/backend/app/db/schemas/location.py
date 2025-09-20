from pydantic import BaseModel

class LocationBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str

class LocationCreate(LocationBase):
    pass

class LocationUpdate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        orm_mode = True