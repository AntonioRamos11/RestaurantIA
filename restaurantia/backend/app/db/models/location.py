from sqlalchemy import Column, Integer, String
from backend.app.db.base import Base

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, address={self.address}, city={self.city}, state={self.state}, zip_code={self.zip_code}, country={self.country})>"