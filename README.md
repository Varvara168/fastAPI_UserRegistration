
docker-compose up -d
docker build -t my-fastapi-app .
docker run -p 8000:8000 --env-file .env my-fastapi-app
docker-compose run app alembic upgrade head

Открыть приложение
http://localhost:8000/docs
