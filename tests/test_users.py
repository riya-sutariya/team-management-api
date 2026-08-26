def test_admin_can_list_users(
    client,
    create_user,
    get_token
):
    create_user(
        "Admin",
        "usersadmin@example.com",
        role="ADMIN"
    )

    create_user(
        "Riya",
        "usersriya@example.com"
    )

    token = get_token(
        "usersadmin@example.com",
        "password123"
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2


def test_user_cannot_list_users(
    client,
    create_user,
    get_token
):
    create_user(
        "Normal User",
        "normal@example.com"
    )

    token = get_token(
        "normal@example.com",
        "password123"
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403


def test_admin_can_change_user_role(
    client,
    create_user,
    get_token
):
    create_user(
        "Admin",
        "roleadmin@example.com",
        role="ADMIN"
    )

    user = create_user(
        "Riya",
        "roleuser@example.com"
    )

    token = get_token(
        "roleadmin@example.com",
        "password123"
    )

    response = client.put(
        f"/users/{user.id}/role",
        params={
            "role": "MANAGER"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["role"] == "MANAGER"


def test_admin_can_delete_user(
    client,
    create_user,
    get_token
):
    create_user(
        "Admin",
        "deleteadmin@example.com",
        role="ADMIN"
    )

    user = create_user(
        "Delete Me",
        "delete@example.com"
    )

    token = get_token(
        "deleteadmin@example.com",
        "password123"
    )

    response = client.delete(
        f"/users/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    response = client.get(
        f"/users/{user.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404


def test_admin_cannot_delete_self(
    client,
    create_user,
    get_token
):
    admin = create_user(
        "Admin",
        "selfadmin@example.com",
        role="ADMIN"
    )

    token = get_token(
        "selfadmin@example.com",
        "password123"
    )

    response = client.delete(
        f"/users/{admin.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 400