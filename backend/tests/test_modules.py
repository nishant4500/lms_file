from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_instructor_token():
    client.post("/register", json={
        "email": "inst_mod@gmail.com",
        "password": "1234",
        "name": "inst",
        "role": "instructor"
    })

    res = client.post("/login", json={
        "email": "inst_mod@gmail.com",
        "password": "1234"
    })
    return res.json()["access_token"]


def test_create_module():
    token = get_instructor_token()

    # create course
    res = client.post(
        "/courses",
        json={"title": "Math", "description": "Algebra"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # fetch course_id properly
    courses = client.get("/courses").json()
    course_id = courses[-1]["id"]

    # create module (IMPORTANT: include required fields)
    response = client.post(
        "/modules",
        json={
            "title": "Module 1",
            "content": "Some content",  
            "course_id": course_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200