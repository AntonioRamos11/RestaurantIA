from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    table_id = Column(Integer, ForeignKey('tables.id'), nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String, default='pending')  # e.g., pending, completed, canceled
    created_at = Column(String)  # Consider using DateTime for actual timestamps

    customer = relationship("Customer", back_populates="orders")
    table = relationship("Table", back_populates="orders")