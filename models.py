import enum
from sqlalchemy import Enum
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column
from sqlalchemy import Boolean, DateTime, Table, Column, Integer, String, Text, ForeignKey, UniqueConstraint
from datetime import datetime
from typing import List

Base = declarative_base()

# Ассоциативная таблица между users и interests
user_interest_association = Table(
    "user_interest_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("interest_id", ForeignKey("interests.id"), primary_key=True),
)

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"

'''class InterestEnum(str, enum.Enum):
    sports = "Sports"
    travel = "Travel"
    reading = "Reading"
    languages = "Languages"
    music = "Music"
    cooking = "Cooking"
    technology = "Technology"
    movies = "Movies"
    photography = "Photography"
    art = "Art"
    nature = "Nature"
    board_games = "Board Games"
    psychology = "Psychology"
    fitness = "Fitness"
    volunteering = "Volunteering"
    cars = "Cars"
    fashion = "Fashion"
    history = "History"
    programming = "Programming"
    handcraft = "Handcraft"'''

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]

    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default='false')
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)

    interests: Mapped[List["Interest"]] = relationship("Interest", secondary=user_interest_association, back_populates="users")
    posts: Mapped[List["Post"]] = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="employer")
    job_responses: Mapped[List["JobResponse"]] = relationship("JobResponse", back_populates="candidate")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="user")

class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
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
    file_path = Column(String, nullable=True) 

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

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))  # К какому чату относится
    sender_id = Column(Integer, ForeignKey("users.id"))  # Кто отправил сообщение
    content = Column(Text, nullable=False)  # Текст сообщения
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время отправки

    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="messages")

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор чата
    user1_id = Column(Integer, ForeignKey("users.id"))  # Первый участник чата
    user2_id = Column(Integer, ForeignKey("users.id"))  # Второй участник чата
    chat_type = Column(String, nullable=False)  # "tinder", "family", "language", "work"

    __table_args__ = (UniqueConstraint('user1_id', 'user2_id', 'chat_type', name='unique_chat'),)
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan") #удаление родительского объекта->удаление дочернего


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
