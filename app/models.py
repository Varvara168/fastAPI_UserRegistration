from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Boolean, DateTime, Table, Column, Integer, String, Text, ForeignKey, UniqueConstraint
from datetime import datetime

Base = declarative_base()

# Ассоциативная таблица между users и interests
user_interest_association = Table(
    "user_interest_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Нужно указать server_default='false' (в нижнем регистре, строкой), чтобы PostgreSQL
    # мог заполнить старые записи значением False при миграции
    is_deleted = Column(Boolean, nullable=False, default=False, server_default='false')
    
    deleted_at = Column(DateTime, nullable=True)
    
    name = Column(String)
    city = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)  # "male", "female", "other"
    relationship_goal = Column(String, nullable=True)  # "family", "language", "dating"

    interests = relationship("Interest", secondary=user_interest_association, back_populates="users")

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    
    jobs = relationship("Job", back_populates="employer")
    job_responses = relationship("JobResponse", back_populates="candidate")

class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", secondary=user_interest_association, back_populates="interests")

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

    # Аналогично для поля is_deleted в Post
    is_deleted = Column(Boolean, nullable=False, default=False, server_default='false')
    deleted_at = Column(DateTime, nullable=True)

    tags = relationship("Tag", secondary=post_tag, back_populates="posts")
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

#лайк без продолжение пока другой не лайкнул взаимно
class Matchs(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE')) #от кого
    to_user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE')) #кому
    
    #Ограничение: одн и тот же человек не может поставиь лайк одному и тому же человеку
    __table_args__ = (UniqueConstraint('from_user_id', 'to_user_id', name='from_to_uc'),)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный ID сообщения
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))  # К какому чату относится
    sender_id = Column(Integer, ForeignKey("users.id"))  # Кто отправил сообщение
    content = Column(Text, nullable=False)  # Текст сообщения
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время отправки

    sender = relationship("User", back_populates="messages")
    chat = relationship("Chat", back_populates="messages")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор чата
    user1_id = Column(Integer, ForeignKey("users.id"))  # Первый участник чата
    user2_id = Column(Integer, ForeignKey("users.id"))  # Второй участник чата
    chat_type = Column(String, nullable=False)  # "tinder", "family", "language", "work"

    __table_args__ = (UniqueConstraint('user1_id', 'user2_id', 'chat_type', name='unique_chat'),)


class Job(Base):
    __tablename__ = "jobs" 

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    employer_id = Column(Integer, ForeignKey("users.id"))
    is_open = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    employer = relationship("User", back_populates="jobs")
    responses = relationship("JobResponse", back_populates="job")

class JobResponse(Base):
    __tablename__ = "job_responses"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    candidate_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_accepted = Column(Boolean, default=False)

    job = relationship("Job", back_populates="responses")
    candidate = relationship("User")
