from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    party_size = Column(Integer, nullable=False)
    reservation_time = Column(DateTime, nullable=False)
    status = Column(String, default='pending')  # e.g., pending, confirmed, canceled

    customer = relationship("Customer", back_populates="reservations")
    table = relationship("Table", back_populates="reservations")