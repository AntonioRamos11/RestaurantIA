from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.schemas.reservation import ReservationCreate, ReservationRead
from app.db.models.reservation import Reservation
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=ReservationRead)
def create_reservation(reservation: ReservationCreate, db: Session = next(get_db())):
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.get("/{id}", response_model=ReservationRead)
def get_reservation(id: int, db: Session = next(get_db())):
    reservation = db.query(Reservation).filter(Reservation.id == id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.get("/availability")
def check_availability(time: str, party_size: int, db: Session = next(get_db())):
    # Logic to check availability based on time and party size
    # This is a placeholder for actual availability logic
    return {"available": True}  # Replace with actual availability check logic