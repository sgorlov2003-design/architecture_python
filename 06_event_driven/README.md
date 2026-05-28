# Домашнее задание 06: Проектирование Event-Driven архитектуры

**Вариант:** 14 — система учёта тренировок и упражнений (фитнес-трекер)  
**Автор:** Горлов Степан Николаевич, М8О-106СВ-25

## Описание проекта

Событийно-ориентированная архитектура для фитнес-трекера: Apache Kafka, паттерн CQRS, producer/consumer на C++ (POCO, librdkafka).

Документация:
- [event_driven_design.md](event_driven_design.md) — архитектура, CQRS, брокер, гарантии доставки
- [event_catalog.md](event_catalog.md) — каталог событий (payload, производители, потребители)

Спецификация REST API (контекст команд, порождающих события): [openapi.yaml](openapi.yaml).

## Требования

- Docker и Docker Compose
- Утилита `make` (или команды из раздела ниже вручную)
- Свободные порты: **2181**, **9092**, **29092**, **8081**

## Запуск

```bash
make build
make run
```

Или по шагам:

```bash
docker compose up -d zookeeper kafka kafka-ui
docker compose run --rm fitness-events
docker compose logs fitness-events
```

Остановка и очистка:

```bash
make clean
```

Kafka UI: http://localhost:8081 — топик `fitness_tracker_events`.

Демо-приложение публикует события `UserRegistered`, `ExerciseCreated`, `WorkoutCreated`, `ExerciseAddedToWorkout` и обрабатывает их в consumer (логи в stdout).

## Сборка локально (без Docker)

Ubuntu 22.04 / Debian:

```bash
sudo apt-get install -y cmake g++ pkg-config libssl-dev zlib1g-dev \
  libpoco-dev librdkafka-dev
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release && make -j
export KAFKA_BROKERS=localhost:9092
export KAFKA_TOPIC=fitness_tracker_events
export KAFKA_GROUP_ID=fitness_demo_group
./fitness_events_demo
```

Перед запуском должен быть доступен брокер Kafka (`docker compose up -d zookeeper kafka`).
