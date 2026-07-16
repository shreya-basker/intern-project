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
async def test_viewer_cannot_create_posts(
    client,
):
    token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "viewer",
    )
    response = await client.post(
        "/posts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Post",
            "body": "Test Body",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_editor_can_create_post(
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

    response = await client.post(
        "/posts",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": "Test Post",
            "body": "Test Body",
        },
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_editor_updates_own_post(client, db_session):
    token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")
    response = await client.post(
        "/posts",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={"title": "Test title", "body": "Test body"},
    )
    assert response.status_code == 201

    post_id = response.json()["id"]
    update_response = await client.put(
        f"/posts/{post_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={"title": "Updated Title", "body": "Update Body"},
    )
    assert update_response.status_code == 200
    data = update_response.json()

    assert data["title"] == "Updated Title"
    assert data["body"] == "Update Body"


@pytest.mark.asyncio
async def test_editor_cannot_edit_another_users_post(client, db_session):
    editor1_token = await create_user_and_get_token(client, "editor1@test.com", "editor1")

    await set_role(db_session, "editor1@test.com", "editor")
    editor2_token = await create_user_and_get_token(client, "editor2@test.com", "editor2")

    await set_role(db_session, "editor2@test.com", "editor")

    create_response = await client.post(
        "/posts",
        headers={
            "Authorization": f"Bearer {editor1_token}",
        },
        json={"title": "Editor 1 title", "body": "Editor 1 body"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    update_response = await client.put(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {editor2_token}"},
        json={"title": "Edited title", "body": "edited body"},
    )
    assert update_response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_update_any_post(client, db_session):
    admin_token = await create_user_and_get_token(client, "admin@test.com", "admin")
    await set_role(db_session, "admin@test.com", "admin")
    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")

    create_response = await client.post(
        "/posts",
        headers={"Authorization": f"Bearer {editor_token}"},
        json={"title": "Editor title", "body": "Editor body"},
    )
    assert create_response.status_code == 201
    post_id = create_response.json()["id"]
    update_response = await client.put(
        f"/posts/{post_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Admin title", "body": "Admin body"},
    )
    assert update_response.status_code == 200


@pytest.mark.asyncio
async def test_editor_can_delete_own_posts(client, db_session):
    token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")
    response = await create_post(
        client,
        token,
    )
    assert response.status_code == 201
    post_id = response.json()["id"]
    delete_response = await client.delete(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_editor_cannot_delete_other_user_posts(client, db_session):
    editor1_token = await create_user_and_get_token(client, "editor1@test.com", "editor1")

    await set_role(db_session, "editor1@test.com", "editor")

    editor2_token = await create_user_and_get_token(client, "editor2@test.com", "editor2")
    await set_role(db_session, "editor2@test.com", "editor")
    response = await create_post(
        client,
        editor2_token,
    )
    assert response.status_code == 201
    post_id = response.json()["id"]
    delete_response = await client.delete(
        f"/posts/{post_id}", headers={"Authorization": f"Bearer {editor1_token}"}
    )
    assert delete_response.status_code == 403


@pytest.mark.asyncio
async def test_posts_editable_flag(client, db_session):
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
    post1_response = await create_post(
        client,
        editor1_token,
        title="Post One",
    )
    post2_response = await create_post(
        client,
        editor2_token,
        title="Post Two",
    )
    post_id_1 = post1_response.json()["id"]
    post_id_2 = post2_response.json()["id"]
    response = await client.get(
        "/posts",
        headers={"Authorization": f"Bearer {editor1_token}"},
    )
    assert response.status_code == 200
    posts = response.json()
    print("Post Response :")
    print(posts)
    post1 = next(p for p in posts if p["id"] == post_id_1)
    post2 = next(p for p in posts if p["id"] == post_id_2)
    assert post1["editable"] is True
    assert post2["editable"] is False


@pytest.mark.asyncio
async def test_viewer_can_post_comments(client, db_session):
    viewer_token = await create_user_and_get_token(client, "viewer@test.com", "viewer")
    await set_role(db_session, "viewer@test.com", "viewer")
    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")
    response = await create_post(
        client,
        editor_token,
    )
    post_id = response.json()["id"]
    comment_response = await client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"post_id": f"{post_id}", "body": "Nice post!"},
    )
    print(comment_response.status_code)
    print(comment_response.json())
    assert comment_response.status_code == 201
    data = comment_response.json()
    assert data["body"] == "Nice post!"
    assert data["post_id"] == post_id


@pytest.mark.asyncio
async def test_viewers_can_delete_their_comments(client, db_session):
    viewer_token = await create_user_and_get_token(client, "viewer@test.com", "viewer")
    await set_role(db_session, "viewer@test.com", "viewer")

    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")

    response = await create_post(client, editor_token)
    post_id = response.json()["id"]
    comment_response = await client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"post_id": f"{post_id}", "body": "Nice post!"},
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]
    delete_comment = await client.delete(
        f"/comments/{comment_id}", headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert delete_comment.status_code == 204


@pytest.mark.asyncio
async def test_viewer_cannot_delete_others_comment(client, db_session):
    viewer1_token = await create_user_and_get_token(client, "viewer1@test.com", "viewer1")
    await set_role(db_session, "viewer1@test.com", "viewer")
    viewer2_token = await create_user_and_get_token(client, "viewer2@test.com", "viewer2")
    await set_role(db_session, "viewer2@test.com", "viewer")

    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")

    response = await create_post(client, editor_token)
    post_id = response.json()["id"]
    comment_response = await client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {viewer1_token}"},
        json={"post_id": f"{post_id}", "body": "Nice post!"},
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]
    delete_comment = await client.delete(
        f"/comments/{comment_id}", headers={"Authorization": f"Bearer {viewer2_token}"}
    )
    assert delete_comment.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_delete_comments(client, db_session):
    admin_token = await create_user_and_get_token(client, "admin@test.com", "admin")
    await set_role(db_session, "admin@test.com", "admin")
    viewer_token = await create_user_and_get_token(client, "viewer@test.com", "viewer")
    await set_role(db_session, "viewer@test.com", "viewer")

    editor_token = await create_user_and_get_token(client, "editor@test.com", "editor")
    await set_role(db_session, "editor@test.com", "editor")

    response = await create_post(client, editor_token)
    post_id = response.json()["id"]
    comment_response = await client.post(
        f"/posts/{post_id}/comments",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"post_id": f"{post_id}", "body": "Nice post!"},
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]
    delete_comment = await client.delete(
        f"/comments/{comment_id}", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete_comment.status_code == 204
