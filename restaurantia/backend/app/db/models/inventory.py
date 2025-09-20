from sqlalchemy import Column, Integer, String, Float
from backend.app.db.base import Base

class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity_on_hand = Column(Integer, default=0)
    cost_per_unit = Column(Float, nullable=False)
    supplier = Column(String, index=True)
    last_updated = Column(String)  # Consider using a DateTime type for better handling of dates

    def __repr__(self):
        return f"<Inventory(id={self.id}, item_name='{self.item_name}', quantity_on_hand={self.quantity_on_hand}, cost_per_unit={self.cost_per_unit}, supplier='{self.supplier}')>"