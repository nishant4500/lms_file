from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_instructor_token():
    client.post("/register", json={
        "email": "inst_resource@gmail.com",
        "password": "123456",
        "name": "inst_resource",
        "role": "instructor"
    })

    res = client.post("/login", json={
        "email": "inst_resource@gmail.com",
        "password": "123456"
    })
    return res.json()["access_token"]


def test_create_and_list_resource():
    token = get_instructor_token()

    create_course = client.post(
        "/courses",
        json={"title": "Science Course", "description": "Introduction to science module content"},
        headers={"Authorization": f"Bearer {token}"}
    )
    course_id = create_course.json()["id"]

    create_module = client.post(
        "/modules",
        json={
            "title": "Module A",
            "content": "Module content for science course",
            "course_id": course_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    module_id = create_module.json()["id"]

    create_resource = client.post(
        "/resources",
        json={
            "title": "Video 1",
            "url": "https://example.com/video-1",
            "resource_type": "video",
            "module_id": module_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_resource.status_code == 200

    list_resources = client.get(f"/modules/{module_id}/resources")
    assert list_resources.status_code == 200
    assert len(list_resources.json()) >= 1
