3️⃣ Запустить Docker

В терминале, находясь в корне проекта:

docker-compose up -d


Это поднимет два контейнера: PostgreSQL и FastAPI (если прописан сервис для приложения в docker-compose.yml).

Если FastAPI не в docker-compose.yml, запускаем отдельно после поднятия БД:

docker build -t my-fastapi-app .
docker run -p 8000:8000 --env-file .env my-fastapi-app

4️⃣ Проверка БД и миграций

Если проект использует Alembic, выполняем миграции:

docker exec -it <имя_контейнера_с_БД> bash
alembic upgrade head


Или, если Alembic настроен в приложении:

docker-compose run app alembic upgrade head


Это создаст все таблицы в новой базе.

5️⃣ Открыть приложение

После запуска контейнера с FastAPI можно открыть браузер:

http://localhost:8000/docs


Там будет Swagger UI со всеми эндпоинтами.
