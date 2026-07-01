from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from week4.app.audit import log_action
from week4.app.database import get_db
from week4.app.dependencies import assert_owner_or_admin, get_current_user, require_permission
from week4.app.models import Post
from week4.app.rbac import can
from week4.app.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def post_create(
    payload: PostCreate,
    current_user=Depends(require_permission("post", "create")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    post = Post(
        user_id=current_user.id,
        title=payload.title,
        body=payload.body,
    )
    db.add(post)

    await db.commit()
    await db.refresh(post)
    await log_action(
        db,
        current_user.id,
        "post.create",
        "post",
        post.id,
    )
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "user_id": post.user_id,
    }


@router.get("")
async def get_post(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Post))
    posts = result.scalars().all()
    response = []
    for post in posts:
        is_owner = post.user_id == current_user.id
        can_edit = is_owner and can(current_user.role, "post", "update_own")
        can_edit = can_edit or can(current_user.role, "post", "update_any")
        post_response = PostResponse(
            id=post.id, user_id=post.user_id, title=post.title, body=post.body, editable=can_edit
        )
        response.append(post_response)
    return response


@router.get("/{post_id}")  # retrieve information about post with post_id
async def get_posts(
    post_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Record not found",
        )
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "user_id": post.user_id,
    }


@router.put("/{post_id}")  # update post with post_id
async def create_post(
    post_id: int,
    payload: PostUpdate,
    current_user=Depends(require_permission("post", "update_own")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Record not found")
    assert_owner_or_admin(post.user_id, current_user)
    if payload.title is not None:
        post.title = payload.title
    if payload.body is not None:
        post.body = payload.body

    await db.commit()
    await db.refresh(post)
    await log_action(
        db,
        current_user.id,
        "post.update",
        "post",
        post.id,
    )
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "user_id": post.user_id,
    }


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user=Depends(require_permission("post", "delete_own")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Record not found")
    assert_owner_or_admin(post.user_id, current_user)
    await db.delete(post)
    await db.commit()
    await log_action(
        db,
        current_user.id,
        "post.delete",
        "post",
        post.id,
    )
    return Response(status_code=204)
