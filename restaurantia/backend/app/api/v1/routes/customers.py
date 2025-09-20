from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.schemas.customer import CustomerCreate, CustomerRead
from backend.app.db.models.customer import Customer
from backend.app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=CustomerRead)
def create_customer(customer: CustomerCreate, db: Session = next(get_db())):
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/{customer_id}", response_model=CustomerRead)
def read_customer(customer_id: int, db: Session = next(get_db())):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.get("/", response_model=list[CustomerRead])
def read_customers(skip: int = 0, limit: int = 10, db: Session = next(get_db())):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@router.delete("/{customer_id}", response_model=CustomerRead)
def delete_customer(customer_id: int, db: Session = next(get_db())):
    db_customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return db_customer