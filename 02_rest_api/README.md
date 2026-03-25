# Домашнее задание 02: Разработка REST API сервиса

---

REST API сервис для системы **«Фитнес-трекер»** (учёт тренировок и упражнений).

**Вариант:** 14  
**Автор:** Горлов Степан Николаевич М8О-106СВ-25

---

## Описание

Система предназначена для:

- регистрации пользователей и аутентификации (JWT, OAuth2 `/token`, логин JSON);
- ведения справочника упражнений;
- создания тренировок и добавления упражнений в тренировку;
- просмотра истории тренировок и статистики за период.

Реализация: **Python 3**, **FastAPI**, in-memory хранилище, контракт в **`openapi.yaml`**, отдельный контейнер **Swagger UI**.

---

## Быстрый старт

### Требования

| Компонент      | Версия   |
| -------------- | -------- |
| Python         | ≥ 3.11   |
| pip            | актуальная |
| Docker         | ≥ 20.10  |
| Docker Compose | ≥ 2.0    |
| make           | опционально |

### Сборка

```bash
make build
```

### Запуск

```bash
docker compose up --build
```

REST API: http://localhost:8080  

### Запуск тестов

```bash
make test
```

### Сборка + тесты

```bash
make build-tests
```

### Очистка

```bash
make clean
```

### Открыть Swagger UI

```
http://localhost:8081
```

---

## Примечания

- Для разработки на хосте: `pip install -r requirements-dev.txt` (при недоступности `pypi.org` добавьте `-i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn`), затем `uvicorn main:app --reload --host 0.0.0.0 --port 8080`. Интерактивные доки: http://localhost:8080/docs  
- Сборка образа по умолчанию использует зеркала PyPI (Tsinghua → Aliyun → официальный индекс). Свой индекс: `docker compose build --build-arg PIP_INDEX_URL=...`  
- Офлайн-сборка: `scripts/download_wheels.ps1` или `scripts/download_wheels.sh`, затем `docker compose build --build-arg INSTALL_MODE=offline`  
- Рекомендуется `DOCKER_BUILDKIT=1` при `docker compose build` (кэш pip в Dockerfile)

---

## Операции варианта 14 → эндпоинты

| № | Операция | Метод | Путь |
| - | -------- | ----- | ---- |
| 1 | Создание пользователя | POST | `/users` |
| 2 | Поиск по логину | GET | `/users/by-login/{login}` |
| 3 | Поиск по маске имя/фамилия | GET | `/users/search?name_mask=` |
| 4 | Создание упражнения | POST | `/exercises` |
| 5 | Список упражнений | GET | `/exercises` |
| 6 | Создание тренировки | POST | `/workouts` (JWT) |
| 7 | Упражнение в тренировку | POST | `/workouts/{id}/exercises` (JWT) |
| 8 | История тренировок | GET | `/users/me/workouts` (JWT) |
| 9 | Статистика за период | GET | `/users/me/workouts/statistics` (JWT) |

Дополнительно: GET/PATCH/DELETE `/exercises/{id}`.

---

## Структура проекта

```
02_rest_api/
  app/
    main.py
    schemas.py
    storage.py
    auth_core.py
    middleware_auth.py
  main.py
  openapi.yaml
  requirements.txt
  requirements-dev.txt
  wheels/
  scripts/
  Dockerfile
  docker-compose.yaml
  Makefile
  .dockerignore
  tests/
```

---

## Примеры

OAuth2-токен:

```bash
curl -X POST "http://localhost:8080/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ivan&password=secret"
```

Запрос с JWT:

```bash
curl -X GET "http://localhost:8080/users/me/workouts" \
  -H "Authorization: Bearer <access_token>"
```
