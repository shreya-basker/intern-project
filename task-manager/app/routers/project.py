from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import assert_owner_or_admin, get_current_user, require_permission
from app.models import Project, ProjectMember, User
from app.schema import (
    AddMember,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.utils import create_audit_log

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/")
async def create_project(
    payload: ProjectCreate,
    current_user=Depends(require_permission("project", "create")),
    db: AsyncSession = Depends(get_db),
):
    project = Project(name=payload.name, description=payload.description, owner_id=current_user.id)

    db.add(project)

    await db.commit()
    await db.refresh(project)
    membership = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
    )
    db.add(membership)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create",
        resource="project",
        resource_id=project.id,
    )
    await db.commit()
    return {"message": "Project created successfully!"}


@router.get("/", response_model=list[ProjectResponse])
async def get_project(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).join(ProjectMember).where(ProjectMember.user_id == current_user.id)
    )
    projects = result.scalars().all()

    response = []
    for project in projects:
        member_count = len(project.members)
        response.append(
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                owner_id=project.owner_id,
                created_at=project.created_at,
                is_archived=project.is_archived,
                member_count=member_count,
            )
        )
    return result


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
    )

    if membership_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=403,
            detail="Not a project member",
        )

    members_result = await db.execute(
        select(User).join(ProjectMember).where(ProjectMember.project_id == project_id)
    )

    members = members_result.scalars().all()

    return ProjectDetailResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        created_at=project.created_at,
        is_archived=project.is_archived,
        member=[user.name for user in members],
        task_count=len(project.task),  # or project.tasks if you renamed it
    )


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    assert_owner_or_admin(project.owner_id, current_user)
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update",
        resource="project",
        resource_id=project.id,
    )
    await db.commit()
    await db.refresh(project)

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    assert_owner_or_admin(project.owner_id, current_user)
    if project.is_archived:
        raise HTTPException(status_code=400, detail="already archived")
    project.is_archived = True
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource="project",
        resource_id=project.id,
    )
    await db.commit()
    await db.refresh(project)

    return {"message": "Project is archived", "project_id": project.id}


@router.post("/{project_id}/members")
async def add_members(
    project_id: int,
    payload: AddMember,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    assert_owner_or_admin(project.owner_id, current_user)
    user = await db.get(User, payload.user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="no user found")
    existing_membership = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == payload.user_id
        )
    )

    if existing_membership.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User already exists in a project")
    membership = ProjectMember(project_id=project_id, user_id=payload.user_id)
    db.add(membership)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="update.members",
        resource="project",
        resource_id=project.id,
    )
    await db.commit()
    await db.refresh(membership)

    return {
        "message": "User added successfully",
        "project_id": project_id,
        "user_id": payload.user_id,
    }


@router.delete("/{project_id}/members/{user_id}")
async def delete_member(
    project_id: int,
    user_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="project not found")
    assert_owner_or_admin(project.owner_id, current_user)

    membership = await db.get(ProjectMember, {"project_id": project_id, "user_id": user_id})

    if membership is None:
        raise HTTPException(status_code=403, detail="User not a member")

    await db.delete(membership)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete.member",
        resource="project",
        resource_id=project.id,
    )
    await db.commit()

    return {"message": "Member removed successfully", "project_id": project_id, "user_id": user_id}
