# Базовый образ Python
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Команда запуска FastAPI через Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
