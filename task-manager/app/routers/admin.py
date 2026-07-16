from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_role
from app.models import AuditLog, Project, ProjectMember, User
from app.schema import AuditLogResponse, ProjectResponse, UpdateRole, UserRoleResponse

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRoleResponse])
async def get_user_role(
    current_user=Depends(require_role("admin")), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()

    return users


@router.patch("/users/{user_id}/role", response_model=UserRoleResponse)
async def update_role(
    user_id: int,
    payload: UpdateRole,
    current_user=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    user.role = payload.role

    await db.commit()
    await db.refresh(user)
    return user


@router.get("/audit_logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    current_user=Depends(require_role("admin")), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100))

    logs = result.scalars().all()
    response = []
    for log in logs:
        response.append(
            AuditLogResponse(
                action=log.action,
                resource=log.resource,
                resource_id=log.resource_id,
                timestamp=log.timestamp,
            )
        )
    return response


@router.get("/projects", response_model=list[ProjectResponse])
async def get_all_projects(
    current_user=Depends(require_role("admin")), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project))
    projects = result.scalars().all()

    response = []
    for project in projects:
        member_result = await db.execute(
            select(ProjectMember).where(ProjectMember.project_id == project.id)
        )

        members = member_result.scalars().all()
        response.append(
            ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                owner_id=project.owner_id,
                created_at=project.created_at,
                is_archived=project.is_archived,
                member_count=len(members),
            )
        )
    return response
