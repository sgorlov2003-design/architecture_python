# Фитнес-трекер — MongoDB

## Домашнее задание 04

**Вариант 14:** учёт тренировок и упражнений (как в ДЗ 02–03)  
**Автор:** Горлов Степан Николаевич, М8О-106СВ-25  
**Стек:** Python 3.11, FastAPI, PyMongo, MongoDB 7, Docker

---

## Описание проекта

REST API: пользователи и JWT, упражнения, тренировки и статистика. Данные в MongoDB, коллекции `users`, `exercises`, `workouts` (в `workouts` вложен массив `items`: упражнение и позиция). Валидация документов — `$jsonSchema` в `validation.js`.

---

## Запуск

```bash
docker compose up --build -d
curl http://localhost:8092/health
```

- API: http://localhost:8092 (`/docs`)
- Swagger: http://localhost:8094
- MongoDB с хоста: порт **27018**, БД `fitness_tracker`

При первом запуске на пустом томе выполняются `validation.js` и `data.js` из `docker-entrypoint-initdb.d`. Сброс данных:

```bash
docker compose down -v
docker compose up --build -d
```

## Остановка

```bash
docker compose down
```

## Запросы в mongosh

```bash
docker compose exec mongodb mongosh fitness_tracker < validation.js
docker compose exec mongodb mongosh fitness_tracker < data.js
docker compose exec mongodb mongosh fitness_tracker < queries.js
```

## Тесты

```bash
pip install -r requirements-dev.txt
make test
```

Переменные окружения — в `.env.example` (нужен доступный MongoDB по `MONGO_URI`).

## Сборка без PyPI

```bash
make wheels
make build-offline
```

## Файлы проекта

| Файл | Назначение |
| ---- | ---------- |
| `validation.js` | Коллекции, `$jsonSchema`, индексы |
| `data.js` | Тестовые данные |
| `queries.js` | Примеры запросов |
| `schema_design.md` | Описание модели |
| `app/main.py` | Маршруты API |
| `app/db.py` | Подключение к БД |
| `app/auth_core.py`, `app/middleware_auth.py` | JWT |
| `app/schemas.py` | Модели запросов/ответов |
| `openapi.yaml` | OpenAPI 3.0 |
