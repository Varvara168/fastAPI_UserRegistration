from sqlalchemy import Column, Integer, String
from database import Base
# искать только в данной папке

class User(Base):
    __tablename__ = 'users'  
    id = Column(Integer, primary_key=True, index=True)  # целое число, ключевое значение(встроенная уникальность и ненулевое значение), значение для быстрого поиска
    username = Column(String, unique=True, index=True, nullable=False)  # строка, уникальный, значение для быстрого поиска, ненулевое
    hashed_password = Column(String, nullable=False)  # строка, зашифрованный, ненулевое
