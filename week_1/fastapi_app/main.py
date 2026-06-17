from datetime import UTC, datetime

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    pwd: str
    active: bool


class UserDetailResponse(BaseModel):
    id: int
    name: str
    email: str
    pwd: str
    active: bool


class UserUpdate(BaseModel):
    name: str
    email: str
    active: bool


class UserListResponse(BaseModel):
    id: int
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    active: bool


user_db = {}


def get_db():
    return user_db


next_user_id = 1


def get_current_user(x_user_id: int | None = Header(default=None), db: dict = Depends(get_db)):
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-user-id header required")
    if x_user_id not in db:
        raise HTTPException(status_code=401, detail="User not found")
    return db[x_user_id]


app = FastAPI()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def request_validation_error(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "error": "Request Validation Error",
            "message": errors[0]["msg"],
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "name": "Shreya",
                        "email": "shreya@gmail.com",
                        "pwd": "shrey@123",
                        "active": True,
                    }
                }
            }
        }
    },
)
def create_user(user: UserCreate, db: dict = Depends(get_db)):
    global next_user_id
    new_user = {
        "id": next_user_id,
        "name": user.name,
        "email": user.email,
        "pwd": user.pwd,
        "active": user.active,
    }
    db[next_user_id] = new_user
    next_user_id += 1
    return new_user


@app.get("/users/{user_id}", response_model=UserDetailResponse)
def get_user(user_id: int, db: dict = Depends(get_db)):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    return db[user_id]


@app.get("/users/", response_model=list[UserListResponse])
def list_user(active: bool | None = None):
    users = list(user_db.values())
    if active is not None:
        users = [user for user in users if user["active"] == active]
    return users


@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return {"current_user": current_user}


@app.put("/users/{user_id}", response_model=UserDetailResponse)
def update_user(user_id: int, user: UserUpdate, db: dict = Depends(get_db)):
    if user_id not in db:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = {"id": user_id, "name": user.name, "email": user.email, "active": user.active}
    db[user_id] = updated_user
    return updated_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: dict = Depends(get_db)):
    if user_id not in db:
        raise HTTPException(status_code=204, detail="User not found")
    del db[user_id]
    return Response(status_code=204)
