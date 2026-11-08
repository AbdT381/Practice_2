.PHONY: run run-test test lint clean

run:
	python -m src.main --config config.toml

run-test:
	python -m src.main --config config_test.toml

test:
	pytest -v tests/

lint:
	python -m py_compile src/*.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
