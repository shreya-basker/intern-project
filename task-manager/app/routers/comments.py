from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import assert_owner_or_admin, get_current_user
from app.models import Comment, ProjectMember, Task
from app.schema import CommentCreate, CommentResponse
from app.utils import create_audit_log

router = APIRouter(prefix="", tags=["comments"])


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse)
async def post_comment(
    task_id: int,
    payload: CommentCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="Not a project member",
        )
    comment = Comment(task_id=task_id, user_id=current_user.id, body=payload.body)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="create",
        resource="comment",
        resource_id=comment.id,
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        body=comment.body,
        author_name=current_user.name,
        created_at=comment.created_at,
    )


@router.get("/tasks/{task_id}/comments", response_model=list[CommentResponse])
async def get_comments(
    task_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    membership_result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == task.project_id,
            ProjectMember.user_id == current_user.id,
        )
    )
    membership = membership_result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=403,
            detail="Not a project member",
        )
    comment_result = await db.execute(select(Comment).where(Comment.task_id == task_id))
    comments = comment_result.scalars().all()
    response = []
    for comment in comments:
        response.append(
            CommentResponse(
                id=comment.id,
                body=comment.body,
                author_name=current_user.name,
                created_at=comment.created_at,
            )
        )
    return response


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="comment not found")
    assert_owner_or_admin(comment.user_id, current_user)
    await db.delete(comment)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource="comment",
        resource_id=comment.id,
    )
    await db.commit()

    return {"message": "Comment deleted successfully", "comment_id": comment_id}
