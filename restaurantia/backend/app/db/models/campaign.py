from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..base import Base

class Campaign(Base):
    __tablename__ = 'campaigns'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_date = Column(String)  # Consider using Date type for actual date handling
    end_date = Column(String)  # Consider using Date type for actual date handling
    discount_percentage = Column(Integer)

    # Relationships
    reservations = relationship("Reservation", back_populates="campaign")