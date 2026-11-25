# Kısayol komutlar: make lint, make test, make check, make docker-run
.PHONY: install run lint format test check docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python app.py

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

test:
	pytest

check: lint test

docker-build:
	docker build -t ogrenci-harcama-takip .

docker-run: docker-build
	docker run --rm -p 8000:8000 -v harcama-veri:/app/instance ogrenci-harcama-takip
