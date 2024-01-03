.PHONY: up
up:
	docker compose up --build

.PHONY: deploy
deploy:
	git pull
	docker image prune -af
	docker compose up --build --force-recreate

.PHONY: run
run: up

.PHONY: local
local:
	docker compose -f local-docker-compose.yml up -d --build
	cd app; alembic upgrade head; \
	uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

.PHONY: migrations
migrations:
	cd app; alembic revision --autogenerate -m $(m)

.PHONY: migrate
migrate:
	cd app; alembic upgrade head

.DEFAULT_GOAL := up
