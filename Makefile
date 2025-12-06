.PHONY: help install install-dev test lint format typecheck security clean build docs

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
ISORT := isort
MYPY := mypy

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ General

help: ## Mostrar esta ayuda
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Instalar el proyecto en modo normal
	@echo "$(GREEN)Installing py-strava...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: ## Instalar el proyecto en modo desarrollo (con dependencias dev)
	@echo "$(GREEN)Installing py-strava in development mode...$(NC)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)Development installation complete!$(NC)"

install-all: ## Instalar todo (dev + postgres)
	@echo "$(GREEN)Installing py-strava with all extras...$(NC)"
	$(PIP) install -e ".[dev,postgres]"
	@echo "$(GREEN)Full installation complete!$(NC)"

install-pre-commit: ## Instalar y configurar pre-commit hooks
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	$(PIP) install pre-commit
	pre-commit install
	@echo "$(GREEN)Pre-commit hooks installed!$(NC)"

##@ Testing

test: ## Ejecutar todos los tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTEST) tests/ -v

test-cov: ## Ejecutar tests con cobertura
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(PYTEST) tests/ -v --cov=py_strava --cov-report=term --cov-report=html --cov-report=xml

test-quick: ## Ejecutar tests rápidos (solo unitarios)
	@echo "$(GREEN)Running quick tests...$(NC)"
	$(PYTEST) tests/unit/ -v

test-integration: ## Ejecutar tests de integración
	@echo "$(GREEN)Running integration tests...$(NC)"
	$(PYTEST) tests/integration/ -v

test-watch: ## Ejecutar tests en modo watch (requiere pytest-watch)
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	ptw -- tests/ -v

##@ Code Quality

lint: ## Ejecutar linting con flake8
	@echo "$(GREEN)Running flake8 linting...$(NC)"
	$(FLAKE8) py_strava/ --count --select=E9,F63,F7,F82 --show-source --statistics
	$(FLAKE8) py_strava/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Formatear código con black e isort
	@echo "$(GREEN)Formatting code with black...$(NC)"
	$(BLACK) py_strava/ tests/
	@echo "$(GREEN)Sorting imports with isort...$(NC)"
	$(ISORT) py_strava/ tests/

format-check: ## Verificar formato sin modificar
	@echo "$(GREEN)Checking code format...$(NC)"
	$(BLACK) --check py_strava/ tests/
	$(ISORT) --check-only py_strava/ tests/

typecheck: ## Ejecutar type checking con mypy
	@echo "$(GREEN)Running type checking with mypy...$(NC)"
	$(MYPY) py_strava/ --ignore-missing-imports

security: ## Ejecutar checks de seguridad con bandit
	@echo "$(GREEN)Running security checks with bandit...$(NC)"
	bandit -r py_strava/ -ll

security-full: ## Ejecutar checks de seguridad completos (bandit + safety)
	@echo "$(GREEN)Running full security checks...$(NC)"
	bandit -r py_strava/ -ll
	safety check --json

quality: lint format-check typecheck security ## Ejecutar todos los checks de calidad

pre-commit: ## Ejecutar pre-commit hooks en todos los archivos
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files

##@ Build & Deploy

build: clean ## Build del paquete
	@echo "$(GREEN)Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)Build complete! Check dist/ directory$(NC)"

build-check: build ## Build y validar con twine
	@echo "$(GREEN)Checking built package...$(NC)"
	twine check dist/*

install-from-build: build ## Instalar desde el paquete construido
	@echo "$(GREEN)Installing from built package...$(NC)"
	$(PIP) install dist/*.whl --force-reinstall

publish-test: build-check ## Publicar en Test PyPI
	@echo "$(YELLOW)Publishing to Test PyPI...$(NC)"
	twine upload --repository testpypi dist/*

publish: build-check ## Publicar en PyPI (CUIDADO!)
	@echo "$(RED)WARNING: This will publish to PyPI!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		twine upload dist/*; \
	fi

##@ Development

run: ## Ejecutar CLI (strava --help)
	@echo "$(GREEN)Running strava CLI...$(NC)"
	strava --help

init-db: ## Inicializar base de datos
	@echo "$(GREEN)Initializing database...$(NC)"
	strava init-db --verify

sync: ## Sincronizar actividades de Strava
	@echo "$(GREEN)Syncing Strava activities...$(NC)"
	strava sync

report: ## Generar reporte
	@echo "$(GREEN)Generating report...$(NC)"
	strava report

dev-setup: install-dev install-pre-commit ## Setup completo para desarrollo
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "$(GREEN)Run 'make test' to verify everything works$(NC)"

##@ Cleanup

clean: ## Limpiar archivos temporales
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage coverage.xml
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-all: clean ## Limpiar todo incluyendo venv
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	rm -rf venv/
	@echo "$(GREEN)Deep cleanup complete!$(NC)"

##@ Documentation

docs: ## Generar documentación (placeholder)
	@echo "$(GREEN)Generating documentation...$(NC)"
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

docs-serve: ## Servir documentación localmente (placeholder)
	@echo "$(GREEN)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation serving not yet implemented$(NC)"

##@ Utilities

version: ## Mostrar versión del proyecto
	@echo "$(GREEN)py-strava version:$(NC)"
	@strava --version || echo "$(RED)CLI not installed. Run 'make install' first$(NC)"

check-tools: ## Verificar que todas las herramientas estén instaladas
	@echo "$(GREEN)Checking required tools...$(NC)"
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "$(RED)Python not found!$(NC)"; exit 1; }
	@command -v $(PIP) >/dev/null 2>&1 || { echo "$(RED)Pip not found!$(NC)"; exit 1; }
	@echo "$(GREEN)All required tools are installed!$(NC)"

update-deps: ## Actualizar dependencias
	@echo "$(GREEN)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements/dev.txt

list-deps: ## Listar dependencias instaladas
	@echo "$(GREEN)Installed dependencies:$(NC)"
	$(PIP) list

freeze-deps: ## Congelar dependencias actuales
	@echo "$(GREEN)Freezing dependencies...$(NC)"
	$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)Dependencies frozen to requirements-frozen.txt$(NC)"

##@ Git

git-status: ## Mostrar estado de git
	@git status

git-log: ## Mostrar últimos 10 commits
	@git log --oneline -10

tag: ## Crear tag de versión (uso: make tag VERSION=v2.2.0)
	@if [ -z "$(VERSION)" ]; then \
		echo "$(RED)ERROR: VERSION not specified. Usage: make tag VERSION=v2.2.0$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Creating tag $(VERSION)...$(NC)"
	git tag -a $(VERSION) -m "Release $(VERSION)"
	@echo "$(GREEN)Tag $(VERSION) created. Push with: git push origin $(VERSION)$(NC)"

##@ CI/CD

ci-local: quality test-cov ## Simular CI localmente
	@echo "$(GREEN)Local CI simulation complete!$(NC)"

ci-build: build-check ## Simular build de CI
	@echo "$(GREEN)CI build simulation complete!$(NC)"

# Default target
.DEFAULT_GOAL := help
