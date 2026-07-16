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


async def add_project_member(
    client,
    token,
    project_id,
    user_id,
):
    response = await client.post(
        f"/projects/{project_id}/members",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "user_id": user_id,
        },
    )

    return response


async def create_task(
    client,
    token,
    project_id=1,
    assignee_id=1,
    title="Test Task",
    description="Test Description",
):
    response = await client.post(
        f"/projects/{project_id}/tasks",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": title,
            "description": description,
            "assignee_id": assignee_id,
            "priority": "low",
            "due_date": None,
        },
    )

    return response


async def create_project_and_owner(
    client,
    db_session,
):
    token = await create_user_and_get_token(
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
        token,
    )

    assert response.status_code == 200

    return token


async def create_comment(
    client,
    token,
    task_id=1,
    body="Test comment",
):
    response = await client.post(
        f"/tasks/{task_id}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "body": body,
        },
    )

    return response


@pytest.mark.asyncio
async def test_project_member_can_post_comment(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create member
    member_token = await create_user_and_get_token(
        client,
        "member@test.com",
        "Member",
    )

    await set_role(
        db_session,
        "member@test.com",
        "editor",
    )

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Member posts a comment
    response = await create_comment(
        client,
        member_token,
        task_id=1,
        body="Looks good!",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["body"] == "Looks good!"
    assert data["author_name"] == "Member"


@pytest.mark.asyncio
async def test_non_project_member_cannot_post_comment(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create project member
    await create_user_and_get_token(
        client,
        "member@test.com",
        "Member",
    )

    await set_role(
        db_session,
        "member@test.com",
        "editor",
    )

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Create outsider
    outsider_token = await create_user_and_get_token(
        client,
        "outsider@test.com",
        "Outsider",
    )

    await set_role(
        db_session,
        "outsider@test.com",
        "editor",
    )

    # Outsider tries to comment
    response = await create_comment(
        client,
        outsider_token,
        task_id=1,
        body="I should not be able to comment",
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not a project member"


@pytest.mark.asyncio
async def test_post_comment_to_nonexistent_task_returns_404(
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

    response = await create_comment(
        client,
        token,
        task_id=999,
        body="This should fail",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "task not found"


@pytest.mark.asyncio
async def test_project_member_can_view_comments(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create member
    member_token = await create_user_and_get_token(
        client,
        "member@test.com",
        "Member",
    )

    await set_role(
        db_session,
        "member@test.com",
        "editor",
    )

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Create comment
    response = await create_comment(
        client,
        member_token,
        task_id=1,
        body="First comment",
    )

    assert response.status_code == 200

    # Member views comments
    response = await client.get(
        "/tasks/1/comments",
        headers={
            "Authorization": f"Bearer {member_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["body"] == "First comment"
    assert data[0]["author_name"] == "Member"


@pytest.mark.asyncio
async def test_non_project_member_cannot_view_comments(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create project member
    member_token = await create_user_and_get_token(
        client,
        "member@test.com",
        "Member",
    )

    await set_role(
        db_session,
        "member@test.com",
        "editor",
    )

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Create comment
    response = await create_comment(
        client,
        member_token,
        task_id=1,
        body="First comment",
    )

    assert response.status_code == 200

    # Create outsider
    outsider_token = await create_user_and_get_token(
        client,
        "outsider@test.com",
        "Outsider",
    )

    await set_role(
        db_session,
        "outsider@test.com",
        "editor",
    )

    # Outsider tries to view comments
    response = await client.get(
        "/tasks/1/comments",
        headers={
            "Authorization": f"Bearer {outsider_token}",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not a project member"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,email,name,user_id",
    [
        ("editor", "member@test.com", "Member", 2),
        ("admin", "admin@test.com", "Admin", 3),
    ],
)
async def test_comment_author_and_admin_can_delete_comment(
    client,
    db_session,
    role,
    email,
    name,
    user_id,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create member (comment author)
    member_token = await create_user_and_get_token(
        client,
        "member@test.com",
        "Member",
    )

    await set_role(
        db_session,
        "member@test.com",
        "editor",
    )

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Member creates comment
    response = await create_comment(
        client,
        member_token,
        task_id=1,
        body="Delete me",
    )

    assert response.status_code == 200

    if role == "admin":
        token = await create_user_and_get_token(
            client,
            email,
            name,
        )

        await set_role(
            db_session,
            email,
            role,
        )
    else:
        token = member_token

    response = await client.delete(
        "/comments/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"
    assert response.json()["comment_id"] == 1


@pytest.mark.asyncio
async def test_other_member_cannot_delete_comment(
    client,
    db_session,
):
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

    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create comment author
    author_token = await create_user_and_get_token(
        client,
        "author@test.com",
        "Author",
    )

    await set_role(
        db_session,
        "author@test.com",
        "editor",
    )

    # Create another member
    other_token = await create_user_and_get_token(
        client,
        "other@test.com",
        "Other",
    )

    await set_role(
        db_session,
        "other@test.com",
        "editor",
    )

    # Add both members
    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=3,
    )

    assert response.status_code == 200

    # Create task
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Author creates comment
    response = await create_comment(
        client,
        author_token,
        task_id=1,
        body="My comment",
    )

    assert response.status_code == 200

    # Other member attempts to delete it
    response = await client.delete(
        "/comments/1",
        headers={
            "Authorization": f"Bearer {other_token}",
        },
    )

    assert response.status_code == 403
