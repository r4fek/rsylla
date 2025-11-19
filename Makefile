.PHONY: help build develop install test test-quick test-all clean fmt lint examples docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make build        - Build the package in release mode"
	@echo "  make develop      - Install in development mode"
	@echo "  make install      - Install the package"
	@echo "  make test         - Run integration tests (requires ScyllaDB)"
	@echo "  make test-quick   - Run tests without rebuilding"
	@echo "  make test-all     - Run full test suite with coverage"
	@echo "  make docker-up    - Start ScyllaDB container"
	@echo "  make docker-down  - Stop ScyllaDB container"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make fmt          - Format code"
	@echo "  make lint         - Run linters"
	@echo "  make examples     - Run all examples"

build:
	maturin build --release

develop:
	maturin develop

install:
	maturin build --release
	pip install target/wheels/*.whl

test:
	./run_tests.sh

test-quick:
	pytest tests/ -v -m integration

test-all:
	pytest tests/ -v --tb=long

docker-up:
	docker compose up -d
	@echo "Waiting for ScyllaDB..."
	@sleep 30

docker-down:
	docker compose down -v

clean:
	cargo clean
	rm -rf target/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.so" -delete

fmt:
	cargo fmt
	black python/ examples/

lint:
	cargo clippy -- -D warnings
	black --check python/ examples/

examples:
	@echo "Running basic_usage example..."
	python examples/basic_usage.py
	@echo "\nRunning prepared_statements example..."
	python examples/prepared_statements.py
	@echo "\nRunning batch_operations example..."
	python examples/batch_operations.py
	@echo "\nRunning advanced_configuration example..."
	python examples/advanced_configuration.py
