from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Table, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id",
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    age: Mapped[int | None]
    active: Mapped[bool | None] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    hashed_password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, server_default=text(" 'viewer' "))
    posts: Mapped[list[Post]] = relationship("Post", back_populates="user")
    comments: Mapped[list[Comment]] = relationship("Comment", back_populates="user")


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="posts",
    )

    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="post",
    )

    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
    )


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    post_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    user: Mapped[User] = relationship(
        "User",
        back_populates="comments",
    )

    post: Mapped[Post] = relationship(
        "Post",
        back_populates="comments",
    )


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    posts: Mapped[list[Post]] = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str]  # e.g. "post.create"
    resource: Mapped[str]  # e.g. "post"
    resource_id: Mapped[int | None]
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)
