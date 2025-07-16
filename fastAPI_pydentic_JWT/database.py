from sqlalchemy import create_engine  #создаёт подключение к БД
from sqlalchemy.orm import sessionmaker, declarative_base # создаёт сессии для взаимодействия с БД. базовый класс для моделей (таблиц).

#Путь к базе данных (SQLALCHEMY_DATABASE_URL)
url = "sqlite:///./users.db"

#Создание движка подключения: "check_same_thread": False - для многопотоковости
engine = create_engine(url, connect_args={"check_same_thread": False}) 

# Сессия — рабочее подключение к базе: изменения не сохраняются автоматически. не сбрасываются автоматически перед запросами. указываем, к какой базе подключаться.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Создание таблиц автоматически, Base- родитель для всех моделей

