from pydantic import BaseModel, ConfigDict, EmailStr


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class PostCreate(BaseModel):
    title: str
    body: str


class PostUpdate(BaseModel):
    title: str | None = None
    body: str | None = None


class PostResponse(BaseModel):
    id: int
    user_id: int | None
    title: str
    body: str | None
    editable: bool
    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    post_id: int
    body: str


class TagCreate(BaseModel):
    name: str
