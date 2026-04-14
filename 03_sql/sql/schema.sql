-- ДЗ 03, вариант 14 — фитнес-трекер. Инициализация схемы PostgreSQL.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    login VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();

CREATE TABLE exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    workout_date DATE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workout_exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workout_id UUID NOT NULL REFERENCES workouts (id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises (id) ON DELETE RESTRICT,
    position INT NOT NULL CHECK (position >= 0),
    UNIQUE (workout_id, position)
);

-- B-tree: авторизация, история, FK
CREATE INDEX idx_users_login ON users (login);
CREATE INDEX idx_workouts_user_date ON workouts (user_id, workout_date DESC);
CREATE INDEX idx_workout_exercises_workout ON workout_exercises (workout_id);
CREATE INDEX idx_workout_exercises_exercise ON workout_exercises (exercise_id);

-- Нечёткий поиск по ФИО (маска имени/фамилии)
CREATE INDEX idx_users_fullname_trgm ON users USING gin (
    (first_name || ' ' || last_name) gin_trgm_ops
);
CREATE INDEX idx_users_first_trgm ON users USING gin (first_name gin_trgm_ops);
CREATE INDEX idx_users_last_trgm ON users USING gin (last_name gin_trgm_ops);

-- Поиск упражнений по подстроке названия
CREATE INDEX idx_exercises_name_trgm ON exercises USING gin (name gin_trgm_ops);
