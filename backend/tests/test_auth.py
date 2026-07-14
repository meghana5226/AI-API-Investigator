def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={
        "email": "alice@example.com", "full_name": "Alice Doe", "password": "SecurePass123!",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_email_fails(client, registered_user):
    response = client.post("/api/v1/auth/register", json=registered_user)
    assert response.status_code == 400


def test_login_success(client, registered_user):
    response = client.post("/api/v1/auth/login", data={
        "username": registered_user["email"], "password": registered_user["password"],
    })
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password_fails(client, registered_user):
    response = client.post("/api/v1/auth/login", data={
        "username": registered_user["email"], "password": "wrong-password",
    })
    assert response.status_code == 401


def test_get_me_requires_auth(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_get_me_with_valid_token(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_token_refresh_flow(client, registered_user):
    login = client.post("/api/v1/auth/login", data={
        "username": registered_user["email"], "password": registered_user["password"],
    })
    refresh_token = login.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
