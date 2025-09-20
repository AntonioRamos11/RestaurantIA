from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.schemas.inventory import InventoryCreate, InventoryUpdate, Inventory
from app.db.models.inventory import Inventory as InventoryModel
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=Inventory)
def create_inventory_item(item: InventoryCreate, db: Session = next(get_db())):
    db_item = InventoryModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/{item_id}", response_model=Inventory)
def read_inventory_item(item_id: int, db: Session = next(get_db())):
    db_item = db.query(InventoryModel).filter(InventoryModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@router.put("/{item_id}", response_model=Inventory)
def update_inventory_item(item_id: int, item: InventoryUpdate, db: Session = next(get_db())):
    db_item = db.query(InventoryModel).filter(InventoryModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}", response_model=Inventory)
def delete_inventory_item(item_id: int, db: Session = next(get_db())):
    db_item = db.query(InventoryModel).filter(InventoryModel.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return db_item