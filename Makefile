.PHONY: help install install-dev test lint format clean package deploy

help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test          Run tests with coverage"
	@echo "  lint          Run linting"
	@echo "  format        Format code with black"
	@echo "  clean         Remove build artifacts"
	@echo "  package       Package Lambda functions"
	@echo "  deploy        Deploy infrastructure"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest

lint:
	flake8 src tests
	mypy src --ignore-missing-imports

format:
	black src tests

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov **/__pycache__

package:
	python scripts/package_lambda.py

deploy:
	python scripts/deploy.py
