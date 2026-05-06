# Домашнее задание 05: кэширование и производительность

REST API **«Фитнес-трекер»** (вариант 14): PostgreSQL как в ДЗ 03, поверх — **Redis** (кэш), ограничение частоты запросов к `/token`, `/auth/login`, `/users`.

**Вариант:** 14  
**Автор:** Горлов Степан Николаевич, М8О-106СВ-25

---

## Описание

- Кэш **cache-aside**: список упражнений `GET /exercises`, пользователь по логину `GET /users/by-login/{login}`, статистика `GET /users/me/workouts/statistics`.
- Инвалидация кэша при изменении упражнений и тренировок.
- **Rate limit:** до 60 POST в минуту на IP для `/token`, `/auth/login`, `/users`.
- Замысел по ключам и TTL: [performance_design.md](performance_design.md).

---

## Запуск

```bash
docker compose up --build -d
curl http://localhost:8095/health
```

| Сервис | URL / порт |
| ------ | ---------- |
| API + `/docs` | http://localhost:8095 |
| Swagger UI | http://localhost:8096 |
| PostgreSQL (хост) | `localhost:5433` |
| Redis (хост) | `localhost:6380` |

Остановка: `docker compose down`. Сброс БД: `docker compose down -v`.

Локально: скопировать `.env.example` в `.env`, поднять только `postgres` и `redis`, затем `uvicorn main:app --reload --port 8080`.

---

## Тесты

После `docker compose up -d --build`:

```bash
make docker-test
```

Локально (Python 3.11+, Postgres **5433**, Redis **6380**):

```bash
pip install -r requirements-dev.txt
make test
```

---

## Сборка без PyPI

```bash
make wheels
make build-offline
```
