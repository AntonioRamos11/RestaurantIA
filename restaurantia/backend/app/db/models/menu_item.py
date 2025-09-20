from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from ..base import Base

class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, index=True)
    allergens = Column(String, nullable=True)

    # Relationships
    orders = relationship("Order", back_populates="menu_item")

    def __repr__(self):
        return f"<MenuItem(id={self.id}, name={self.name}, price={self.price})>"