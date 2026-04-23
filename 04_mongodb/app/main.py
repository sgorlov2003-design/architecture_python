import re
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError, OperationFailure

from app import db
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


def _workout_exercise_ids(items: list) -> list[str]:
    if not items:
        return []
    return [x["exercise_id"] for x in sorted(items, key=lambda x: x["position"])]


def _rethrow_schema(exc: OperationFailure):
    if exc.code == 121:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ошибка валидации схемы",
        )
    raise exc


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.open_pool()
    yield
    db.close_pool()


app = FastAPI(title="Фитнес-трекер API", description="ДЗ 04, вариант 14", version="1.0.0", lifespan=lifespan)
app.add_middleware(JWTAuthMiddleware)


@app.get("/")
def root():
    return {"service": "fitness-tracker-mongo", "docs": "/docs", "openapi": "/openapi.json"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate):
    now = datetime.now(timezone.utc)
    doc = {
        "_id": str(uuid4()),
        "login": body.login,
        "password_hash": hash_password(body.password),
        "first_name": body.first_name,
        "last_name": body.last_name,
        "created_at": now,
        "updated_at": now,
    }
    try:
        db.database().users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Логин занят")
    except OperationFailure as e:
        _rethrow_schema(e)
    return UserResponse(
        id=doc["_id"],
        login=doc["login"],
        first_name=doc["first_name"],
        last_name=doc["last_name"],
    )


@app.post("/token", response_model=TokenResponse)
def login_oauth2(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    u = db.database().users.find_one({"login": form_data.username}, {"password_hash": 1})
    if not u or not verify_password(form_data.password, u["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(form_data.username))


@app.post("/auth/login", response_model=TokenResponse)
def login_json(body: UserLogin):
    u = db.database().users.find_one({"login": body.login}, {"password_hash": 1})
    if not u or not verify_password(body.password, u["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    return TokenResponse(access_token=create_access_token(body.login))


@app.get("/users/by-login/{login}", response_model=UserResponse)
def get_user_by_login(login: str):
    row = db.database().users.find_one({"login": login})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return UserResponse(
        id=str(row["_id"]),
        login=row["login"],
        first_name=row["first_name"],
        last_name=row["last_name"],
    )


@app.get("/users/search", response_model=list[UserResponse])
def search_users(name_mask: Optional[str] = None):
    coll = db.database().users
    if name_mask:
        safe = re.escape(name_mask)
        rx = {"$regex": safe, "$options": "i"}
        cur = coll.find(
            {
                "$or": [
                    {"first_name": rx},
                    {"last_name": rx},
                    {
                        "$expr": {
                            "$regexMatch": {
                                "input": {"$concat": ["$first_name", " ", "$last_name"]},
                                "regex": safe,
                                "options": "i",
                            }
                        }
                    },
                ]
            },
            {"login": 1, "first_name": 1, "last_name": 1},
        ).sort("login", 1)
    else:
        cur = coll.find({}, {"login": 1, "first_name": 1, "last_name": 1}).sort("login", 1)
    return [
        UserResponse(id=str(r["_id"]), login=r["login"], first_name=r["first_name"], last_name=r["last_name"])
        for r in cur
    ]


@app.post("/exercises", response_model=ExerciseResponse, status_code=status.HTTP_201_CREATED)
def create_exercise(body: ExerciseCreate):
    now = datetime.now(timezone.utc)
    doc = {
        "_id": str(uuid4()),
        "name": body.name,
        "description": body.description,
        "created_at": now,
    }
    try:
        db.database().exercises.insert_one(doc)
    except OperationFailure as e:
        _rethrow_schema(e)
    return ExerciseResponse(id=doc["_id"], name=doc["name"], description=doc.get("description"))


@app.get("/exercises", response_model=list[ExerciseResponse])
def list_exercises():
    rows = db.database().exercises.find({}).sort("name", 1)
    return [ExerciseResponse(id=str(r["_id"]), name=r["name"], description=r.get("description")) for r in rows]


@app.get("/exercises/{exercise_id}", response_model=ExerciseResponse)
def get_exercise(exercise_id: str):
    row = db.database().exercises.find_one({"_id": exercise_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    return ExerciseResponse(id=str(row["_id"]), name=row["name"], description=row.get("description"))


@app.patch("/exercises/{exercise_id}", response_model=ExerciseResponse)
def patch_exercise(exercise_id: str, body: ExerciseUpdate):
    coll = db.database().exercises
    row = coll.find_one({"_id": exercise_id})
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    name = body.name if body.name is not None else row["name"]
    descr = body.description if body.description is not None else row.get("description")
    coll.update_one({"_id": exercise_id}, {"$set": {"name": name, "description": descr}})
    row = coll.find_one({"_id": exercise_id})
    return ExerciseResponse(id=str(row["_id"]), name=row["name"], description=row.get("description"))


@app.delete("/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise(exercise_id: str):
    if db.database().workouts.count_documents({"items.exercise_id": exercise_id}, limit=1) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Упражнение используется в тренировках",
        )
    res = db.database().exercises.delete_one({"_id": exercise_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/workouts", response_model=WorkoutResponse, status_code=status.HTTP_201_CREATED)
def create_workout(body: WorkoutCreate, user_id: str = Depends(get_current_user_id)):
    wdate = body.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    wid = str(uuid4())
    now = datetime.now(timezone.utc)
    doc = {
        "_id": wid,
        "user_id": user_id,
        "name": body.name,
        "workout_date": wdate,
        "items": [],
        "created_at": now,
    }
    try:
        db.database().workouts.insert_one(doc)
    except OperationFailure as e:
        _rethrow_schema(e)
    return WorkoutResponse(id=wid, user_id=user_id, name=body.name, date=wdate, exercise_ids=[])


@app.post("/workouts/{workout_id}/exercises", response_model=WorkoutResponse)
def add_exercise_to_workout(workout_id: str, body: ExerciseToWorkout, user_id: str = Depends(get_current_user_id)):
    coll = db.database().workouts
    w = coll.find_one({"_id": workout_id})
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тренировка не найдена")
    if w["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")
    if not db.database().exercises.find_one({"_id": body.exercise_id}, {"_id": 1}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Упражнение не найдено")
    items = list(w.get("items") or [])
    npos = max((i["position"] for i in items), default=-1) + 1
    items.append({"exercise_id": body.exercise_id, "position": npos})
    try:
        coll.update_one({"_id": workout_id}, {"$set": {"items": items}})
    except OperationFailure as e:
        _rethrow_schema(e)
    w = coll.find_one({"_id": workout_id})
    return WorkoutResponse(
        id=str(w["_id"]),
        user_id=w["user_id"],
        name=w["name"],
        date=w["workout_date"],
        exercise_ids=_workout_exercise_ids(w.get("items") or []),
    )


@app.get("/users/me/workouts", response_model=list[WorkoutResponse])
def get_my_workouts(user_id: str = Depends(get_current_user_id)):
    cur = db.database().workouts.find({"user_id": user_id}).sort([("workout_date", -1), ("created_at", -1)])
    out = []
    for w in cur:
        out.append(
            WorkoutResponse(
                id=str(w["_id"]),
                user_id=w["user_id"],
                name=w["name"],
                date=w["workout_date"],
                exercise_ids=_workout_exercise_ids(w.get("items") or []),
            )
        )
    return out


@app.get("/users/me/workouts/statistics", response_model=WorkoutStatistics)
def get_workout_statistics(
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    start = period_start or "0000-01-01"
    end = period_end or "9999-12-31"
    coll = db.database().workouts
    q = {"user_id": user_id, "workout_date": {"$gte": start, "$lte": end}}
    tw = coll.count_documents(q)
    pipeline = [
        {"$match": q},
        {"$project": {"n": {"$size": {"$ifNull": ["$items", []]}}}},
        {"$group": {"_id": None, "te": {"$sum": "$n"}}},
    ]
    agg = list(coll.aggregate(pipeline))
    te = int(agg[0]["te"]) if agg else 0
    return WorkoutStatistics(
        user_id=user_id,
        period_start=start,
        period_end=end,
        total_workouts=int(tw),
        total_exercises=te,
    )
