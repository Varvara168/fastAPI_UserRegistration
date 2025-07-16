from sqlalchemy import Column, Integer, String
from .database import Base
#искать только в данной папке

class User(Base):
    __tablename__ = 'usesrs'
    id = Column(Integer, primary_key=True, index=True) #целое число, ключевое значение(встренная уникалность и ненулевое значение), значение для быстрого поиска
    username = Column(String, unique=True, index=True, nullable=False) # строка, уникальный, значение для быстрого поиска, ненулевое
    password = Column(String, nullable=False) #сторка, зашифрованный, ненулевое
