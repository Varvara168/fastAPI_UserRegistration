from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean, DateTime, Table, Column, Integer, String, Text, ForeignKey
from datetime import datetime, timedelta

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")


post_tag = Table(
    "post_tag",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    posts = relationship("Post", secondary=post_tag, back_populates="tags")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)

    is_deleted = Column(Boolean, default=False, nullable=False)     # флаг мягкого удаления
    deleted_at = Column(DateTime, nullable=True)                    # когда удалён

    tags = relationship("Tag", secondary=post_tag, back_populates="posts")
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")