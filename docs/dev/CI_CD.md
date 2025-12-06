# CI/CD - Integración y Despliegue Continuo

**Versión**: 2.2.0
**Última actualización**: 3 de diciembre de 2025

---

## Resumen

Este documento describe la configuración de CI/CD (Continuous Integration / Continuous Deployment) del proyecto **py-strava**.

El proyecto está configurado para funcionar con:
- **GitLab CI/CD** (`.gitlab-ci.yml`)
- **GitHub Actions** (`.github/workflows/ci.yml`)
- **Pre-commit Hooks** (`.pre-commit-config.yaml`)
- **Makefile** (comandos de desarrollo)

---

## Tabla de Contenidos

1. [GitLab CI/CD](#gitlab-cicd)
2. [GitHub Actions](#github-actions)
3. [Pre-commit Hooks](#pre-commit-hooks)
4. [Makefile](#makefile)
5. [Tests](#tests)
6. [Despliegue](#despliegue)

---

## GitLab CI/CD

### Archivo de Configuración

**Ubicación**: [`.gitlab-ci.yml`](../../.gitlab-ci.yml)

### Stages

El pipeline de GitLab CI/CD tiene 4 stages:

1. **test** - Tests unitarios y de integración
2. **quality** - Linting, formatting, type checking, seguridad
3. **build** - Build del paquete Python
4. **deploy** - Deploy a PyPI (manual)

### Jobs Principales

#### Stage: Test

- **test:python** - Tests en Python 3.8 (obligatorio)
- **test:python3.9** - Tests en Python 3.9 (obligatorio)
- **test:python3.10** - Tests en Python 3.10 (obligatorio)
- **test:python3.11** - Tests en Python 3.11 (opcional)

#### Stage: Quality

- **lint:flake8** - Linting con flake8
- **format:black** - Verificación de formato con black
- **format:isort** - Verificación de imports con isort
- **typecheck:mypy** - Type checking con mypy
- **security:bandit** - Security scanning con bandit

#### Stage: Build

- **build:package** - Construye el paquete Python (wheel + sdist)
- **build:validate** - Valida la instalación del paquete

#### Stage: Deploy

- **deploy:pypi** - Deploy a PyPI (solo en tags, manual)
- **deploy:test-pypi** - Deploy a Test PyPI (solo en develop, manual)

### Uso

```bash
# El pipeline se ejecuta automáticamente en:
- Commits a main
- Commits a develop
- Merge requests

# Para desplegar a PyPI:
1. Crear un tag: git tag -a v2.2.0 -m "Release v2.2.0"
2. Push del tag: git push origin v2.2.0
3. Aprobar el job manual "deploy:pypi" en GitLab CI
```

### Variables de Entorno Necesarias

```plaintext
# En GitLab CI/CD Settings > Variables
PYPI_TOKEN          # Token de PyPI para deploy
TEST_PYPI_TOKEN     # Token de Test PyPI (opcional)
```

---

## GitHub Actions

### Archivo de Configuración

**Ubicación**: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)

### Workflows

El workflow de GitHub Actions incluye:

1. **test** - Tests en múltiples versiones de Python (3.8-3.11) y SO (Ubuntu, Windows, macOS)
2. **lint** - Linting con flake8
3. **format** - Verificación de formato (black + isort)
4. **typecheck** - Type checking con mypy
5. **security** - Security checks (bandit + safety)
6. **build** - Build y validación del paquete
7. **deploy** - Deploy a PyPI (solo en releases)

### Triggers

```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  release:
    types: [ created ]
```

### Matrix Testing

El proyecto se prueba en:
- **Python**: 3.8, 3.9, 3.10, 3.11
- **OS**: Ubuntu, Windows, macOS

### Uso

```bash
# El workflow se ejecuta automáticamente en:
- Push a main/develop
- Pull requests
- Creación de releases

# Para desplegar a PyPI:
1. Crear release en GitHub
2. El job deploy:pypi se ejecuta automáticamente
```

### Secrets Necesarios

```plaintext
# En GitHub Settings > Secrets and variables > Actions
PYPI_API_TOKEN      # Token de PyPI para deploy
CODECOV_TOKEN       # Token de Codecov (opcional)
```

---

## Pre-commit Hooks

### Instalación

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks en el repositorio
pre-commit install

# Ejecutar en todos los archivos (primera vez)
pre-commit run --all-files
```

### O usar Makefile

```bash
make install-pre-commit
```

### Hooks Configurados

1. **black** - Code formatting
2. **isort** - Import sorting
3. **flake8** - Linting
4. **mypy** - Type checking
5. **bandit** - Security scanning
6. **trailing-whitespace** - Eliminar espacios en blanco
7. **end-of-file-fixer** - Asegurar fin de línea
8. **check-yaml** - Validar YAML
9. **check-json** - Validar JSON
10. **check-toml** - Validar TOML
11. **check-merge-conflict** - Detectar conflictos de merge
12. **detect-private-key** - Detectar claves privadas
13. **markdownlint** - Lint Markdown
14. **pyupgrade** - Upgrade syntax a Python 3.8+
15. **pydocstyle** - Docstring style checking

### Uso

```bash
# Los hooks se ejecutan automáticamente en cada commit

# Ejecutar manualmente en todos los archivos
pre-commit run --all-files

# Ejecutar un hook específico
pre-commit run black --all-files

# Actualizar hooks a últimas versiones
pre-commit autoupdate
```

---

## Makefile

### Comandos Disponibles

#### Instalación

```bash
make install            # Instalar en modo normal
make install-dev        # Instalar en modo desarrollo
make install-all        # Instalar todo (dev + postgres)
make install-pre-commit # Instalar pre-commit hooks
```

#### Testing

```bash
make test               # Ejecutar todos los tests
make test-cov           # Tests con cobertura
make test-quick         # Tests rápidos (solo unitarios)
make test-integration   # Tests de integración
make test-watch         # Tests en modo watch
```

#### Calidad de Código

```bash
make lint               # Linting con flake8
make format             # Formatear código (black + isort)
make format-check       # Verificar formato sin modificar
make typecheck          # Type checking con mypy
make security           # Security checks con bandit
make quality            # Todos los checks de calidad
make pre-commit         # Ejecutar pre-commit hooks
```

#### Build & Deploy

```bash
make build              # Build del paquete
make build-check        # Build y validar con twine
make publish-test       # Publicar en Test PyPI
make publish            # Publicar en PyPI (¡CUIDADO!)
```

#### Development

```bash
make run                # Ejecutar CLI (strava --help)
make init-db            # Inicializar base de datos
make sync               # Sincronizar actividades
make report             # Generar reporte
make dev-setup          # Setup completo para desarrollo
```

#### Cleanup

```bash
make clean              # Limpiar archivos temporales
make clean-all          # Limpiar todo incluyendo venv
```

#### CI/CD

```bash
make ci-local           # Simular CI localmente
make ci-build           # Simular build de CI
```

#### Ayuda

```bash
make help               # Mostrar todos los comandos disponibles
```

---

## Tests

### Estructura de Tests

```
tests/
├── conftest.py          # Configuración de pytest
├── unit/                # Tests unitarios
│   ├── __init__.py
│   ├── test_version.py
│   └── test_imports.py
├── integration/         # Tests de integración
│   └── __init__.py
└── fixtures/            # Datos de prueba
```

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Con cobertura
pytest tests/ -v --cov=py_strava --cov-report=term --cov-report=html

# Solo unitarios
pytest tests/unit/ -v

# Solo integración
pytest tests/integration/ -v

# Un archivo específico
pytest tests/unit/test_version.py -v

# O usar Makefile
make test
make test-cov
```

### Configuración de Pytest

**Ubicación**: [`pytest.ini`](../../pytest.ini)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

---

## Despliegue

### Pre-requisitos

1. **Cuenta en PyPI**
   - Crear cuenta en [pypi.org](https://pypi.org)
   - Generar API token

2. **Configurar Token**

   **GitLab CI/CD**:
   ```bash
   # En GitLab: Settings > CI/CD > Variables
   PYPI_TOKEN = tu_token_aqui
   ```

   **GitHub Actions**:
   ```bash
   # En GitHub: Settings > Secrets > Actions
   PYPI_API_TOKEN = tu_token_aqui
   ```

### Proceso de Release

#### 1. Actualizar Versión

```bash
# Actualizar en:
- py_strava/cli/main.py (__version__)
- setup.py (version)
- pyproject.toml (version)
```

#### 2. Actualizar CHANGELOG

```bash
# Añadir entrada en CHANGELOG.md
## [X.Y.Z] - YYYY-MM-DD
### Added
- Feature 1
...
```

#### 3. Commit y Tag

```bash
# Commit de release
git add .
git commit -m "chore: release vX.Y.Z"

# Crear tag
git tag -a vX.Y.Z -m "Release vX.Y.Z"

# Push
git push origin main
git push origin vX.Y.Z
```

#### 4. Deploy Manual (GitLab)

```bash
# En GitLab CI/CD:
1. Ir al pipeline del tag
2. Aprobar job manual "deploy:pypi"
```

#### 4. Deploy Automático (GitHub)

```bash
# En GitHub:
1. Crear release desde el tag
2. El deploy se ejecuta automáticamente
```

### Test en Test PyPI (Recomendado)

```bash
# Build local
make build-check

# Subir a Test PyPI
make publish-test

# Verificar instalación
pip install --index-url https://test.pypi.org/simple/ py-strava

# Si todo funciona, hacer release real
```

---

## Troubleshooting

### Tests Fallan Localmente

```bash
# Reinstalar dependencias
make clean
make install-dev

# Ejecutar tests de nuevo
make test
```

### Pre-commit Hooks Fallan

```bash
# Reinstalar hooks
pre-commit uninstall
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### Build Falla

```bash
# Limpiar build anterior
make clean

# Build de nuevo
make build-check
```

### CI/CD Falla en Pipeline

```bash
# Simular CI localmente
make ci-local

# Si pasa localmente pero falla en CI:
- Verificar versión de Python
- Verificar variables de entorno
- Verificar permisos
```

---

## Mejores Prácticas

### 1. Antes de Commit

```bash
# Ejecutar pre-commit
pre-commit run --all-files

# O
make pre-commit
```

### 2. Antes de Pull Request

```bash
# Ejecutar toda la suite de calidad
make quality

# Ejecutar tests con cobertura
make test-cov
```

### 3. Antes de Release

```bash
# Simular CI completo
make ci-local

# Build y validar
make build-check
```

### 4. Durante Desarrollo

```bash
# Tests en modo watch
make test-watch

# Formatear código automáticamente
make format
```

---

## Referencias

### Documentación Externa

- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Pre-commit](https://pre-commit.com/)
- [Pytest](https://docs.pytest.org/)
- [Python Packaging](https://packaging.python.org/)
- [PyPI](https://pypi.org/)

### Documentación del Proyecto

- [CHANGELOG.md](../../CHANGELOG.md)
- [ARQUITECTURA.md](ARQUITECTURA.md)
- [README.md](../../README.md)

---

**Última actualización**: 3 de diciembre de 2025
**Versión del documento**: 1.0
