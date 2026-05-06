# Кэш и нагрузка (ДЗ 05)

## Ключи Redis

| Ключ | Содержимое | TTL |
| ---- | ---------- | --- |
| `ft:exercises:list` | JSON-массив упражнений | 60 с |
| `ft:user:login:{login}` | JSON пользователя | 90 с |
| `ft:stats:{user_id}:{start}:{end}` | JSON статистики | 45 с |
| `ft:rl:{ip}:{bucket}` | счётчик rate limit | 120 с |

## Инвалидация

После POST/PATCH/DELETE упражнений удаляется `ft:exercises:list`. После создания тренировки или добавления упражнения в тренировку — все ключи `ft:stats:{user_id}:*`.

## Rate limit

Окно 60 с, не более 60 POST на IP в окне для `/token`, `/auth/login`, `/users`. При превышении — HTTP 429.
