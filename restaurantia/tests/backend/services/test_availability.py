import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_availability():
    response = client.get("/api/v1/availability?date=2023-10-01&time=19:00&party_size=4")
    assert response.status_code == 200
    assert "available_tables" in response.json()

def test_get_availability_no_results():
    response = client.get("/api/v1/availability?date=2023-10-01&time=19:00&party_size=20")
    assert response.status_code == 200
    assert response.json() == {"available_tables": []}

def test_create_reservation():
    reservation_data = {
        "name": "John Doe",
        "party_size": 4,
        "date": "2023-10-01",
        "time": "19:00",
        "contact_info": "john@example.com"
    }
    response = client.post("/api/v1/reservations", json=reservation_data)
    assert response.status_code == 201
    assert "reservation_id" in response.json()

def test_create_reservation_invalid_data():
    reservation_data = {
        "name": "",
        "party_size": 0,
        "date": "2023-10-01",
        "time": "19:00",
        "contact_info": "john@example.com"
    }
    response = client.post("/api/v1/reservations", json=reservation_data)
    assert response.status_code == 422  # Unprocessable Entity for validation errors

def test_get_reservation():
    reservation_id = 1  # Assuming this ID exists
    response = client.get(f"/api/v1/reservations/{reservation_id}")
    assert response.status_code == 200
    assert "name" in response.json()  # Check if the reservation details are returned

def test_get_reservation_not_found():
    response = client.get("/api/v1/reservations/9999")  # Assuming this ID does not exist
    assert response.status_code == 404  # Not Found for non-existing reservation