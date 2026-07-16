from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import assert_owner_or_admin, get_current_user
from app.models import Comment, Project, ProjectMember, Task, User
from app.schema import (
    AddTasks,
    AssignTask,
    CommentResponse,
    TaskDetailResponse,
    TaskResponse,
    TaskUpdateStatus,
)
from app.utils import create_audit_log

router = APIRouter(prefix="", tags=["tasks"])


@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_tasks(
    project_id: int,
    payload: AddTasks,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id
        )
    )
    member = membership_result.scalar_one_or_none()

    if member is None:
        raise HTTPException(
            status_code=403,
            detail="Not a project member",
        )

    if current_user.role not in ["editor", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only editors or admins can create tasks",
        )
    assignee = await db.get(User, payload.assignee_id)
    if assignee is None:
        raise HTTPException(status_code=404, detail="Assignee not found")
    task = Task(
        project_id=project_id,
        title=payload.title,
        description=payload.description,
        assignee_id=payload.assignee_id,
        created_by_id=current_user.id,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    db.add(task)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create",
        resource="task",
        resource_id=task.id,
    )
    await db.commit()
    await db.refresh(task)

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        assignee_name=assignee.name,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_at=task.created_at,
        editable=True,
    )


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def tasks_in_a_project(
    project_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[TaskResponse]:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == current_user.id
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="not a project member")
    if current_user.role == "admin" or current_user.id == project.owner_id:
        result = await db.execute(select(Task).where(Task.project_id == project_id))
    else:
        result = await db.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.assignee_id == current_user.id,
            )
        )

    tasks = result.scalars().all()

    response = []

    for task in tasks:
        assignee = await db.get(User, task.assignee_id)
        if assignee is None:
            raise HTTPException(
                status_code=404,
                detail="Assignee not found",
            )
        response.append(
            TaskResponse(
                id=task.id,
                project_id=task.project_id,
                title=task.title,
                description=task.description,
                assignee_id=task.assignee_id,
                assignee_name=assignee.name,
                status=task.status,
                priority=task.priority,
                due_date=task.due_date,
                created_at=task.created_at,
                editable=(
                    current_user.role == "admin"
                    or current_user.id == project.owner_id
                    or current_user.id == task.assignee_id
                ),
            )
        )

    return response


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(
    task_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="task not found",
        )

    project = await db.get(Project, task.project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="project not found",
        )
    assignee = await db.get(User, task.assignee_id)
    if (
        current_user.role != "admin"
        and current_user.id != project.owner_id
        and current_user.id != task.assignee_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to view this task",
        )

    comment_result = await db.execute(select(Comment).where(Comment.task_id == task.id))
    comments = comment_result.scalars().all()

    return TaskDetailResponse(
        task=TaskResponse(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            assignee_id=task.assignee_id,
            assignee_name=assignee.name,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            created_at=task.created_at,
            editable=(
                current_user.role == "admin"
                or current_user.id == project.owner_id
                or current_user.id == task.assignee_id
            ),
        ),
        comments=[
            CommentResponse(
                id=comment.id,
                body=comment.body,
                author_name=comment.user.name,
                created_at=comment.created_at,
            )
            for comment in comments
        ],
    )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_tasks(
    task_id: int,
    payload: TaskUpdateStatus,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="task not found")
    project = await db.get(Project, task.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    if (
        current_user.role != "admin"
        and current_user.id != project.owner_id
        and current_user.id != task.assignee_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not allowed to update this task",
        )
    if payload.status is not None:
        task.status = payload.status

    assignee = await db.get(User, task.assignee_id)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update",
        resource="task",
        resource_id=task.id,
    )
    await db.commit()
    await db.refresh(task)

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        assignee_name=assignee.name,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_at=task.created_at,
        editable=True,
    )


@router.patch("/tasks/{task_id}/assign", response_model=TaskResponse)
async def assign_task(
    task_id: int,
    payload: AssignTask,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    project = await db.get(Project, task.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")
    assert_owner_or_admin(project.owner_id, current_user)
    user = await db.get(User, payload.assignee_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.id, ProjectMember.user_id == payload.assignee_id
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=400, detail="not a project member")
    task.assignee_id = payload.assignee_id
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="assign",
        resource="task",
        resource_id=task.id,
    )
    await db.commit()
    await db.refresh(task)

    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        assignee_id=task.assignee_id,
        assignee_name=user.name,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        created_at=task.created_at,
        editable=True,
    )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    assert_owner_or_admin(task.created_by_id, current_user)
    await db.delete(task)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource="task",
        resource_id=task.id,
    )
    await db.commit()

    return {"message": "Task deleted successfully", "task_id": task_id}
