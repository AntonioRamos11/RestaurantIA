from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.base import Base

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    loyalty_points = Column(Integer, default=0)

    reservations = relationship("Reservation", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, email={self.email})>"