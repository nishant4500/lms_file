from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():
    # register instructor
    client.post("/register", json={
        "email": "course@gmail.com",
        "password": "1234",
        "name": "inst",
        "role": "instructor"
    })

    # login
    response = client.post("/login", json={
        "email": "course@gmail.com",
        "password": "1234"
    })
    return response.json()["access_token"]


def test_create_course_success():
    token = get_token()

    response = client.post(
        "/courses",
        json={"title": "Math", "description": "Algebra"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_create_course_empty_title():
    token = get_token()

    response = client.post(
        "/courses",
        json={"title": "", "description": "Test"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


def test_create_course_student_forbidden():
    # register student
    client.post("/register", json={
        "email": "student@gmail.com",
        "password": "1234",
        "name": "stud",
        "role": "student"
    })

    # login
    res = client.post("/login", json={
        "email": "student@gmail.com",
        "password": "1234"
    })
    token = res.json()["access_token"]

    response = client.post(
        "/courses",
        json={"title": "Math", "description": "Algebra"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403