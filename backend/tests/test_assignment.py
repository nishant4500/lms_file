from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_instructor_token():
    client.post("/register", json={
        "email": "inst_assign@gmail.com",
        "password": "1234",
        "name": "inst",
        "role": "instructor"
    })

    res = client.post("/login", json={
        "email": "inst_assign@gmail.com",
        "password": "1234"
    })
    return res.json()["access_token"]


def test_create_assignment():
    token = get_instructor_token()

    res = client.post(
        "/courses",
        json={"title": "Math", "description": "Algebra"},
        headers={"Authorization": f"Bearer {token}"}
    )

    courses = client.get("/courses").json()
    course_id = courses[-1]["id"]

    response = client.post(
        "/assignments",
        json={
            "title": "Assignment 1",
            "description": "Test",
            "course_id": course_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200