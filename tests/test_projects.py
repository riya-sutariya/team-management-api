from app.models import User
from app.security import hash_password


def test_user_cannot_create_project(
    client,
    create_user,
    get_token
):
    create_user(
        "Normal User",
        "user@example.com"
    )

    token = get_token(
        "user@example.com",
        "password123"
    )

    response = client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Project",
            "description": "Testing RBAC"
        }
    )

    assert response.status_code == 403


def test_admin_can_create_project(
    client,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "admin@example.com",
        role="ADMIN"
    )

    token = get_token(
        "admin@example.com",
        "password123"
    )

    response = client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Admin Project",
            "description": "Created by admin"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Admin Project"
    assert data["created_by"] == admin.id


def test_project_crud(
    client,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "admin@example.com",
        role="ADMIN"
    )

    token = get_token(
        "admin@example.com",
        "password123"
    )

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # CREATE
    response = client.post(
        "/projects/",
        headers=headers,
        json={
            "name": "Website",
            "description": "Company website"
        }
    )

    assert response.status_code == 200

    project_id = response.json()["id"]

    # GET ALL
    response = client.get(
        "/projects/",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    # GET ONE
    response = client.get(
        f"/projects/{project_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Website"

    # UPDATE
    response = client.put(
        f"/projects/{project_id}",
        headers=headers,
        json={
            "name": "Updated Website",
            "description": "Updated description"
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Website"

    # DELETE
    response = client.delete(
        f"/projects/{project_id}",
        headers=headers
    )

    assert response.status_code == 200


def test_project_not_found(
    client,
    create_user,
    get_token
):
    create_user(
        "Admin",
        "admin@example.com",
        role="ADMIN"
    )

    token = get_token(
        "admin@example.com",
        "password123"
    )

    response = client.get(
        "/projects/9999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404