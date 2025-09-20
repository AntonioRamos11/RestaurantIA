from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.customer import Customer
from app.db.models.reservation import Reservation
from app.db.schemas.reservation import ReservationCreate, ReservationUpdate

def get_current_customer(customer_id: int, db: Session = Depends(get_db)) -> Customer:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)) -> Reservation:
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def update_reservation(reservation_id: int, reservation: ReservationUpdate, db: Session = Depends(get_db)) -> Reservation:
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for key, value in reservation.dict(exclude_unset=True).items():
        setattr(db_reservation, key, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

def delete_reservation(reservation_id: int, db: Session = Depends(get_db)) -> None:
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(db_reservation)
    db.commit()