from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime | None
    is_archived: bool
    member_count: int
    model_config = {"from_attributes": True}


class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    created_at: datetime | None
    is_archived: bool
    member: list[str]
    task_count: int


class ProjectUpdate(BaseModel):
    name: str
    description: str


class AddMember(BaseModel):
    user_id: int


class AddTasks(BaseModel):
    title: str
    description: str
    assignee_id: int
    priority: str = "low"
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: str
    assignee_id: int
    assignee_name: str
    status: str
    priority: str
    due_date: datetime | None = None
    created_at: datetime | None
    editable: bool

    model_config = {"from_attributes": True}


class TaskDetailResponse(BaseModel):
    task: TaskResponse
    comments: list[CommentResponse]


class TaskUpdateStatus(BaseModel):
    status: str


class AssignTask(BaseModel):
    assignee_id: int


class CommentCreate(BaseModel):
    body: str


class CommentResponse(BaseModel):
    id: int
    body: str
    author_name: str
    created_at: datetime | None


class UserRoleResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    model_config = {"from_attributes": True}


class UpdateRole(BaseModel):
    role: str


class AuditLogResponse(BaseModel):
    action: str
    resource: str
    resource_id: int
    user_name: str
    timestamp: datetime | None


class ErrorLogResponse(BaseModel):
    id: int
    timestamp: datetime | None
    endpoint: str
    http_method: str
    user_id: int | None
    exception_type: str
    error_message: str
    stack_trace: str
    analysis_time: datetime | None
    root_cause: str | None
    suggested_fix: str | None
    llm_model: str | None
    status: str

    model_config = {"from_attributes": True}


class ErrorLogSummary(BaseModel):
    id: int
    timestamp: datetime
    endpoint: str
    exception_type: str
    status: str
    root_cause: str | None
    suggested_fix: str | None
    model_config = {"from_attributes": True}
