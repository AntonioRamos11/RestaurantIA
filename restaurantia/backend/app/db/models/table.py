from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    seats = Column(Integer, nullable=False)
    location_id = Column(Integer, ForeignKey('locations.id'))

    location = relationship("Location", back_populates="tables")

    def __repr__(self):
        return f"<Table(number={self.number}, seats={self.seats})>"