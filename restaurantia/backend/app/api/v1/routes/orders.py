from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.schemas.order import OrderCreate, OrderRead
from backend.app.db.models.order import Order
from backend.app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=OrderRead)
def create_order(order: OrderCreate, db: Session = next(get_db())):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/{order_id}", response_model=OrderRead)
def read_order(order_id: int, db: Session = next(get_db())):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@router.get("/", response_model=list[OrderRead])
def read_orders(skip: int = 0, limit: int = 10, db: Session = next(get_db())):
    orders = db.query(Order).offset(skip).limit(limit).all()
    return orders