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


async def create_post(
    client,
    token,
    title="Test Post",
    body="Test Body",
):
    response = await client.post(
        "/posts",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": title,
            "body": body,
        },
    )

    return response


@pytest.mark.asyncio
async def test_viewer_can_see_tags(client, db_session):
    viewer_token = await create_user_and_get_token(client, "viewer@test.com", "viewer")
    response = await client.get("/tags", headers={"Authorization": f"Bearer {viewer_token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_editor_cannot_post(client, db_session):
    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")
    response = await client.post(
        "/tags",
        headers={"Authorization": f"Bearer {editor_token}"},
        json={
            "name": "python",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_post_tags(client, db_session):
    viewer_token = await create_user_and_get_token(client, "viewer@test.com", "viewer")
    await set_role(db_session, "viewer@test.com", "viewer")

    response = await client.post(
        "/tags", headers={"Authorization": f"Bearer {viewer_token}"}, json={"name": "python"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_post(client, db_session):
    admin_token = await create_user_and_get_token(client, "admin@test.com", "admin")
    await set_role(db_session, "admin@test.com", "admin")
    response = await client.post(
        "/tags", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "python"}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_delete_tags(client, db_session):
    admin_token = await create_user_and_get_token(client, "admin@test.com", "admin")
    await set_role(db_session, "admin@test.com", "admin")

    create_response = await client.post(
        "/tags", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "python"}
    )
    print(create_response.json())
    tag_id = create_response.json()["id"]
    delete_response = await client.delete(
        f"/tags/{tag_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_editor_can_tag_own_posts(client, db_session):
    token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")
    admin_token = await create_user_and_get_token(client, "admin@test.com", "admin")
    await set_role(db_session, "admin@test.com", "admin")
    tag_response = await client.post(
        "/tags", headers={"Authorization": f"Bearer {admin_token}"}, json={"name": "python"}
    )
    tag_id = tag_response.json()["id"]
    post_response = await create_post(client, token)
    post_id = post_response.json()["id"]
    response = await client.post(
        f"/posts/{post_id}/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_editor_cannot_tag_another_users_post(
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

    editor1_token = await create_user_and_get_token(
        client,
        "editor1@test.com",
        "Editor One",
    )

    await set_role(
        db_session,
        "editor1@test.com",
        "editor",
    )

    editor2_token = await create_user_and_get_token(
        client,
        "editor2@test.com",
        "Editor Two",
    )

    await set_role(
        db_session,
        "editor2@test.com",
        "editor",
    )

    tag_response = await client.post(
        "/tags",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
        json={
            "name": "python",
        },
    )

    tag_id = tag_response.json()["id"]

    post_response = await create_post(
        client,
        editor1_token,
    )

    post_id = post_response.json()["id"]

    response = await client.post(
        f"/posts/{post_id}/tags/{tag_id}",
        headers={
            "Authorization": f"Bearer {editor2_token}",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_tag_any_post(
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

    tag_response = await client.post(
        "/tags",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
        json={
            "name": "python",
        },
    )

    assert tag_response.status_code == 201

    tag_id = tag_response.json()["id"]

    post_response = await create_post(
        client,
        editor_token,
    )

    post_id = post_response.json()["id"]

    response = await client.post(
        f"/posts/{post_id}/tags/{tag_id}",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )

    assert response.status_code == 200
