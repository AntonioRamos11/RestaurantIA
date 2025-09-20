from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_reservation():
    response = client.post("/reservations", json={
        "party_size": 4,
        "table_id": 1,
        "time": "2023-10-01T19:00:00",
        "status": "confirmed"
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_availability():
    response = client.get("/availability?time=2023-10-01T19:00:00&party_size=4")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_reservation():
    reservation_id = 1  # Assuming this ID exists
    response = client.get(f"/reservations/{reservation_id}")
    assert response.status_code == 200
    assert "party_size" in response.json()