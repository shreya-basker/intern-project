from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    age: Mapped[int | None]
    hashed_password: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")

    # relationships
    projects: Mapped[list[Project]] = relationship(
        "Project", foreign_keys="Project.owner_id", back_populates="owner"
    )
    assigned_tasks: Mapped[list[Task]] = relationship(
        "Task", foreign_keys="Task.assignee_id", back_populates="assignee"
    )
    created_tasks: Mapped[list[Task]] = relationship(
        "Task", foreign_keys="Task.created_by_id", back_populates="creator"
    )
    comment: Mapped[list[Comment]] = relationship("Comment", back_populates="user")
    project_member: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="user"
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int | None] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    is_archived: Mapped[bool | None] = mapped_column(Boolean, server_default=text("False"))

    # relationship
    owner: Mapped[User] = relationship("User", back_populates="projects")
    task: Mapped[list[Task]] = relationship(
        "Task", back_populates="project", cascade="all, delete-orphan"
    )
    members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember", back_populates="project", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, server_default=text("'todo'"))
    priority: Mapped[str] = mapped_column(Text, server_default=text("'low'"))
    assignee_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_by_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    # relationship
    assignee: Mapped[User] = relationship(
        "User", foreign_keys=[assignee_id], back_populates="assigned_tasks"
    )
    creator: Mapped[User] = relationship(
        "User", foreign_keys=[created_by_id], back_populates="created_tasks"
    )
    project: Mapped[Project] = relationship("Project", back_populates="task")
    comments: Mapped[list[Comment]] = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    # relationship
    task: Mapped[Task] = relationship("Task", back_populates="comments")
    user: Mapped[User] = relationship("User", back_populates="comment")


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    # relationship
    user: Mapped[User] = relationship("User", back_populates="project_member")
    project: Mapped[Project] = relationship("Project", back_populates="members")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str]  # e.g. "post.create"
    resource: Mapped[str]  # e.g. "post"
    resource_id: Mapped[int | None]
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
