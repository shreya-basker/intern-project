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


@pytest.mark.asyncio
async def test_viewer_cannot_create_task(
    client,
    db_session,
):
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

    create_response = await create_project(
        client,
        editor_token,
    )
    assert create_response.status_code == 200

    # Create viewer
    viewer_token = await create_user_and_get_token(
        client,
        "viewer@test.com",
        "Viewer",
    )
    await set_role(
        db_session,
        "viewer@test.com",
        "viewer",
    )

    # Add viewer to the project
    add_response = await add_project_member(
        client,
        editor_token,
        project_id=1,
        user_id=2,
    )
    assert add_response.status_code == 200

    # Viewer tries to create a task
    response = await create_task(
        client,
        viewer_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,email",
    [
        ("editor", "editor@test.com"),
        ("admin", "admin@test.com"),
    ],
)
async def test_editor_and_admin_can_create_task(
    client,
    db_session,
    role,
    email,
):
    token = await create_user_and_get_token(
        client,
        email,
        role,
    )

    await set_role(
        db_session,
        email,
        role,
    )

    create_project_response = await create_project(
        client,
        token,
    )

    assert create_project_response.status_code == 200

    response = await create_task(
        client,
        token,
        project_id=1,
        assignee_id=1,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["project_id"] == 1
    assert data["assignee_id"] == 1


@pytest.mark.asyncio
async def test_member_sees_only_their_assigned_tasks(
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

    # Create project
    response = await create_project(
        client,
        owner_token,
    )

    assert response.status_code == 200

    # Create member 1
    member1_token = await create_user_and_get_token(
        client,
        "member1@test.com",
        "Member 1",
    )

    await set_role(
        db_session,
        "member1@test.com",
        "editor",
    )

    # Add both members to the project
    await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=3,
    )

    # Task assigned to member1
    await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
        title="Task One",
    )

    # Task assigned to member2
    await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=3,
        title="Task Two",
    )

    # Member1 should only see their own task
    response = await client.get(
        "/projects/1/tasks",
        headers={
            "Authorization": f"Bearer {member1_token}",
        },
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task One"
    assert tasks[0]["assignee_id"] == 2


@pytest.mark.asyncio
async def test_admin_can_see_all_tasks(
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

    create_response = await create_project(
        client,
        owner_token,
    )

    assert create_response.status_code == 200

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

    # Create member 1
    await create_user_and_get_token(
        client,
        "member1@test.com",
        "Member 1",
    )

    await set_role(
        db_session,
        "member1@test.com",
        "editor",
    )

    # Create member 2
    await create_user_and_get_token(
        client,
        "member2@test.com",
        "Member 2",
    )

    await set_role(
        db_session,
        "member2@test.com",
        "editor",
    )

    # Add members
    await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=3,
    )

    await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=4,
    )

    # Create two tasks
    await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=3,
        title="Task One",
    )

    await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=4,
        title="Task Two",
    )

    # Admin lists tasks
    response = await client.get(
        "/projects/1/tasks",
        headers={
            "Authorization": f"Bearer {admin_token}",
        },
    )

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_assigned_member_can_view_task_details(
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

    # Add member to project
    response = await add_project_member(
        client,
        owner_token,
        project_id=1,
        user_id=2,
    )

    assert response.status_code == 200

    # Create task assigned to member
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Assigned member views task details
    response = await client.get(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {member_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"]["id"] == 1
    assert data["task"]["assignee_id"] == 2
    assert data["task"]["title"] == "Test Task"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,email,name,user_id",
    [
        ("editor", "owner@test.com", "Owner", 1),
        ("admin", "admin@test.com", "Admin", 2),
    ],
)
async def test_owner_and_admin_can_view_task_details(
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

    # Create admin only for the second case
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
        token = owner_token

    # Create member
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
        user_id=3 if role == "admin" else 2,
    )

    assert response.status_code == 200

    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=3 if role == "admin" else 2,
    )

    assert response.status_code == 200

    response = await client.get(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task"]["id"] == 1


@pytest.mark.asyncio
async def test_project_owner_can_update_task_status(
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

    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Owner updates task status
    response = await client.put(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {owner_token}",
        },
        json={
            "status": "in_progress",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_other_member_cannot_update_task_status(
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

    # Create assignee
    await create_user_and_get_token(
        client,
        "member1@test.com",
        "Member 1",
    )

    await set_role(
        db_session,
        "member1@test.com",
        "editor",
    )

    # Create another member
    member2_token = await create_user_and_get_token(
        client,
        "member2@test.com",
        "Member 2",
    )

    await set_role(
        db_session,
        "member2@test.com",
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

    # Create task assigned to member1
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Member2 tries to update it
    response = await client.put(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {member2_token}",
        },
        json={
            "status": "done",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role,email,name,user_id",
    [
        ("editor", "owner@test.com", "Owner", 1),
        ("admin", "admin@test.com", "Admin", 2),
    ],
)
async def test_owner_and_admin_can_delete_task(
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

    # Create admin only for admin case
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
        token = owner_token

    # Create member
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
        user_id=3 if role == "admin" else 2,
    )

    assert response.status_code == 200

    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=3 if role == "admin" else 2,
    )

    assert response.status_code == 200

    response = await client.delete(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"
    assert response.json()["task_id"] == 1


@pytest.mark.asyncio
async def test_other_member_cannot_delete_task(
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

    # Create member 1 (assignee)
    await create_user_and_get_token(
        client,
        "member1@test.com",
        "Member 1",
    )

    await set_role(
        db_session,
        "member1@test.com",
        "editor",
    )

    # Create member 2 (will attempt delete)
    member2_token = await create_user_and_get_token(
        client,
        "member2@test.com",
        "Member 2",
    )

    await set_role(
        db_session,
        "member2@test.com",
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

    # Owner creates task assigned to member1
    response = await create_task(
        client,
        owner_token,
        project_id=1,
        assignee_id=2,
    )

    assert response.status_code == 200

    # Member2 attempts to delete
    response = await client.delete(
        "/tasks/1",
        headers={
            "Authorization": f"Bearer {member2_token}",
        },
    )

    assert response.status_code == 403
