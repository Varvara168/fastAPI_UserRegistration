## 🚀 FastAPI Auth API

**Простой API-сервис на FastAPI с регистрацией и авторизацией по токену (JWT).**

---

### 📦 Стек технологий:

* **FastAPI** — фреймворк для создания API
* **SQLite** — база данных
* **SQLAlchemy** — ORM для работы с БД
* **Pydantic** — валидация данных
* **JWT (python-jose)** — авторизация по токену
* **Docker** — контейнеризация приложения

---

### 🔧 Установка и запуск

#### 📁 Клонировать репозиторий

```bash
git clone https://github.com/ТВОЙ_ЛОГИН/fastapi-auth-app.git
cd fastapi-auth-app
```

#### 🐳 Запуск через Docker

```bash
docker build -t fastapi-jwt .
docker run -p 8000:8000 fastapi-jwt
```

Приложение будет доступно по адресу:
👉 [http://localhost:8000](http://localhost:8000)

---

### 🔐 Эндпоинты

| Метод | URL          | Описание                           |
| ----- | ------------ | ---------------------------------- |
| POST  | `/register`  | Регистрация нового пользователя    |
| POST  | `/login`     | Логин, выдача JWT токена           |
| GET   | `/protected` | Защищённый маршрут (требует токен) |

---

### 📥 Примеры запросов

#### 🔸 Регистрация

```json
POST /register
{
  "username": "varvara",
  "password": "secret"
}
```

#### 🔸 Логин

```x-www-form-urlencoded
POST /login
username=varvara
password=secret
```

Ответ:

```json
{
  "access_token": "....",
  "token_type": "bearer"
}
```

#### 🔸 Доступ к защищённому маршруту

```http
GET /protected
Authorization: Bearer <access_token>
```

---

### 🧾 Структура проекта

```
├── auth.py
├── database.py
├── Dockerfile
├── main.py
├── models.py
├── schemas.py
├── requirements.txt
└── .dockerignore
```
