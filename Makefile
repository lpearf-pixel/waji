.PHONY: up down logs backend-check ai-check edge-check check

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

backend-check:
	cd apps/platform && python manage.py check

ai-check:
	python -m compileall services/audio_ai/app

edge-check:
	cd edge/agent && cargo check

check: backend-check ai-check edge-check
