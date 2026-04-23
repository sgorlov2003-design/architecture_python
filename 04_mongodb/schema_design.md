# Документная модель (ДЗ 04, вариант 14)

**users** — `_id` (UUID string), `login`, `password_hash` (SHA-256), `first_name`, `last_name`, `created_at`, `updated_at`. Уникальный индекс по `login`.

**exercises** — `_id`, `name`, `description` (string или null), `created_at`.

**workouts** — `_id`, `user_id`, `name`, `workout_date` (строка `YYYY-MM-DD`), `items` (массив `{ exercise_id, position }`), `created_at`. Индекс `user_id` + `workout_date`.

Валидация задаётся в `validation.js` (`validationLevel: strict`). Скрипты: `data.js` — данные, `queries.js` — примеры выборок.
