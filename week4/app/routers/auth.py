from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from week4.app.database import get_db
from week4.app.dependencies import get_current_user, require_role
from week4.app.models import User
from week4.app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)) -> dict[str, object]:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    print("password=", payload.password)
    print("type=", type(payload.password))
    print("length=", len(payload.password))

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role="viewer",
    )
    db.add(user)

    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_me(current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role}


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> None:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()


REFRESH_TOKEN_EXPIRE_DAYS = 7


@router.post("/refresh")
async def refresh(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    new_token = create_access_token({"sub": str(current_user.id), "role": current_user.role})
    return {"access_token": new_token, "token_type": "bearer"}
