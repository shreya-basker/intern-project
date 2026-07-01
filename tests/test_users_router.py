import pytest
from sqlalchemy import select

from week4.app.models import User


async def create_user_and_get_token(
    client,
    email,
    name,
    password="secret123",
):
    await client.post(
        "/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )

    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    return login_response.json()["access_token"]


async def set_role(
    db_session,
    email,
    role,
):
    result = await db_session.execute(select(User).where(User.email == email))

    user = result.scalar_one()

    user.role = role

    await db_session.commit()

    return user


@pytest.mark.asyncio
async def test_admin_can_delete_user(
    client,
    db_session,
):
    admin_token = await create_user_and_get_token(
        client,
        "admin@test.com",
        "Admin",
    )

    await set_role(
        db_session,
        "admin@test.com",
        "admin",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Victim",
            "email": "victim@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "victim@test.com"))

    victim = result.scalar_one()
    print("Victim id:", victim.id)

    print("Victim email:", victim.email)

    response = await client.delete(
        f"/users/{victim.id}",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_viewer_can_get_users(client):
    token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "Viewer",
    )

    response = await client.get(
        "/users",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_viewer_can_get_user(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "Viewer",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Target",
            "email": "target@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "target@test.com"))

    target = result.scalar_one()

    response = await client.get(
        f"/users/{target.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_delete_user(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "Viewer",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Victim",
            "email": "victim@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "victim@test.com"))

    victim = result.scalar_one()

    response = await client.delete(
        f"/users/{victim.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_editor_cannot_delete_user(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )

    await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Victim",
            "email": "victim@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "victim@test.com"))

    victim = result.scalar_one()

    response = await client.delete(
        f"/users/{victim.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_editor_can_update_own_profile(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )

    editor = await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )

    response = await client.put(
        f"/users/{editor.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Updated Editor",
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_editor_cannot_update_other_profile(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )

    await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Other User",
            "email": "other@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "other@test.com"))

    other = result.scalar_one()

    response = await client.put(
        f"/users/{other.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Hacked Name",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_any_profile(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "admin@test.com",
        "Admin",
    )

    await set_role(
        db_session,
        "admin@test.com",
        "admin",
    )

    await client.post(
        "/auth/register",
        json={
            "name": "Target",
            "email": "target@test.com",
            "password": "secret123",
        },
    )

    result = await db_session.execute(select(User).where(User.email == "target@test.com"))

    target = result.scalar_one()

    response = await client.put(
        f"/users/{target.id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Updated By Admin",
        },
    )

    assert response.status_code == 200
