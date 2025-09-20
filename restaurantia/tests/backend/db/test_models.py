from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from backend.app.db.models.reservation import Reservation
from backend.app.db.session import get_db

@pytest.fixture(scope='module')
def test_db():
    # Setup the database for testing
    engine = create_engine('postgresql://user:password@localhost/test_db')
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create the database tables
    Reservation.metadata.create_all(bind=engine)

    yield TestingSessionLocal

    # Teardown the database after tests
    Reservation.metadata.drop_all(bind=engine)

@pytest.fixture
def db(test_db):
    # Create a new session for each test
    session = test_db()
    yield session
    session.close()

def test_create_reservation(db):
    new_reservation = Reservation(customer_id=1, table_id=1, party_size=4, reservation_time='2023-10-01 19:00:00')
    db.add(new_reservation)
    db.commit()
    assert new_reservation.id is not None

def test_read_reservation(db):
    reservation = db.query(Reservation).filter(Reservation.id == 1).first()
    assert reservation is not None
    assert reservation.party_size == 4

def test_update_reservation(db):
    reservation = db.query(Reservation).filter(Reservation.id == 1).first()
    reservation.party_size = 5
    db.commit()
    updated_reservation = db.query(Reservation).filter(Reservation.id == 1).first()
    assert updated_reservation.party_size == 5

def test_delete_reservation(db):
    reservation = db.query(Reservation).filter(Reservation.id == 1).first()
    db.delete(reservation)
    db.commit()
    deleted_reservation = db.query(Reservation).filter(Reservation.id == 1).first()
    assert deleted_reservation is None