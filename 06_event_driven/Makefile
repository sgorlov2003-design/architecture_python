build:
	docker compose build --no-cache fitness-events

up:
	docker compose up -d zookeeper kafka kafka-ui

demo:
	docker compose run --rm fitness-events

run: up
	@echo "Waiting for Kafka..."
	@sleep 15
	docker compose run --rm fitness-events

clean:
	docker compose down -v --remove-orphans
