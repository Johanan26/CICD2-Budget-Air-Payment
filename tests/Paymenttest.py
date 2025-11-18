import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.Paymentmodels import Base

TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_payment():
    payload = {
        "amount" : "12.50",
        "currency" : "EUR",
        "description" : "Test payment",
        "user_id" : "user1",
        "order_id" : "order1",
        "provider" : "INTERNAL",
        "provider_payment_id" : "None"
    }

    response = client.post("/payments", json=payload)
    assert response.status_code == 201

    data= response.json()
    assert data["amount"] == 12.50
    assert data["currency"] == "EUR"
    assert data["status"] == "pending"
    assert "id" in data

def test_get_payment():
    p = client.post("/payments", json={
       "amount" : "5.00",
        "currency" : "EUR",
        "description" : "Fetch test",
        "user_id" : "",
        "order_id" : "",
        "provider" : "INTERNAL",
        "provider_payment_id" : "None" 
    }).json()

    response = client.get(f"/payments/{p['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == p["id"]
    assert data["amount"] == 5.0

def test_update_payment_status():
    p = client.post("/payments", json={
    "amount" : "9.99",
    "currency" : "EUR",
    "description" : "status test",
    "user_id" : "",
    "order_id" : "",
    "provider" : "INTERNAL",
    "provider_payment_id" : "None" 
    }).json()

    response = client.patch(f"/payments/{p['id']}/status",json={
        "status": "success",
        "failure_reason": None
    })

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

def test_list_payment():
    response = client.get("/payments")
    assert response.status_code == 200
    assert isinstance(response.json().list)
    assert len(response.json()) >= 1
      
