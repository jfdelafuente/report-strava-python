# Propuesta de Reestructuración del Proyecto py-strava

## Análisis de la Estructura Actual

### Problemas Identificados

1. **Archivos duplicados/innecesarios en raíz**:
   - `py_strava__init__.py` y `py_stravastrava__init__.py` (archivos incorrectos)
   - Múltiples documentos MD sin organización clara
   - `STRAVA_DB.session.sql` en raíz (debería estar en `/bd` o `/scripts`)

2. **Documentación fragmentada**:
   - 7 archivos MD de mejoras/análisis dispersos
   - No hay separación clara entre docs de usuario y de desarrollo
   - Falta un CHANGELOG.md formal

3. **Estructura de tests inconsistente**:
   - `/test` en raíz con solo 2 archivos
   - `/py_strava/ejemplos/test` con más tests
   - No hay configuración de pytest
   - Falta separación entre tests unitarios e integración

4. **Código de ejemplo desorganizado**:
   - `/py_strava/ejemplos` mezclado con código principal
   - Scripts de ejemplo sin documentación clara
   - Algunos ejemplos están obsoletos

5. **Configuración y credenciales**:
   - Archivos de configuración en múltiples ubicaciones
   - No hay `.env.example` para facilitar setup
   - Falta `.gitignore` robusto

6. **Scripts de utilidad en raíz**:
   - `init_database.py`, `ejemplo_uso_bd.py`, `test_setup.py` sin organizar
   - Deberían estar en un directorio `/scripts` o `/tools`

7. **Módulo `strava_token_1.py`**:
   - Nombre inconsistente (¿por qué el `_1`?)
   - Sugiere versiones antiguas sin limpiar

## Estructura Propuesta

```
report-strava-python/
│
├── .github/                          # CI/CD y GitHub workflows (opcional)
│   └── workflows/
│       ├── tests.yml
│       └── lint.yml
│
├── docs/                             # Documentación organizada
│   ├── user/                         # Documentación para usuarios
│   │   ├── README.md                 # Guía de usuario
│   │   ├── INICIO_RAPIDO.md
│   │   ├── CONFIGURACION.md          # Setup detallado
│   │   └── SOLUCION_ERRORES.md
│   │
│   ├── dev/                          # Documentación para desarrolladores
│   │   ├── ARQUITECTURA.md           # Decisiones de diseño
│   │   ├── CONTRIBUIR.md             # Guía de contribución
│   │   ├── MEJORAS_IMPLEMENTADAS.md  # Consolidación de MEJORAS*.md
│   │   └── API.md                    # Documentación de módulos
│   │
│   └── database/                     # Documentación de BD
│       ├── SCHEMA.md                 # Estructura de tablas
│       ├── MIGRACIONES.md
│       └── INIT_DATABASE.md
│
├── scripts/                          # Scripts de utilidad
│   ├── init_database.py              # Mover desde raíz
│   ├── ejemplo_uso_bd.py             # Mover desde raíz
│   ├── setup_project.py              # Nuevo: setup automatizado
│   ├── migrate_db.py                 # Nuevo: migraciones
│   └── validate_tokens.py            # Nuevo: validar configuración
│
├── tests/                            # Tests reorganizados
│   ├── __init__.py
│   ├── conftest.py                   # Configuración pytest
│   │
│   ├── unit/                         # Tests unitarios
│   │   ├── __init__.py
│   │   ├── test_strava_token.py
│   │   ├── test_strava_activities.py
│   │   ├── test_strava_fechas.py
│   │   ├── test_db_sqlite.py
│   │   └── test_db_postgres.py
│   │
│   ├── integration/                  # Tests de integración
│   │   ├── __init__.py
│   │   ├── test_sync_workflow.py
│   │   └── test_database_operations.py
│   │
│   └── fixtures/                     # Datos de prueba
│       ├── sample_activities.json
│       └── sample_tokens.json
│
├── examples/                         # Ejemplos organizados (mover desde py_strava/ejemplos)
│   ├── README.md
│   ├── basic/                        # Ejemplos básicos
│   │   ├── 01_get_token.py
│   │   ├── 02_get_activities.py
│   │   └── 03_query_database.py
│   │
│   ├── advanced/                     # Ejemplos avanzados
│   │   ├── custom_sync.py
│   │   ├── batch_operations.py
│   │   └── database_usage.py
│   │
│   └── deprecated/                   # Ejemplos antiguos (para referencia)
│       └── old_examples.txt
│
├── py_strava/                        # Paquete principal
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py                 # Nuevo: excepciones personalizadas
│   ├── constants.py                  # Nuevo: constantes compartidas
│   │
│   ├── core/                         # Lógica de negocio core
│   │   ├── __init__.py
│   │   ├── sync.py                   # Lógica de sincronización (extraer de main.py)
│   │   └── reports.py                # Lógica de informes (extraer de informe_strava.py)
│   │
│   ├── api/                          # Cliente de API Strava
│   │   ├── __init__.py
│   │   ├── client.py                 # Cliente HTTP base
│   │   ├── auth.py                   # Gestión de autenticación
│   │   ├── activities.py             # Endpoints de actividades
│   │   └── rate_limiter.py           # Nuevo: control de rate limiting
│   │
│   ├── database/                     # Capa de base de datos
│   │   ├── __init__.py
│   │   ├── schema.py                 # Mover db_schema.py aquí
│   │   ├── models.py                 # Nuevo: modelos de datos
│   │   ├── sqlite.py                 # Renombrar strava_db_sqlite.py
│   │   ├── postgres.py               # Renombrar strava_db_postgres.py
│   │   └── migrations/               # Nuevo: sistema de migraciones
│   │       ├── __init__.py
│   │       └── v1_initial.py
│   │
│   ├── utils/                        # Utilidades
│   │   ├── __init__.py
│   │   ├── dates.py                  # Renombrar strava_fechas.py
│   │   ├── logging.py                # Configuración de logging
│   │   └── validators.py             # Nuevo: validaciones
│   │
│   ├── cli/                          # Interfaz de línea de comandos
│   │   ├── __init__.py
│   │   ├── main.py                   # CLI con argparse/click
│   │   ├── commands/                 # Comandos individuales
│   │   │   ├── __init__.py
│   │   │   ├── sync.py
│   │   │   ├── report.py
│   │   │   └── init_db.py
│   │   └── output.py                 # Formateo de salida
│   │
│   └── legacy/                       # Código legacy (temporal)
│       ├── __init__.py
│       ├── main.py                   # main.py antiguo
│       └── informe_strava.py         # informe_strava.py antiguo
│
├── data/                             # Datos generados
│   ├── .gitkeep
│   └── README.md                     # Explicar qué va aquí
│
├── bd/                               # Base de datos
│   ├── .gitkeep
│   ├── postgres_credentials.json.example
│   └── README.md
│
├── json/                             # Configuración JSON
│   ├── .gitkeep
│   ├── strava_tokens.json.example
│   └── README.md
│
├── .env.example                      # Nuevo: template de variables de entorno
├── .gitignore                        # Mejorado
├── .editorconfig                     # Nuevo: consistencia de editor
├── pyproject.toml                    # Nuevo: configuración moderna de Python
├── setup.py                          # Nuevo: instalación del paquete
├── pytest.ini                        # Nuevo: configuración de pytest
├── mypy.ini                          # Nuevo: configuración de type checking
├── .flake8                           # Nuevo: configuración de linting
│
├── README.md                         # README principal (simplificado)
├── CHANGELOG.md                      # Nuevo: historial de cambios
├── LICENSE                           # Nuevo: licencia MIT
├── CONTRIBUTING.md                   # Nuevo: guía de contribución
│
└── requirements/                     # Dependencias organizadas
    ├── base.txt                      # Dependencias base
    ├── dev.txt                       # Herramientas de desarrollo
    ├── test.txt                      # Dependencias para tests
    └── prod.txt                      # Producción (PostgreSQL, etc.)
```

## Cambios Específicos por Módulo

### 1. Reestructuración de `py_strava`

#### Antes:
```python
# py_strava/strava/strava_token.py
# py_strava/strava/strava_activities.py
# py_strava/strava/strava_db_sqlite.py
# py_strava/strava/strava_db_postgres.py
# py_strava/strava/strava_fechas.py
```

#### Después:
```python
# py_strava/api/auth.py (renombrado desde strava_token.py)
# py_strava/api/activities.py (renombrado desde strava_activities.py)
# py_strava/database/sqlite.py (renombrado)
# py_strava/database/postgres.py (renombrado)
# py_strava/utils/dates.py (renombrado desde strava_fechas.py)
```

**Razones**:
- Nombres más claros y consistentes (sin prefijo `strava_` redundante)
- Agrupación lógica por responsabilidad
- Facilita imports: `from py_strava.api import auth` vs `from py_strava.strava import strava_token`

### 2. Nuevo módulo CLI

```python
# py_strava/cli/main.py
import click

@click.group()
def cli():
    """Strava Sync - Herramienta CLI para sincronizar actividades de Strava"""
    pass

@cli.command()
@click.option('--since', help='Fecha desde la cual sincronizar')
def sync(since):
    """Sincronizar actividades de Strava"""
    from py_strava.core.sync import run_sync
    run_sync(since=since)

@cli.command()
@click.option('--output', default='data/report.csv', help='Archivo de salida')
def report(output):
    """Generar informe CSV"""
    from py_strava.core.reports import generate_report
    generate_report(output)

@cli.command()
@click.option('--reset', is_flag=True, help='Resetear BD (¡cuidado!)')
def init_db(reset):
    """Inicializar base de datos"""
    from scripts.init_database import main
    main(reset=reset)

if __name__ == '__main__':
    cli()
```

**Uso**:
```bash
# En vez de: python -m py_strava.main
strava sync

# En vez de: python -m py_strava.informe_strava
strava report

# En vez de: python init_database.py
strava init-db
```

### 3. Configuración moderna con `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "py-strava"
version = "2.1.0"
description = "Sincroniza y analiza actividades de Strava"
authors = [{name = "Jose F. de la Fuente"}]
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}

dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "requests>=2.31.0",
    "python-dateutil>=2.8.2",
    "click>=8.1.0",  # Para CLI
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "mypy>=1.7.0",
    "black>=23.12.0",
    "flake8>=6.1.0",
    "isort>=5.12.0",
]
postgres = [
    "psycopg2-binary>=2.9.9",
]

[project.scripts]
strava = "py_strava.cli.main:cli"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --cov=py_strava --cov-report=html --cov-report=term"

[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 4. Sistema de excepciones personalizadas

```python
# py_strava/exceptions.py
"""Excepciones personalizadas para py-strava."""

class StravaError(Exception):
    """Excepción base para errores de Strava."""
    pass

class TokenError(StravaError):
    """Error relacionado con tokens de autenticación."""
    pass

class APIError(StravaError):
    """Error al comunicarse con la API de Strava."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)

class DatabaseError(StravaError):
    """Error de base de datos."""
    pass

class ConfigurationError(StravaError):
    """Error de configuración."""
    pass

class RateLimitError(APIError):
    """Error de límite de rate en API."""
    pass
```

### 5. Modelos de datos (opcional - para futura migración a ORM)

```python
# py_strava/database/models.py
"""Modelos de datos para la aplicación."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Activity:
    """Modelo de actividad de Strava."""
    id_activity: int
    name: str
    start_date_local: datetime
    type: str
    distance: float
    moving_time: float
    elapsed_time: float
    total_elevation_gain: float
    end_latlng: Optional[str] = None
    kudos_count: int = 0
    external_id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convierte a diccionario para insertar en BD."""
        return {
            'id_activity': self.id_activity,
            'name': self.name,
            'start_date_local': self.start_date_local.isoformat(),
            'type': self.type,
            'distance': self.distance,
            'moving_time': self.moving_time,
            'elapsed_time': self.elapsed_time,
            'total_elevation_gain': self.total_elevation_gain,
            'end_latlng': self.end_latlng,
            'kudos_count': self.kudos_count,
            'external_id': self.external_id,
        }

@dataclass
class Kudo:
    """Modelo de kudo."""
    resource_state: str
    firstname: str
    lastname: str
    id_activity: int
    id_kudos: Optional[int] = None
```

### 6. Archivo `.env.example`

```bash
# Configuración de Base de Datos
DB_TYPE=sqlite  # sqlite o postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=strava
DB_USER=postgres
DB_PASSWORD=

# Rutas de archivos SQLite
SQLITE_DB_PATH=./bd/strava.sqlite

# Configuración de Strava API
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=

# Configuración de Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./data/strava.log

# Configuración de Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=900
```

### 7. Archivo `.gitignore` mejorado

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Datos sensibles
bd/*.sqlite
bd/*.sqlite-*
bd/postgres_credentials.json
json/strava_tokens.json
.env

# Datos generados
data/*.csv
data/*.log
data/*.json

# Tests
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# Sistema
.DS_Store
Thumbs.db

# Mantener estructura de directorios
!bd/.gitkeep
!data/.gitkeep
!json/.gitkeep
```

## Plan de Migración

### Fase 1: Preparación (Sin romper nada)
1. Crear nueva estructura de directorios
2. Crear archivos de configuración (`pyproject.toml`, `.env.example`, etc.)
3. Mover documentación a `/docs`
4. Mover scripts a `/scripts`
5. Consolidar tests en `/tests`

### Fase 2: Reorganización de código
1. Crear módulos nuevos (`api/`, `database/`, `utils/`, `core/`)
2. Copiar (no mover) archivos a nuevas ubicaciones
3. Actualizar imports en nuevos módulos
4. Mantener módulos antiguos funcionando (en `/legacy`)

### Fase 3: Actualización de interfaces
1. Implementar nuevo CLI con Click
2. Crear alias/wrappers para mantener compatibilidad
3. Actualizar documentación

### Fase 4: Limpieza
1. Deprecar módulos legacy
2. Eliminar archivos duplicados
3. Eliminar código no usado
4. Actualizar README y documentación final

### Fase 5: Testing y validación
1. Ejecutar suite completa de tests
2. Validar que todo funciona igual
3. Actualizar CI/CD si existe
4. Crear release v2.1.0

## Beneficios de la Reestructuración

### 1. Mantenibilidad
- **Separación clara de responsabilidades**: Cada módulo tiene un propósito específico
- **Código más testeable**: Estructura facilita tests unitarios
- **Menos acoplamiento**: Módulos independientes y reutilizables

### 2. Escalabilidad
- **Fácil añadir features**: Nueva funcionalidad tiene un lugar claro
- **Soporte para múltiples BD**: Abstracción clara de capa de datos
- **API extensible**: Nuevos endpoints de Strava fáciles de añadir

### 3. Experiencia de desarrollo
- **Setup más rápido**: `.env.example` y scripts de setup
- **Desarrollo más ágil**: Hot reload, tests rápidos
- **Onboarding facilitado**: Documentación organizada

### 4. Experiencia de usuario
- **CLI intuitivo**: Comandos claros tipo `strava sync`
- **Instalación estándar**: `pip install -e .` o `pip install py-strava`
- **Mejor documentación**: Separada para usuarios y desarrolladores

### 5. Profesionalismo
- **Estructura estándar**: Sigue convenciones de Python
- **Tooling moderno**: pyproject.toml, type hints, linting
- **Preparado para distribución**: Puede publicarse en PyPI

## Comparación Antes/Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Estructura** | Plana, archivos dispersos | Jerárquica, organizada por función |
| **Documentación** | 7 archivos MD en raíz | Organizada en `/docs` por audiencia |
| **Tests** | 2 ubicaciones, sin pytest | Unificados en `/tests` con pytest |
| **CLI** | `python -m py_strava.main` | `strava sync` (instalable) |
| **Configuración** | `requirements.txt` | `pyproject.toml` moderno |
| **Imports** | `from py_strava.strava import strava_token` | `from py_strava.api import auth` |
| **Ejemplos** | Mezclados con código | Separados en `/examples` |
| **Scripts** | En raíz del proyecto | Organizados en `/scripts` |
| **Dependencias** | Un archivo requirements.txt | Separadas por entorno |
| **Instalación** | Manual, compleja | `pip install -e .` |

## Ejemplo de Uso Después de la Reestructuración

### Instalación
```bash
# Clonar repositorio
git clone https://gitlab.com/josefcodelafuente/py-strava.git
cd py-strava

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar proyecto en modo desarrollo
pip install -e ".[dev]"

# Copiar configuración ejemplo
cp .env.example .env
cp json/strava_tokens.json.example json/strava_tokens.json

# Editar configuración
nano .env
nano json/strava_tokens.json

# Inicializar base de datos
strava init-db
```

### Uso diario
```bash
# Sincronizar actividades
strava sync

# Generar informe
strava report --output mi_informe.csv

# Ver ayuda
strava --help

# Modo debug
strava --log-level DEBUG sync
```

### Desarrollo
```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov

# Type checking
mypy py_strava

# Linting
black py_strava
flake8 py_strava
isort py_strava

# Todo junto (pre-commit)
black py_strava && isort py_strava && flake8 py_strava && mypy py_strava && pytest
```

## Próximos Pasos Recomendados

1. **Revisar propuesta** con el equipo
2. **Crear branch** `feature/restructure-project`
3. **Implementar Fase 1** (sin romper nada)
4. **Validar** que todo sigue funcionando
5. **Continuar con Fases 2-5** incrementalmente
6. **Crear PR** con revisión exhaustiva
7. **Merge** y crear release v2.1.0

## Notas Adicionales

### Archivos a eliminar
- `py_strava__init__.py` (incorrecto)
- `py_stravastrava__init__.py` (incorrecto)
- `STRAVA_DB.session.sql` (mover o eliminar)
- `py_strava/strava/strava_token_1.py` (si está duplicado)

### Archivos a consolidar
Crear un solo `docs/dev/MEJORAS_IMPLEMENTADAS.md` consolidando:
- `MEJORAS.md`
- `MEJORAS_MODULOS_DATABASE.md`
- `MEJORAS_STRAVA_DB_SQLITE.md`
- `MEJORAS_STRAVA_TOKEN_Y_MAIN.md`
- `ANALISIS_MEJORAS_POSTGRES.md`
- `RESUMEN_CAMBIOS.md`

### Retrocompatibilidad
Durante la migración, mantener wrappers en `/legacy` para evitar romper código existente:

```python
# py_strava/legacy/main.py
"""
Wrapper para mantener compatibilidad con versión anterior.
DEPRECADO: Usa 'strava sync' en su lugar.
"""
import warnings
from py_strava.core.sync import run_sync

warnings.warn(
    "python -m py_strava.main está deprecado. Usa 'strava sync'",
    DeprecationWarning,
    stacklevel=2
)

if __name__ == '__main__':
    run_sync()
```

---

**Versión**: 1.0
**Fecha**: 3 de diciembre de 2025
**Autor**: Análisis de Claude Code
