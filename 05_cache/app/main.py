from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from psycopg import errors as pg_errors

from app import db
from app import redis_cache
from app.auth_core import (
    create_access_token,
    get_current_user_id,
    hash_password,
    verify_password,
)
from app.middleware_auth import JWTAuthMiddleware
from app.middleware_ratelimit import RateLimitMiddleware
from app.schemas import (
    ExerciseCreate,
    ExerciseResponse,
    ExerciseToWorkout,
    ExerciseUpdate,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    WorkoutCreate,
    WorkoutResponse,
    WorkoutStatistics,
)

TTL_EXERCISES = 60
TTL_USER_LOGIN = 90
TTL_STATS = 45


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.open_pool()
    redis_cache.connect()
    yield
    redis_cache.close()
    db.close_pool()


app = FastAPI(
    title="Fitness Tracker API",
    description="ДЗ 05, вариант 14 — PostgreSQL + Redis",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTAuthMiddleware)


@app.get("/")
def root():
    return {"service": "fitness-tracker-cache", "docs": "/docs", "openapi": "/openapi.json"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    try:
        with db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (login, password_hash, first_name, last_name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id::text, login, first_name, last_name
                    """,
                    (body.login, hash_password(body.password), body.first_name, body.last_name),
                )
                row = cur.fetchone()
            conn.commit()
    except pg_errors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким логином уже существует",
        )
    return UserResponse(id=row[0], login=row[1], first_name=row[2], last_name=row[3])


@app.post("/token", response_model=TokenResponse)
def login_oauth2(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM users WHERE login = %s",
                (form_data.username,),
            )
            row = cur.fetchone()
    if not row or not verify_password(form_data.password, row[0]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(form_data.username))


@app.post("/auth/login", response_model=TokenResponse)
def login_json(body: UserLogin):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM users WHERE login = %s",
                (body.login,),
            )
            row = cur.fetchone()
    if not row or not verify_password(body.password, row[0]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    return TokenResponse(access_token=create_access_token(body.login))


@app.get("/users/by-login/{login}", response_model=UserResponse)
def get_user_by_login(login: str):
    k = redis_cache.key_user_login(login)
    cached = redis_cache.get_json(k)
    if cached is not None:
        return UserResponse(**cached)
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, login, first_name, last_name FROM users WHERE login = %s",
                (login,),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    u = UserResponse(id=row[0], login=row[1], first_name=row[2], last_name=row[3])
    redis_cache.set_json(k, u.model_dump(), TTL_USER_LOGIN)
    return u


@app.get("/users/search", response_model=list[UserResponse])
def search_users(name_mask: Optional[str] = None):
    with db.connection() as conn:
        with conn.cursor() as cur:
            if name_mask:
                cur.execute(
                    """
                    SELECT id::text, login, first_name, last_name FROM users
                    WHERE (first_name || ' ' || last_name) ILIKE %s
                    ORDER BY login
                    """,
                    (f"%{name_mask}%",),
                )
            else:
                cur.execute(
                    "SELECT id::text, login, first_name, last_name FROM users ORDER BY login"
                )
            rows = cur.fetchall()
    return [UserResponse(id=r[0], login=r[1], first_name=r[2], last_name=r[3]) for r in rows]


@app.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(body: ExerciseCreate):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO exercises (name, description)
                VALUES (%s, %s)
                RETURNING id::text, name, description
                """,
                (body.name, body.description),
            )
            row = cur.fetchone()
        conn.commit()
    redis_cache.invalidate_exercises()
    return ExerciseResponse(id=row[0], name=row[1], description=row[2])


@app.get("/exercises", response_model=list[ExerciseResponse])
def list_exercises():
    cached = redis_cache.get_json(redis_cache.KEY_EXERCISES_LIST)
    if cached is not None:
        return [ExerciseResponse(**x) for x in cached]
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id::text, name, description FROM exercises ORDER BY name")
            rows = cur.fetchall()
    out = [ExerciseResponse(id=r[0], name=r[1], description=r[2]) for r in rows]
    redis_cache.set_json(
        redis_cache.KEY_EXERCISES_LIST,
        [x.model_dump() for x in out],
        TTL_EXERCISES,
    )
    return out


@app.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: str):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, name, description FROM exercises WHERE id = %s::uuid",
                (exercise_id,),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    return ExerciseResponse(id=row[0], name=row[1], description=row[2])


@app.patch("/exercises/{exercise_id}", response_model=ExerciseResponse)
def patch_exercise(exercise_id: str, body: ExerciseUpdate):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, name, description FROM exercises WHERE id = %s::uuid",
                (exercise_id,),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
            name, descr = row[1], row[2]
            if body.name is not None:
                name = body.name
            if body.description is not None:
                descr = body.description
            cur.execute(
                "UPDATE exercises SET name = %s, description = %s WHERE id = %s::uuid RETURNING id::text, name, description",
                (name, descr, exercise_id),
            )
            row = cur.fetchone()
        conn.commit()
    redis_cache.invalidate_exercises()
    return ExerciseResponse(id=row[0], name=row[1], description=row[2])


@app.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: str):
    row = None
    try:
        with db.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM exercises WHERE id = %s::uuid RETURNING id", (exercise_id,))
                row = cur.fetchone()
            conn.commit()
    except pg_errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Упражнение используется в тренировках и не может быть удалено",
        )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    redis_cache.invalidate_exercises()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(body: WorkoutCreate, user_id: str = Depends(get_current_user_id)):
    wdate = body.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO workouts (user_id, name, workout_date)
                VALUES (%s::uuid, %s, %s::date)
                RETURNING id::text
                """,
                (user_id, body.name, wdate),
            )
            wid = cur.fetchone()[0]
        conn.commit()
    redis_cache.invalidate_stats(user_id)
    return WorkoutResponse(id=wid, user_id=user_id, name=body.name, date=wdate, exercise_ids=[])


@app.post("/workouts/{workout_id}/exercises", response_model=WorkoutResponse)
def add_exercise_to_workout(workout_id: str, body: ExerciseToWorkout, user_id: str = Depends(get_current_user_id)):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, user_id::text, name, workout_date::text FROM workouts WHERE id = %s::uuid",
                (workout_id,),
            )
            wrow = cur.fetchone()
            if not wrow:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
            _, w_user_id, wname, wdate = wrow
            if w_user_id != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этой тренировке")
            cur.execute("SELECT id FROM exercises WHERE id = %s::uuid", (body.exercise_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
            cur.execute(
                "SELECT COALESCE(MAX(position), -1) + 1 FROM workout_exercises WHERE workout_id = %s::uuid",
                (workout_id,),
            )
            pos = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO workout_exercises (workout_id, exercise_id, position)
                VALUES (%s::uuid, %s::uuid, %s)
                """,
                (workout_id, body.exercise_id, pos),
            )
            cur.execute(
                """
                SELECT e.id::text FROM workout_exercises we
                JOIN exercises e ON e.id = we.exercise_id
                WHERE we.workout_id = %s::uuid
                ORDER BY we.position
                """,
                (workout_id,),
            )
            eids = [r[0] for r in cur.fetchall()]
        conn.commit()
    redis_cache.invalidate_stats(user_id)
    return WorkoutResponse(
        id=workout_id,
        user_id=user_id,
        name=wname,
        date=wdate,
        exercise_ids=eids,
    )


@app.get("/users/me/workouts", response_model=list[WorkoutResponse])
def get_my_workouts(user_id: str = Depends(get_current_user_id)):
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT w.id::text, w.user_id::text, w.name, w.workout_date::text
                FROM workouts w
                WHERE w.user_id = %s::uuid
                ORDER BY w.workout_date DESC, w.created_at DESC
                """,
                (user_id,),
            )
            wrows = cur.fetchall()
            result = []
            for wid, uid, wname, wdate in wrows:
                cur.execute(
                    """
                    SELECT e.id::text FROM workout_exercises we
                    JOIN exercises e ON e.id = we.exercise_id
                    WHERE we.workout_id = %s::uuid
                    ORDER BY we.position
                    """,
                    (wid,),
                )
                eids = [r[0] for r in cur.fetchall()]
                result.append(
                    WorkoutResponse(id=wid, user_id=uid, name=wname, date=wdate, exercise_ids=eids)
                )
    return result


@app.get("/users/me/workouts/statistics", response_model=WorkoutStatistics)
def get_workout_statistics(
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    start = period_start or "0000-01-01"
    end = period_end or "9999-12-31"
    ck = redis_cache.key_stats(user_id, start, end)
    cached = redis_cache.get_json(ck)
    if cached is not None:
        return WorkoutStatistics(**cached)
    with db.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(DISTINCT w.id), COUNT(we.id)
                FROM workouts w
                LEFT JOIN workout_exercises we ON we.workout_id = w.id
                WHERE w.user_id = %s::uuid
                  AND w.workout_date BETWEEN %s::date AND %s::date
                """,
                (user_id, start, end),
            )
            tw, te = cur.fetchone()
    st = WorkoutStatistics(
        user_id=user_id,
        period_start=start,
        period_end=end,
        total_workouts=int(tw),
        total_exercises=int(te),
    )
    redis_cache.set_json(ck, st.model_dump(), TTL_STATS)
    return st
