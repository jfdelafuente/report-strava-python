# Requirements

Este directorio contiene las dependencias del proyecto organizadas por entorno.

## Archivos

### `base.txt`
Dependencias core necesarias para ejecutar el proyecto en producción.

```bash
pip install -r requirements/base.txt
```

**Incluye**:
- pandas (análisis de datos)
- numpy (cálculos numéricos)
- requests (HTTP client)
- python-dateutil (manejo de fechas)
- click (CLI framework)

### `dev.txt`
Dependencias de desarrollo (incluye base.txt + herramientas de desarrollo).

```bash
pip install -r requirements/dev.txt
```

**Incluye todo de base.txt más**:
- pytest, pytest-cov (testing)
- mypy (type checking)
- black (code formatter)
- flake8 (linting)
- isort (import sorting)

### `postgres.txt`
Dependencias opcionales para soporte de PostgreSQL.

```bash
pip install -r requirements/postgres.txt
```

**Incluye base.txt más**:
- psycopg2-binary (PostgreSQL driver)

## Instalación Rápida

### Desarrollo
```bash
# Instalar con todas las herramientas de desarrollo
pip install -r requirements/dev.txt
```

### Producción (solo dependencias core)
```bash
pip install -r requirements/base.txt
```

### Con PostgreSQL
```bash
pip install -r requirements/postgres.txt
```

### Desde setup.py (recomendado)
```bash
# Modo desarrollo (editable)
pip install -e .

# Con extras de desarrollo
pip install -e ".[dev]"

# Con soporte PostgreSQL
pip install -e ".[postgres]"

# Todo junto
pip install -e ".[dev,postgres]"
```

## Actualizar Dependencias

Para actualizar todas las dependencias a sus versiones más recientes:

```bash
pip install -U -r requirements/base.txt
```

## Sincronización con pyproject.toml

Las dependencias están definidas tanto aquí como en `pyproject.toml`. Mantener ambos sincronizados:

- `requirements/base.txt` ↔ `[project.dependencies]`
- `requirements/dev.txt` ↔ `[project.optional-dependencies.dev]`
- `requirements/postgres.txt` ↔ `[project.optional-dependencies.postgres]`
