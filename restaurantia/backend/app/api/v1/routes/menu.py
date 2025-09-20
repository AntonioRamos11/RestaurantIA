from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItem
from backend.app.db.models.menu_item import MenuItem as MenuItemModel
from backend.app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=MenuItem)
def create_menu_item(menu_item: MenuItemCreate, db: Session = next(get_db())):
    db_menu_item = MenuItemModel(**menu_item.dict())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@router.get("/{item_id}", response_model=MenuItem)
def read_menu_item(item_id: int, db: Session = next(get_db())):
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return db_menu_item

@router.put("/{item_id}", response_model=MenuItem)
def update_menu_item(item_id: int, menu_item: MenuItemUpdate, db: Session = next(get_db())):
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for key, value in menu_item.dict(exclude_unset=True).items():
        setattr(db_menu_item, key, value)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

@router.delete("/{item_id}", response_model=MenuItem)
def delete_menu_item(item_id: int, db: Session = next(get_db())):
    db_menu_item = db.query(MenuItemModel).filter(MenuItemModel.id == item_id).first()
    if db_menu_item is None:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(db_menu_item)
    db.commit()
    return db_menu_item