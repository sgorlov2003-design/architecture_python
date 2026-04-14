-- Типовые запросы для отчёта по оптимизации (EXPLAIN ANALYZE выполнять вручную в psql).

-- Q1: Поиск пользователей по маске ФИО (использует GIN pg_trgm)
-- Параметр: шаблон подстроки
-- EXPLAIN ANALYZE
SELECT id, login, first_name, last_name
FROM users
WHERE (first_name || ' ' || last_name) ILIKE '%' || :name_mask || '%'
ORDER BY login;

-- Q2: История тренировок пользователя с упражнениями (JOIN + сортировка по дате)
-- EXPLAIN ANALYZE
SELECT w.id AS workout_id, w.name, w.workout_date, e.id AS exercise_id, e.name AS exercise_name, we.position
FROM workouts w
JOIN workout_exercises we ON we.workout_id = w.id
JOIN exercises e ON e.id = we.exercise_id
WHERE w.user_id = :user_id
ORDER BY w.workout_date DESC, we.position;

-- Q3: Статистика за период: число тренировок и суммарное число упражнений в них
-- EXPLAIN ANALYZE
SELECT
    COUNT(DISTINCT w.id) AS total_workouts,
    COUNT(we.id) AS total_exercise_entries
FROM workouts w
LEFT JOIN workout_exercises we ON we.workout_id = w.id
WHERE w.user_id = :user_id
  AND w.workout_date BETWEEN :period_start AND :period_end;

-- Q4: Упражнения, чаще всего попадающие в тренировки (агрегат по справочнику)
-- EXPLAIN ANALYZE
SELECT e.id, e.name, COUNT(we.id) AS usage_count
FROM exercises e
LEFT JOIN workout_exercises we ON we.exercise_id = e.id
GROUP BY e.id, e.name
ORDER BY usage_count DESC, e.name;

-- Q5: Нечёткий поиск упражнений по названию
-- EXPLAIN ANALYZE
SELECT id, name, description
FROM exercises
WHERE name ILIKE '%' || :sub || '%'
ORDER BY name;
