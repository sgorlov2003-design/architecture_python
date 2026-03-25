"""Домашнее задание 02. Вариант 14 — Фитнес-трекер. FastAPI + JWT + OAuth2 /token."""
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth_core import (
    create_access_token,
    get_current_user_id,
    hash_password,
    verify_password,
)
from app.middleware_auth import JWTAuthMiddleware
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
from app.storage import exercises_db, users_db, workouts_db

app = FastAPI(
    title="Фитнес-трекер API",
    description="ДЗ 02, вариант 14 — REST API по операциям из homeworks_variants",
    version="1.0.0",
)
app.add_middleware(JWTAuthMiddleware)


@app.get("/")
def root():
    return {"service": "fitness-tracker", "docs": "/docs", "openapi": "/openapi.json"}


# --- Регистрация / логин (OAuth2 form + JSON) ---

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    """1. Создание нового пользователя."""
    if body.login in users_db:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким логином уже существует")
    user_id = str(uuid4())
    users_db[body.login] = {
        "id": user_id,
        "login": body.login,
        "password_hash": hash_password(body.password),
        "first_name": body.first_name,
        "last_name": body.last_name,
    }
    return UserResponse(
        id=user_id,
        login=body.login,
        first_name=body.first_name,
        last_name=body.last_name,
    )


@app.post("/token", response_model=TokenResponse)
def login_oauth2(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """OAuth2 password flow. В Swagger: Authorize → username=логин, password=пароль."""
    if form_data.username not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = users_db[form_data.username]
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(form_data.username))


@app.post("/auth/login", response_model=TokenResponse)
def login_json(body: UserLogin):
    """Логин JSON-ом (удобно для curl/Postman)."""
    if body.login not in users_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    user = users_db[body.login]
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    return TokenResponse(access_token=create_access_token(body.login))


@app.get("/users/by-login/{login}", response_model=UserResponse)
def get_user_by_login(login: str):
    """2. Поиск пользователя по логину."""
    if login not in users_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    u = users_db[login]
    return UserResponse(id=u["id"], login=u["login"], first_name=u["first_name"], last_name=u["last_name"])


@app.get("/users/search", response_model=list[UserResponse])
def search_users(name_mask: Optional[str] = None):
    """3. Поиск пользователей по маске имя и фамилии (подстрока)."""
    result = []
    for u in users_db.values():
        full = f"{u['first_name']} {u['last_name']}"
        if not name_mask or name_mask.lower() in full.lower():
            result.append(UserResponse(id=u["id"], login=u["login"], first_name=u["first_name"], last_name=u["last_name"]))
    return result


@app.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(body: ExerciseCreate):
    """4. Создание упражнения."""
    ex_id = str(uuid4())
    exercises_db.append({"id": ex_id, "name": body.name, "description": body.description})
    return ExerciseResponse(id=ex_id, name=body.name, description=body.description)


@app.get("/exercises", response_model=list[ExerciseResponse])
def list_exercises():
    """5. Получение списка упражнений."""
    return [ExerciseResponse(id=e["id"], name=e["name"], description=e.get("description")) for e in exercises_db]


@app.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: str):
    ex = next((e for e in exercises_db if e["id"] == exercise_id), None)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    return ExerciseResponse(id=ex["id"], name=ex["name"], description=ex.get("description"))


@app.patch("/exercises/{exercise_id}", response_model=ExerciseResponse)
def patch_exercise(exercise_id: str, body: ExerciseUpdate):
    """Частичное обновление упражнения (HTTP PATCH по заданию)."""
    ex = next((e for e in exercises_db if e["id"] == exercise_id), None)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    if body.name is not None:
        ex["name"] = body.name
    if body.description is not None:
        ex["description"] = body.description
    return ExerciseResponse(id=ex["id"], name=ex["name"], description=ex.get("description"))


@app.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: str):
    """Удаление упражнения (HTTP DELETE)."""
    for i, e in enumerate(exercises_db):
        if e["id"] == exercise_id:
            exercises_db.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")


@app.post("/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(body: WorkoutCreate, user_id: str = Depends(get_current_user_id)):
    """6. Создание тренировки (JWT + middleware)."""
    w_id = str(uuid4())
    date = body.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    workouts_db.append({"id": w_id, "user_id": user_id, "name": body.name, "date": date, "exercise_ids": []})
    return WorkoutResponse(id=w_id, user_id=user_id, name=body.name, date=date, exercise_ids=[])


@app.post("/workouts/{workout_id}/exercises", response_model=WorkoutResponse)
def add_exercise_to_workout(workout_id: str, body: ExerciseToWorkout, user_id: str = Depends(get_current_user_id)):
    """7. Добавление упражнения в тренировку."""
    workout = next((w for w in workouts_db if w["id"] == workout_id), None)
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    if workout["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этой тренировке")
    ex = next((e for e in exercises_db if e["id"] == body.exercise_id), None)
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    workout["exercise_ids"].append(body.exercise_id)
    return WorkoutResponse(
        id=workout["id"],
        user_id=workout["user_id"],
        name=workout["name"],
        date=workout["date"],
        exercise_ids=workout["exercise_ids"].copy(),
    )


@app.get("/users/me/workouts", response_model=list[WorkoutResponse])
def get_my_workouts(user_id: str = Depends(get_current_user_id)):
    """8. Получение истории тренировок пользователя."""
    return [
        WorkoutResponse(id=w["id"], user_id=w["user_id"], name=w["name"], date=w["date"], exercise_ids=w["exercise_ids"].copy())
        for w in workouts_db
        if w["user_id"] == user_id
    ]


@app.get("/users/me/workouts/statistics", response_model=WorkoutStatistics)
def get_workout_statistics(
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    """9. Получение статистики тренировок за период."""
    my_workouts = [w for w in workouts_db if w["user_id"] == user_id]
    start = period_start or "0000-01-01"
    end = period_end or "9999-12-31"
    in_period = [w for w in my_workouts if start <= w["date"] <= end]
    total_exercises = sum(len(w["exercise_ids"]) for w in in_period)
    return WorkoutStatistics(
        user_id=user_id,
        period_start=start,
        period_end=end,
        total_workouts=len(in_period),
        total_exercises=total_exercises,
    )
