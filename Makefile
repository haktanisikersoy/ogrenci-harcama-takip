# Kısayol komutlar: make lint, make test, make check
.PHONY: install run lint format test check

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
