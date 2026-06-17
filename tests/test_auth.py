import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "name": "Duplicate User",
        "email": "dup@example.com",
        "password": "secret123",
    }

    await client.post("/auth/register", json=payload)

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "secret123",
        },
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "login@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(
        "/auth/register",
        json={
            "name": "Wrong Password User",
            "email": "wrong@example.com",
            "password": "secret123",
        },
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_me_requires_token(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_read_me_with_token(client):
    await client.post(
        "/auth/register",
        json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "secret123",
        },
    )

    login_response = await client.post(
        "/auth/login",
        data={
            "username": "me@example.com",
            "password": "secret123",
        },
    )

    token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
