.PHONY: install lint type-check test test-integration format check clean docker-up docker-down validate-canon check-residue check-emdash

VENV_PYTHON = .venv/Scripts/python
VENV_PIP = .venv/Scripts/pip

install:
	python -m venv .venv
	$(VENV_PIP) install -r requirements-dev.txt
	$(VENV_PIP) install -e .

lint:
	$(VENV_PYTHON) -m ruff check src/ tests/

type-check:
	$(VENV_PYTHON) -m mypy src/

test:
	$(VENV_PYTHON) -m pytest tests/ -v

format:
	$(VENV_PYTHON) -m ruff format src/ tests/

test-integration:
	@echo "Integration tests not yet implemented (Phase 2+)"

check: lint type-check test

clean:
	rm -rf __pycache__ .mypy_cache .ruff_cache .pytest_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-up:
	@echo "Docker not yet configured (Phase 7+)"

docker-down:
	@echo "Docker not yet configured (Phase 7+)"

validate-canon:
	$(VENV_PYTHON) -m starry_lyfe.canon.validator

check-residue:
	$(VENV_PYTHON) -m pytest tests/unit/test_residue_grep.py -v

check-emdash:
	$(VENV_PYTHON) -m pytest tests/unit/test_emdash_ban.py -v
