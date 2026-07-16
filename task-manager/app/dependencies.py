from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.rbac import Role, can
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(role: str) -> Callable:
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user

    return checker


def require_permission(resource: str, action: str) -> Callable[..., User]:
    """Dependency factory — raises 403 if current user lacks permission."""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if not can(current_user.role, resource, action):
            raise HTTPException(
                status_code=403,
                detail=f"Role '{current_user.role}' cannot perform '{action}' on '{resource}'",
            )
        return current_user

    return checker


def assert_owner_or_admin(resource_owner_id: int, current_user: User) -> None:
    """
    Raises 403 if current_user is neither the owner nor an admin.
    Call this inside route handlers that need ownership checks.
    """
    if current_user.id != resource_owner_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="You can only modify your own resources")
