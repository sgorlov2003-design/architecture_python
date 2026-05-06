"""DTO (Pydantic) для API."""
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    login: str = Field(..., min_length=1, examples=["ivan_petrov"])
    password: str = Field(..., min_length=1, examples=["secret123"])
    first_name: str = Field(..., min_length=1, examples=["Иван"])
    last_name: str = Field(..., min_length=1, examples=["Петров"])


class UserResponse(BaseModel):
    id: str
    login: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Приседания"])
    description: Optional[str] = Field(None, examples=["Базовое упражнение"])


class ExerciseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class WorkoutCreate(BaseModel):
    name: str = Field(..., min_length=1, examples=["Утренняя тренировка"])
    date: Optional[str] = Field(None, examples=["2025-03-18"])


class WorkoutResponse(BaseModel):
    id: str
    user_id: str
    name: str
    date: str
    exercise_ids: list[str] = []


class ExerciseToWorkout(BaseModel):
    exercise_id: str


class WorkoutStatistics(BaseModel):
    user_id: str
    period_start: str
    period_end: str
    total_workouts: int
    total_exercises: int
