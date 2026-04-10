from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_instructor_token():
    client.post("/register", json={
        "email": "inst_test@gmail.com",
        "password": "1234",
        "name": "inst",
        "role": "instructor"
    })

    res = client.post("/login", json={
        "email": "inst_test@gmail.com",
        "password": "1234"
    })
    return res.json()["access_token"]


def get_student_token():
    client.post("/register", json={
        "email": "stud_test@gmail.com",
        "password": "1234",
        "name": "stud",
        "role": "student"
    })

    res = client.post("/login", json={
        "email": "stud_test@gmail.com",
        "password": "1234"
    })
    return res.json()["access_token"]

def test_enroll_course():
    instructor_token = get_instructor_token()

    # create course
    res = client.post(
        "/courses",
        json={"title": "Math", "description": "Algebra"},
        headers={"Authorization": f"Bearer {instructor_token}"}
    )
    course_id = res.json()["id"]

    student_token = get_student_token()

    response = client.post(
        f"/courses/{course_id}/enroll",
        headers={"Authorization": f"Bearer {student_token}"}
    )

    assert response.status_code == 200