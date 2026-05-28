# Каталог событий (Event Catalog)

## UserRegistered

| Параметр | Описание |
|----------|----------|
| Название события | UserRegistered |
| Структура payload | user_id (uuid), login (string), first_name (string), last_name (string) |
| Производитель события | User Service (POST /users) |
| Потребители события | NotificationService, AnalyticsService |
| Гарантии доставки | exactly-once при публикации, at-least-once при потреблении с дедупликацией |

## ExerciseCreated

| Параметр | Описание |
|----------|----------|
| Название события | ExerciseCreated |
| Структура payload | exercise_id (uuid), user_id (uuid), name (string), category (string, optional) |
| Производитель события | Exercise Service (POST /exercises) |
| Потребители события | SearchIndexService, AnalyticsService, AuditService |
| Гарантии доставки | exactly-once при публикации, at-least-once при потреблении с дедупликацией |

## ExerciseUpdated

| Параметр | Описание |
|----------|----------|
| Название события | ExerciseUpdated |
| Структура payload | exercise_id (uuid), user_id (uuid), updated_fields (array of string), name (string), updated_at (timestamp) |
| Производитель события | Exercise Service (PATCH /exercises/{id}) |
| Потребители события | CacheInvalidationService, SearchIndexService |
| Гарантии доставки | exactly-once при публикации, at-least-once при потреблении с дедупликацией |

## WorkoutCreated

| Параметр | Описание |
|----------|----------|
| Название события | WorkoutCreated |
| Структура payload | workout_id (uuid), user_id (uuid), name (string), date (date) |
| Производитель события | Workout Service (POST /workouts) |
| Потребители события | AnalyticsService, AuditService, StatisticsProjectionService |
| Гарантии доставки | exactly-once при публикации, at-least-once при потреблении с дедупликацией |

## ExerciseAddedToWorkout

| Параметр | Описание |
|----------|----------|
| Название события | ExerciseAddedToWorkout |
| Структура payload | workout_id (uuid), exercise_id (uuid), user_id (uuid), sets (int), reps (int), added_at (timestamp) |
| Производитель события | Workout Service (POST /workouts/{id}/exercises) |
| Потребители события | StatisticsProjectionService, CacheInvalidationService, NotificationService |
| Гарантии доставки | exactly-once при публикации, at-least-once при потреблении с дедупликацией |
