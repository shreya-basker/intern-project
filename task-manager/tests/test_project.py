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


async def create_project(client, token, name="Test Project", description="First Project"):
    response = await client.post(
        "/projects/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": name, "description": description},
    )
    return response


@pytest.mark.asyncio
async def test_viewer_cannot_create_project(
    client,
    db_session,
):
    token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "Viewer",
    )

    await set_role(
        db_session,
        "viewer@test.com",
        "viewer",
    )

    response = await client.post(
        "/projects/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Project Alpha",
            "description": "First Project",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["editor", "admin"])
async def test_editor_and_admin_can_create_project(
    client,
    db_session,
    role,
):
    email = f"{role}@test.com"
    token = await create_user_and_get_token(
        client,
        email,
        role.capitalize(),
    )
    await set_role(
        db_session,
        email,
        role,
    )
    response = await create_project(
        client,
        token,
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Project created successfully!"


@pytest.mark.asyncio
async def test_editor_cannot_update_another_users_project(
    client,
    db_session,
):
    # Owner
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

    # Another editor
    editor_token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )
    await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )

    # Owner creates project
    create_response = await create_project(
        client,
        owner_token,
    )

    assert create_response.status_code == 200

    # Second editor tries to update it
    update_response = await client.put(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {editor_token}",
        },
        json={
            "name": "Hacked Project",
            "description": "Should not work",
        },
    )

    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_any_project(
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

    # Create editor (project owner)
    editor_token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )
    await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )
    # Editor creates the project
    create_response = await create_project(
        client,
        editor_token,
    )
    assert create_response.status_code == 200

    # Admin updates the project
    update_response = await client.put(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
        json={
            "name": "Admin Updated Project",
            "description": "Updated by Admin",
        },
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Admin Updated Project"
    assert data["description"] == "Updated by Admin"


@pytest.mark.asyncio
async def test_owner_can_archive_project(
    client,
    db_session,
):
    email = "editor@test.com"

    token = await create_user_and_get_token(
        client,
        email,
        "Editor",
    )

    await set_role(
        db_session,
        email,
        "editor",
    )

    create_response = await create_project(
        client,
        token,
    )

    assert create_response.status_code == 200

    delete_response = await client.delete(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project is archived"
    assert delete_response.json()["project_id"] == 1


@pytest.mark.asyncio
async def test_editor_cannot_archive_another_users_project(
    client,
    db_session,
):
    # Owner
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

    # Another editor
    editor_token = await create_user_and_get_token(
        client,
        "editor@test.com",
        "Editor",
    )

    await set_role(
        db_session,
        "editor@test.com",
        "editor",
    )

    # Owner creates project
    create_response = await create_project(
        client,
        owner_token,
    )

    assert create_response.status_code == 200

    # Second editor tries to archive it
    delete_response = await client.delete(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {editor_token}",
        },
    )

    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_archive_any_project(
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

    # Create project owner
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

    # Owner creates project
    create_response = await create_project(
        client,
        owner_token,
    )

    assert create_response.status_code == 200

    # Admin archives it
    delete_response = await client.delete(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Project is archived"


@pytest.mark.asyncio
async def test_owner_can_delete_project(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    response = await client.delete(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {owner_token}",
        },
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_delete_project(
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    response = await client.delete(
        "/projects/1",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )

    assert response.status_code == 200
