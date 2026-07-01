from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from week4.app.database import get_db
from week4.app.dependencies import assert_owner_or_admin, get_current_user, require_permission
from week4.app.models import Post, User
from week4.app.rbac import can
from week4.app.schemas import UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_users(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: int, current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> Any:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    if can(current_user.role, "user", "update_any"):
        return user
    return {
        "name": user.name,
        "email": user.email,
    }


@router.put("/{user_id}")
async def put_user(
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_permission("user", "update_own")),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    assert_owner_or_admin(user.id, current_user)
    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    await db.commit()
    await db.refresh(user)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_permission("user", "delete")),
    db: AsyncSession = Depends(get_db),
) -> Response:
    print("DELETE ROUTE HIT")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    await db.delete(user)
    await db.commit()
    return Response(status_code=204)


@router.get("/{user_id}/posts")
async def get_user_posts(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    result = await db.execute(select(Post).where(Post.user_id == user_id))

    posts = result.scalars().all()
    return {
        "id": posts.id,
        "title": posts.title,
        "body": posts.body,
        "user_id": posts.user_id,
    }
