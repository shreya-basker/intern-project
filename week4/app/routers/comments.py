from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from week4.app.audit import log_action
from week4.app.database import get_db
from week4.app.dependencies import assert_owner_or_admin, get_current_user, require_permission
from week4.app.models import Comment, Post
from week4.app.schemas import CommentCreate

router = APIRouter(tags=["comments"])


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comments(
    post_id: int,
    payload: CommentCreate,
    current_user=Depends(require_permission("comment", "create")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found",
        )
    comment = Comment(post_id=post_id, user_id=current_user.id, body=payload.body)
    db.add(comment)

    await db.commit()
    await db.refresh(comment)
    await log_action(
        db,
        current_user.id,
        "comment.create",
        "comment",
        comment.id,
    )
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "body": comment.body,
    }


@router.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Record not found")
    result = await db.execute(select(Comment).where(Comment.post_id == post_id))
    comments = result.scalars().all()
    return {
        "id": comments.id,
        "post_id": comments.post_id,
        "user_id": comments.user_id,
        "body": comments.body,
    }


@router.delete("/comments/{comment_id}")
async def delete_comments(
    comment_id: int,
    current_user=Depends(require_permission("comment", "delete_own")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    comment = await db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Record not found")
    assert_owner_or_admin(comment.user_id, current_user)
    comment_id_to_log = comment.id
    await db.delete(comment)
    await db.commit()
    await log_action(
        db,
        current_user.id,
        "comment.delete",
        "comment",
        comment_id_to_log,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
