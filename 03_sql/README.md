# Домашнее задание 03: проектирование и оптимизация реляционной БД

**Автор:** Горлов Степан Николаевич, М8О-106СВ-25  
**Вариант:** 14 (фитнес-трекер)

REST API совпадает по операциям с ДЗ 02; данные хранятся в **PostgreSQL** (параметризованные запросы, пул соединений `psycopg_pool`).

## Схема БД

| Таблица | Описание |
| ------- | -------- |
| `users` | Учётные записи: `login` (UNIQUE), `password_hash`, имя, фамилия, метки времени; `updated_at` обновляется триггером |
| `exercises` | Справочник упражнений |
| `workouts` | Тренировки: владелец `user_id`, название, дата |
| `workout_exercises` | Связь тренировки и упражнения с полем `position` (порядок в тренировке) |

Файлы: [sql/schema.sql](sql/schema.sql), демо-данные [sql/data.sql](sql/data.sql), примеры запросов [sql/queries.sql](sql/queries.sql).

## Индексы

- B-tree: `idx_users_login`, `idx_workouts_user_date`, индексы по FK в `workout_exercises`.
- GIN + `pg_trgm`: поиск по маске ФИО и по названию упражнения.

Подробный разбор планов выполнения и стратегия партиционирования: [sql/optimization.md](sql/optimization.md).

## Запуск (Docker)

Из каталога `03_sql`:

```bash
docker compose up -d --build
```

- API: http://localhost:8090 (документация: `/docs`; при необходимости порт меняется в `docker-compose.yaml`)
- Swagger UI со статической спецификацией: http://localhost:8091
- PostgreSQL: порт `5432`, БД `fitness_tracker`, пользователь `fitness_user`, пароль `fitness_password` (только для учебной среды)

Остановка: `docker compose down`. Для сброса данных: `docker compose down -v`.

## Локальная разработка и тесты

1. Поднять только БД: `docker compose up -d postgres`
2. Скопировать [`.env.example`](.env.example) в `.env` или задать `DATABASE_URL` и `JWT_SECRET_KEY`
3. Установить зависимости: `pip install -r requirements-dev.txt` (рекомендуется **Python 3.11–3.13** из-за готовых wheel для зависимостей)
4. Запуск API: `uvicorn main:app --reload --port 8080`
5. Тесты: `make test` или `python -m pytest tests/ -v`

## Сборка образа API без PyPI (опционально)

```bash
make wheels
make build-offline
```

## Структура каталога

| Путь | Назначение |
| ---- | ---------- |
| `app/main.py` | FastAPI, маршруты |
| `app/db.py` | Пул PostgreSQL |
| `app/auth_core.py`, `app/middleware_auth.py` | JWT |
| `app/schemas.py` | DTO |
| `sql/` | DDL, данные, запросы, отчёт по оптимизации |
| `openapi.yaml` | OpenAPI 3.0 |
