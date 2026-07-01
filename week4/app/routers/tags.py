from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from week4.app.audit import log_action
from week4.app.database import get_db
from week4.app.dependencies import assert_owner_or_admin, get_current_user, require_permission
from week4.app.models import Post, Tag
from week4.app.schemas import TagCreate

router = APIRouter(tags=["tags"])


@router.get("/tags")
async def get_tags(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Tag))
    tags = result.scalars().all()
    return tags


@router.post(
    "/tags",
    status_code=status.HTTP_201_CREATED,
)
async def post_tags(
    payload: TagCreate,
    current_user=Depends(require_permission("tag", "manage")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    tag = Tag(name=payload.name)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    await log_action(
        db,
        current_user.id,
        "tag.create",
        "tag",
        tag.id,
    )
    return {
        "id": tag.id,
        "name": tag.name,
    }


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    current_user=Depends(require_permission("tag", "manage")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found",
        )

    await db.delete(tag)
    await db.commit()
    await log_action(
        db,
        current_user.id,
        "tag.delete",
        "tag",
        tag_id,
    )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.post("/posts/{post_id}/tags/{tag_id}")
async def tag_post(
    post_id: int,
    tag_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Post).options(selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    assert_owner_or_admin(post.user_id, current_user)
    post.tags.append(tag)

    await db.commit()
    await db.refresh(post)
    await log_action(
        db,
        current_user.id,
        "post.tag.add",
        "post",
        post.id,
    )
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "user_id": post.user_id,
    }


@router.delete("/posts/{post_id}/tags/{tag_id}")
async def tag_post_delete(
    post_id: int,
    tag_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    result = await db.execute(
        select(Post).options(selectinload(Post.tags)).where(Post.id == post_id)
    )
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    tag = await db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    assert_owner_or_admin(post.user_id, current_user)
    post.tags.remove(tag)

    await db.commit()
    await db.refresh(post)
    await log_action(
        db,
        current_user.id,
        "post.tag.remove",
        "post",
        post.id,
    )
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "user_id": post.user_id,
    }
