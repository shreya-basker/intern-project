import pytest
from sqlalchemy import select

from app.models import User


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


async def update_user_role(
    client,
    token,
    user_id,
    role,
):
    response = await client.patch(
        f"/admin/users/{user_id}/role",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "role": role,
        },
    )

    return response


async def create_project(
    client,
    token,
    name="Test Project",
    description="First Project",
):
    response = await client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": name,
            "description": description,
        },
    )

    return response


async def get_users(
    client,
    token,
):
    response = await client.get(
        "/admin/users",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    return response


async def get_audit_logs(
    client,
    token,
):
    response = await client.get(
        "/admin/audit_logs",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    return response


async def get_all_projects(
    client,
    token,
):
    response = await client.get(
        "/admin/projects",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    return response


@pytest.mark.asyncio
async def test_admin_can_list_users(
    client,
    db_session,
):
    # Create admin
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

    # Create another user
    await create_user_and_get_token(
        client,
        "user@test.com",
        "User",
    )

    await set_role(
        db_session,
        "user@test.com",
        "viewer",
    )

    response = await get_users(
        client,
        admin_token,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    emails = [user["email"] for user in data]

    assert "admin@test.com" in emails
    assert "user@test.com" in emails


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(
    client,
    db_session,
):
    # Create user
    token = await create_user_and_get_token(
        client,
        "user@test.com",
        "User",
    )

    await set_role(
        db_session,
        "user@test.com",
        "editor",
    )

    response = await get_users(
        client,
        token,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_user_role(
    client,
    db_session,
):
    # Create admin
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

    # Create normal user
    await create_user_and_get_token(
        client,
        "user@test.com",
        "User",
    )

    await set_role(
        db_session,
        "user@test.com",
        "viewer",
    )

    response = await update_user_role(
        client,
        admin_token,
        user_id=2,
        role="editor",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 2
    assert data["email"] == "user@test.com"
    assert data["role"] == "editor"


@pytest.mark.asyncio
async def test_admin_can_view_audit_logs(
    client,
    db_session,
):
    # Create admin
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

    response = await get_audit_logs(
        client,
        admin_token,
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_non_admin_cannot_view_audit_logs(
    client,
    db_session,
):
    # Create editor
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

    response = await get_audit_logs(
        client,
        token,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_view_all_projects(
    client,
    db_session,
):
    # Create admin
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

    # Create owner
    owner_token = await create_user_and_get_token(
        client,
        "owner@test.com",
        "Owner",
    )

    await set_role(
        db_session,
        "owner@test.com",
        "editor",
    )

    # Create project
    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    response = await get_all_projects(
        client,
        admin_token,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Test Project"
    assert data[0]["owner_id"] == 2
    assert data[0]["is_archived"] is False
