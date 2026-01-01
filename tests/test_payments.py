import pytest
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.main
print("USING:", app.main.__file__)

from app.main import app as fastapi_app, get_db
from app.Paymentmodels import Base

TEST_DB_URL = "sqlite+pysqlite://"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass = StaticPool,)
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

fastapi_app.dependency_overrides[get_db] = override_get_db
client = TestClient(fastapi_app)

def test_create_payment():
    payload = {
        "amount" : "12.50",
        "currency" : "EUR",
        "description" : "Test payment",
        "user_id" : "user1",
        "order_id" : "order1",
        "provider" : "internal",
        "provider_payment_id" : "None"
    }

    response = client.post("/payments", json=payload)
    assert response.status_code == 201

    data= response.json()
    assert data["amount"] == "12.50"
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
        "provider" : "internal",
        "provider_payment_id" : "None" 
    }).json()

    response = client.get(f"/payment/{p['id']}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == p["id"]
    assert data["amount"] == "5.00"

def test_update_payment_status():
    p = client.post("/payments", json={
    "amount" : "9.99",
    "currency" : "EUR",
    "description" : "status test",
    "user_id" : "",
    "order_id" : "",
    "provider" : "internal",
    "provider_payment_id" : "None" 
    }).json()

    response = client.patch(f"/payment/{p['id']}/status",json={
        "status": "success",
        "failure_reason": None
    })

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"

def test_list_payment():
    response = client.get("/payments")
    assert response.status_code == 200
    assert isinstance(response.json(),list)
    assert len(response.json()) >= 1

def test_get_payment_404():
    response = client.get("/payment/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "payment not found"

def test_update_payment_status_404():
    response = client.patch('/payment/does-not-exist/status',json={"status": "success", "failure_reason":None})
    assert response.status_code == 404
    assert response.json()["detail"] == "Payment not found"

def test_list_payments_skip_limit():
    for amt in ["1.00", "2.00", "3.00"]:
        res = client.post("/payments", json={
            "amount": amt,
            "currency": "EUR",
            "description": f"p{amt}",
            "user_id": "user",
            "order_id": "order",
            "provider": "internal",
            "provider_payment_id": "None"
        })
        assert res.status_code == 201
      
    response = client.get("/payments?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    



