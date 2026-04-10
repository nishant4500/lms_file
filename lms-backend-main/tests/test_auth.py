from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

def test_register_success():
    email = f"test_{uuid.uuid4()}@gmail.com"

    response = client.post("/register", json={
        "email": email,
        "password": "1234",
        "name": "test",
        "role": "student"
    })

    assert response.status_code == 200

def test_register_empty_email():
    response = client.post("/register", json={
        "email": "",
        "password": "1234",
        "name": "test",
        "role": "student"
    })
    assert response.status_code == 400

def test_login_success():
    client.post("/register", json={
        "email": "login@gmail.com",
        "password": "1234",
        "name": "test",
        "role": "student"
    })

    response = client.post("/login", json={
        "email": "login@gmail.com",
        "password": "1234"
    })
    assert response.status_code == 200