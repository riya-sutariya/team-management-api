def test_register(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["role"] == "USER"


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "name": "Wrong Password",
            "email": "wrong@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401

def test_get_current_user(client):
    # Register
    client.post(
        "/auth/register",
        json={
            "name": "Current User",
            "email": "current@example.com",
            "password": "password123"
        }
    )

    # Login
    login_response = client.post(
        "/auth/login",
        json={
            "email": "current@example.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    # Call protected endpoint
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Current User"
    assert data["email"] == "current@example.com"
    assert data["role"] == "USER"

def test_get_current_user_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401

def test_get_current_user_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401

def test_refresh_token(client):
    client.post(
        "/auth/register",
        json={
            "name": "Refresh User",
            "email": "refresh@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_refresh_token_rotation(client):
    client.post(
        "/auth/register",
        json={
            "name": "Rotation User",
            "email": "rotation@example.com",
            "password": "password123"
        }
    )

    login_response = client.post(
        "/auth/login",
        json={
            "email": "rotation@example.com",
            "password": "password123"
        }
    )

    assert login_response.status_code == 200

    old_refresh_token = (
        login_response.json()["refresh_token"]
    )

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data

    new_refresh_token = data["refresh_token"]

    assert new_refresh_token != old_refresh_token

    # Old refresh token must no longer work.
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert response.status_code == 401

def test_invalid_refresh_token(client):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "completely-invalid-token"
        }
    )

    assert response.status_code == 401