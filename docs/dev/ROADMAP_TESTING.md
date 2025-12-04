# Roadmap de Testing - py-strava

## 📋 Índice

- [Estado Actual](#estado-actual)
- [Fase 1: Tests Unitarios Básicos ✅ COMPLETADO](#fase-1-tests-unitarios-básicos--completado)
- [Fase 2: Tests de Módulos Core 🚧 EN PROGRESO](#fase-2-tests-de-módulos-core--en-progreso)
- [Fase 3: Tests de Integración](#fase-3-tests-de-integración)
- [Fase 4: Tests End-to-End](#fase-4-tests-end-to-end)
- [Fase 5: CI/CD y Automatización](#fase-5-cicd-y-automatización)

---

## 📊 Estado Actual

### Métricas Globales

| Métrica | Valor |
|---------|-------|
| **Tests totales** | 83 tests ✅ |
| **Tests pasando** | 100% (83/83) |
| **Cobertura global** | 22% |
| **Tiempo de ejecución** | ~2.6 segundos |

### Cobertura por Módulo

| Módulo | Cobertura | Estado |
|--------|-----------|--------|
| `py_strava/config.py` | 100% | ✅ Completo |
| `py_strava/database/sqlite.py` | 91% | ✅ Casi completo |
| `py_strava/core/reports.py` | 90% | ✅ Casi completo |
| `py_strava/database/schema.py` | 53% | ⚠️ Parcial |
| `py_strava/api/auth.py` | 17% | ❌ Sin tests |
| `py_strava/core/sync.py` | 16% | ❌ Sin tests |
| `py_strava/cli/commands/*` | 13-25% | ❌ Sin tests |

---

## Fase 1: Tests Unitarios Básicos ✅ COMPLETADO

### Objetivos
Establecer la base de testing con los módulos más críticos y estables del proyecto.

### ✅ Completado (Diciembre 2025)

#### 1.1 Configuración de Pytest ✅
- [x] Instalación de pytest y pytest-cov
- [x] Configuración de pytest.ini con marcadores personalizados
- [x] Configuración de filterwarnings para deprecation warnings
- [x] Setup de estructura de directorios tests/unit/

#### 1.2 Fixtures y Utilidades ✅
**Archivo**: `tests/conftest.py`

- [x] `project_root` - Raíz del proyecto
- [x] `sample_db_path` - Path a BD temporal
- [x] `temp_data_dir` - Directorio temporal para datos
- [x] `temp_json_dir` - Directorio temporal para JSON
- [x] `temp_bd_dir` - Directorio temporal para BD
- [x] `test_database` - BD SQLite con esquema completo
- [x] `sample_activity_data` - Datos de actividad de ejemplo
- [x] `sample_kudo_data` - Datos de kudo de ejemplo
- [x] `sample_token_data` - Datos de token de ejemplo
- [x] `mock_strava_activities` - Actividades mock de Strava API

#### 1.3 Tests de Configuración ✅
**Archivo**: `tests/unit/test_config.py` (11 tests)

- [x] Imports de módulo
- [x] Directorios base existen
- [x] BASE_DIR apunta a raíz del proyecto
- [x] Rutas de archivos definidas correctamente
- [x] Estructura de rutas correcta
- [x] Configuración de logging
- [x] Configuración de PostgreSQL
- [x] Configuración de Strava API
- [x] Variables de entorno
- [x] Conversión de Path a string
- [x] Inmutabilidad de configuración

#### 1.4 Tests de Base de Datos SQLite ✅
**Archivo**: `tests/unit/test_database_sqlite.py` (28 tests)

**Connection Management** (5 tests)
- [x] sql_connection crea BD
- [x] Foreign keys habilitadas
- [x] Row factory configurado
- [x] DatabaseConnection context manager
- [x] Auto-commit en context manager

**Execute Operations** (3 tests)
- [x] Execute query simple
- [x] Execute con parámetros
- [x] Comportamiento de commit

**Insert Operations** (4 tests)
- [x] Insert single record
- [x] Insert retorna lastrowid
- [x] Insert many records
- [x] Insert many con lista vacía

**Fetch Operations** (4 tests)
- [x] Fetch all records
- [x] Fetch con parámetros
- [x] Fetch one single result
- [x] Fetch one sin resultados

**Update Operations** (3 tests)
- [x] Update single field
- [x] Update multiple fields
- [x] Update retorna filas afectadas

**Create Table** (2 tests)
- [x] Create table simple
- [x] Create table IF NOT EXISTS

**Insert Statement** (2 tests)
- [x] Generación de insert statement
- [x] Insert statement con commit

**Commit Function** (2 tests)
- [x] Commit con statement y params
- [x] Commit con tupla format

**Error Handling** (3 tests)
- [x] SQL inválido lanza error
- [x] Insert en tabla inexistente lanza error
- [x] Fetch de tabla inexistente lanza error

#### 1.5 Tests de Schema de Base de Datos ✅
**Archivo**: `tests/unit/test_database_schema.py` (18 tests)

**Schema Constants** (4 tests)
- [x] CREATE_TABLE_ACTIVITIES definido
- [x] CREATE_TABLE_KUDOS definido
- [x] DROP TABLE statements definidos
- [x] Alias SQL para CLI definidos

**Activities Table** (4 tests)
- [x] Creación de tabla Activities
- [x] Columnas de Activities
- [x] Primary key de Activities
- [x] Inserción en Activities

**Kudos Table** (4 tests)
- [x] Creación de tabla Kudos
- [x] Columnas de Kudos
- [x] Primary key AUTOINCREMENT
- [x] Foreign key constraint

**Drop Tables** (2 tests)
- [x] Drop Activities table
- [x] Drop Kudos table

**Database Functions** (2 tests)
- [x] initialize_database crea tablas
- [x] reset_database function exists
- [x] reset_database drops y recrea

**Integration** (2 tests)
- [x] Creación de schema completo
- [x] Inserción de datos realistas

#### 1.6 Tests de Generación de Informes ✅
**Archivo**: `tests/unit/test_core_reports.py` (26 tests)

**Module Structure** (2 tests)
- [x] Imports de módulo
- [x] Constantes definidas

**Database Connection** (2 tests)
- [x] Conexión exitosa
- [x] Conexión a BD inexistente

**Fetch Kudos Data** (4 tests)
- [x] Fetch retorna resultados
- [x] Estructura de datos correcta
- [x] BD vacía retorna lista vacía
- [x] Ordenamiento correcto

**Export to CSV** (5 tests)
- [x] Crea archivo CSV
- [x] Contenido de CSV correcto
- [x] Crea directorios padre
- [x] Datos vacíos no crea archivo
- [x] Manejo de caracteres especiales

**Generate Kudos Report** (3 tests)
- [x] Generación exitosa
- [x] Contenido correcto
- [x] BD inválida no falla

**Run Report** (4 tests)
- [x] Ejecución exitosa
- [x] Crea archivo de salida
- [x] Parámetros por defecto
- [x] Estructura de retorno

**Query & CSV** (3 tests)
- [x] Query SQL bien formada
- [x] Query selecciona campos correctos
- [x] CSV fieldnames definidos
- [x] CSV fieldnames contenido correcto

**Integration** (1 test)
- [x] Workflow completo de generación

### Resultados Fase 1

✅ **83 tests implementados**
✅ **100% passing**
✅ **Cobertura**: config.py (100%), sqlite.py (91%), reports.py (90%)
✅ **Tiempo**: ~2.6 segundos

---

## Fase 2: Tests de Módulos Core 🚧 EN PROGRESO

### Objetivos
Cubrir los módulos de lógica de negocio core del proyecto (autenticación y sincronización).

### 2.1 Tests de Autenticación OAuth2 ⏳ PENDIENTE
**Archivo**: `tests/unit/test_api_auth.py` (estimado: 25-30 tests)

**Token Management**
- [ ] getTokenFromFile lee token correctamente
- [ ] getTokenFromFile maneja archivo inexistente
- [ ] writeTokenToFile escribe JSON correctamente
- [ ] writeTokenToFile crea directorio si no existe
- [ ] Token expiration check funciona
- [ ] Token no expirado no refresca

**OAuth2 Flow**
- [ ] generateAuthorizationUrl genera URL correcta
- [ ] generateAuthorizationUrl incluye scopes
- [ ] extractAuthorizationCode parsea URL correctamente
- [ ] extractAuthorizationCode maneja URLs inválidas
- [ ] authenticate intercambia code por token
- [ ] authenticate maneja errores de API

**Token Refresh**
- [ ] refreshToken actualiza token expirado
- [ ] refreshToken no refresca token válido
- [ ] refreshToken maneja errores de API
- [ ] refreshToken actualiza archivo JSON

**Strava Token Manager**
- [ ] StravaTokenManager inicializa correctamente
- [ ] get_valid_token retorna token válido
- [ ] get_valid_token refresca token expirado
- [ ] authenticate flujo completo
- [ ] refresh_token actualiza tokens
- [ ] Manejo de errores de red
- [ ] Manejo de credenciales inválidas

**Mocks Necesarios**:
```python
@pytest.fixture
def mock_strava_api():
    """Mock de respuestas de Strava API"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            'token_type': 'Bearer',
            'expires_at': 1733500000,
            'access_token': 'new_token',
            'refresh_token': 'new_refresh'
        }
        yield mock_post

@pytest.fixture
def expired_token_data():
    """Token expirado para tests"""
    return {
        'expires_at': 1000000000,  # Pasado
        'access_token': 'old_token',
        'refresh_token': 'refresh_token'
    }
```

**Prioridad**: 🔴 ALTA (módulo crítico para funcionamiento)
**Estimación**: 4-6 horas
**Dependencias**: requests-mock o responses library

### 2.2 Tests de Sincronización ⏳ PENDIENTE
**Archivo**: `tests/unit/test_core_sync.py` (estimado: 30-35 tests)

**Token Access**
- [ ] get_access_token obtiene token válido
- [ ] get_access_token maneja token expirado
- [ ] get_access_token maneja archivo inexistente
- [ ] get_access_token maneja errores de refresh

**Timestamp Management**
- [ ] get_last_sync_timestamp lee log correctamente
- [ ] get_last_sync_timestamp maneja archivo vacío
- [ ] get_last_sync_timestamp maneja archivo inexistente
- [ ] get_last_sync_timestamp retorna 0 por defecto

**Activity Fetching**
- [ ] fetch_new_activities obtiene actividades
- [ ] fetch_new_activities usa timestamp correcto
- [ ] fetch_new_activities maneja paginación
- [ ] fetch_new_activities maneja respuesta vacía
- [ ] fetch_new_activities maneja errores de API

**Activity Processing**
- [ ] process_activity extrae campos correctos
- [ ] process_activity maneja campos faltantes
- [ ] process_activity convierte tipos correctamente
- [ ] process_activity maneja end_latlng None

**Kudos Fetching**
- [ ] fetch_activity_kudos obtiene kudos
- [ ] fetch_activity_kudos maneja actividad sin kudos
- [ ] fetch_activity_kudos maneja errores de API

**Kudos Processing**
- [ ] process_kudos extrae campos correctos
- [ ] process_kudos maneja lista vacía

**Database Sync**
- [ ] sync_activity_to_db inserta actividad
- [ ] sync_activity_to_db actualiza actividad existente
- [ ] sync_kudos_to_db inserta kudos
- [ ] sync_kudos_to_db maneja kudos duplicados

**Logging**
- [ ] log_synced_activity escribe correctamente
- [ ] log_synced_activity crea archivo si no existe
- [ ] log_synced_activity maneja errores de escritura

**Main Sync Function**
- [ ] run_sync ejecuta flujo completo
- [ ] run_sync usa parámetros por defecto
- [ ] run_sync maneja errores gracefully
- [ ] run_sync retorna estadísticas correctas
- [ ] run_sync con BD PostgreSQL
- [ ] run_sync con BD SQLite

**Mocks Necesarios**:
```python
@pytest.fixture
def mock_strava_activities_api():
    """Mock de API de actividades"""
    return [
        {'id': 1, 'name': 'Run', 'distance': 5000},
        {'id': 2, 'name': 'Ride', 'distance': 20000}
    ]

@pytest.fixture
def mock_strava_kudos_api():
    """Mock de API de kudos"""
    return [
        {'firstname': 'John', 'lastname': 'Doe'},
        {'firstname': 'Jane', 'lastname': 'Smith'}
    ]
```

**Prioridad**: 🔴 ALTA (módulo crítico)
**Estimación**: 6-8 horas
**Dependencias**: requests-mock, freezegun (para tests de fechas)

### 2.3 Tests de CLI Commands ⏳ PENDIENTE
**Archivos**:
- `tests/unit/test_cli_init_db.py` (estimado: 8-10 tests)
- `tests/unit/test_cli_sync.py` (estimado: 10-12 tests)
- `tests/unit/test_cli_report.py` (estimado: 8-10 tests)

**init-db command**
- [ ] init-db crea tablas Activities y Kudos
- [ ] init-db con --reset elimina y recrea
- [ ] init-db maneja BD existente
- [ ] init-db maneja errores de BD
- [ ] init-db output formateado correctamente

**sync command**
- [ ] sync ejecuta sincronización completa
- [ ] sync con --from-date usa fecha especificada
- [ ] sync con --limit limita actividades
- [ ] sync maneja token inválido
- [ ] sync maneja errores de API
- [ ] sync muestra progreso
- [ ] sync output formateado correctamente

**report command**
- [ ] report genera CSV correctamente
- [ ] report con --output usa ruta personalizada
- [ ] report con --format soporta JSON
- [ ] report maneja BD vacía
- [ ] report output formateado correctamente

**Mocks Necesarios**:
```python
from click.testing import CliRunner

@pytest.fixture
def cli_runner():
    """Click CLI test runner"""
    return CliRunner()

def test_init_db_creates_tables(cli_runner, tmp_path):
    result = cli_runner.invoke(init_db, ['--db-path', str(tmp_path / 'test.db')])
    assert result.exit_code == 0
    assert 'Tabla Activities creada' in result.output
```

**Prioridad**: 🟡 MEDIA
**Estimación**: 4-5 horas
**Dependencias**: None (usa Click testing)

### 2.4 Tests de Utilidades (utils) ⏳ PENDIENTE
**Archivo**: `tests/unit/test_utils_dates.py` (estimado: 10-12 tests)

**Date Utils**
- [ ] last_timestamp lee última línea correctamente
- [ ] last_timestamp maneja archivo vacío
- [ ] timestamp_to_unix convierte correctamente
- [ ] unix_to_timestamp convierte correctamente
- [ ] parse_strava_date parsea ISO 8601
- [ ] format_date formatea correctamente
- [ ] Manejo de zonas horarias

**Prioridad**: 🟢 BAJA
**Estimación**: 2-3 horas

---

## Fase 3: Tests de Integración

### Objetivos
Verificar que los módulos funcionan correctamente en conjunto.

### 3.1 Integration Tests Setup ⏳ PENDIENTE
**Directorio**: `tests/integration/`

**Configuración**:
- [ ] Crear `tests/integration/__init__.py`
- [ ] Configurar fixtures de integración en conftest
- [ ] BD de test persistente para toda la suite
- [ ] Datos de test realistas

### 3.2 Database Integration Tests ⏳ PENDIENTE
**Archivo**: `tests/integration/test_database_integration.py`

- [ ] CRUD completo de Activities
- [ ] CRUD completo de Kudos
- [ ] Joins entre Activities y Kudos
- [ ] Transactions y rollbacks
- [ ] Migraciones de schema
- [ ] Performance con datos grandes (1000+ activities)

**Prioridad**: 🟡 MEDIA
**Estimación**: 4-5 horas

### 3.3 API Integration Tests ⏳ PENDIENTE
**Archivo**: `tests/integration/test_api_integration.py`

- [ ] OAuth2 flow completo (con mocks)
- [ ] Fetch activities desde API (mock)
- [ ] Fetch kudos desde API (mock)
- [ ] Rate limiting handling
- [ ] Error handling y retries
- [ ] Paginación de resultados

**Prioridad**: 🟡 MEDIA
**Estimación**: 5-6 horas

### 3.4 Sync Integration Tests ⏳ PENDIENTE
**Archivo**: `tests/integration/test_sync_integration.py`

- [ ] Sincronización completa end-to-end
- [ ] Sincronización incremental (solo nuevas)
- [ ] Sincronización con errores parciales
- [ ] Logging de actividades sincronizadas
- [ ] Actualización de actividades existentes
- [ ] Limpieza de kudos obsoletos

**Prioridad**: 🔴 ALTA
**Estimación**: 6-8 horas

### 3.5 Reports Integration Tests ⏳ PENDIENTE
**Archivo**: `tests/integration/test_reports_integration.py`

- [ ] Generación de reporte con datos reales
- [ ] Múltiples formatos (CSV, JSON)
- [ ] Filtros y agregaciones
- [ ] Performance con 1000+ kudos
- [ ] Encoding y caracteres especiales

**Prioridad**: 🟢 BAJA
**Estimación**: 3-4 horas

---

## Fase 4: Tests End-to-End

### Objetivos
Simular uso real de la aplicación completa.

### 4.1 CLI E2E Tests ⏳ PENDIENTE
**Archivo**: `tests/e2e/test_cli_workflows.py`

**Workflows Completos**:
- [ ] Setup inicial: init-db → sync → report
- [ ] Actualización: sync nuevas actividades → report
- [ ] Reset y re-sync completo
- [ ] Manejo de errores en workflow

**Prioridad**: 🟡 MEDIA
**Estimación**: 4-5 horas

### 4.2 Error Recovery E2E ⏳ PENDIENTE
**Archivo**: `tests/e2e/test_error_recovery.py`

- [ ] Recovery de token expirado
- [ ] Recovery de BD corrupta
- [ ] Recovery de API rate limit
- [ ] Recovery de red intermitente
- [ ] Partial sync resume

**Prioridad**: 🟡 MEDIA
**Estimación**: 5-6 horas

---

## Fase 5: CI/CD y Automatización

### Objetivos
Automatizar ejecución de tests en pipelines CI/CD.

### 5.1 GitHub Actions Setup ⏳ PENDIENTE
**Archivo**: `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run tests
      run: |
        pytest tests/ -v --cov=py_strava --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

**Tareas**:
- [ ] Configurar GitHub Actions workflow
- [ ] Matrix testing (Python 3.8-3.11)
- [ ] Coverage reporting con Codecov
- [ ] Badge de coverage en README
- [ ] Pre-commit hooks con tests

**Prioridad**: 🟡 MEDIA
**Estimación**: 2-3 horas

### 5.2 GitLab CI Setup ⏳ PENDIENTE
**Archivo**: `.gitlab-ci.yml`

- [ ] Pipeline de tests en GitLab CI
- [ ] Stages: lint, test, coverage
- [ ] Artifacts de coverage
- [ ] Merge request integration

**Prioridad**: 🟢 BAJA
**Estimación**: 2-3 horas

### 5.3 Pre-commit Hooks ⏳ PENDIENTE
**Archivo**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit/ -v --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

- [ ] Configurar pre-commit
- [ ] Hook para ejecutar tests rápidos
- [ ] Hook para linting (black, flake8)
- [ ] Hook para type checking (mypy)

**Prioridad**: 🟡 MEDIA
**Estimación**: 2 horas

### 5.4 Performance Testing ⏳ PENDIENTE
**Archivo**: `tests/performance/test_performance.py`

- [ ] Benchmark de sincronización (1000 activities)
- [ ] Benchmark de generación de reportes
- [ ] Benchmark de queries complejas
- [ ] Memory profiling
- [ ] Load testing de BD

**Prioridad**: 🟢 BAJA
**Estimación**: 4-5 horas

---

## 📈 Métricas y Objetivos

### Objetivos de Cobertura por Fase

| Fase | Cobertura Objetivo | Módulos Críticos |
|------|-------------------|------------------|
| Fase 1 ✅ | 20-25% | config, database, reports |
| Fase 2 | 50-60% | + api, core/sync, cli |
| Fase 3 | 70-75% | + integration |
| Fase 4 | 80-85% | + e2e workflows |
| Fase 5 | 85-90% | + automation |

### Objetivos de Testing

- ✅ **Unit Tests**: 100+ tests
- 🎯 **Integration Tests**: 40+ tests (objetivo)
- 🎯 **E2E Tests**: 15+ tests (objetivo)
- 🎯 **Performance Tests**: 10+ tests (objetivo)

### Objetivos de Tiempo

| Tipo | Tiempo Objetivo |
|------|----------------|
| Unit tests | < 5 segundos ✅ |
| Integration tests | < 30 segundos |
| E2E tests | < 2 minutos |
| Full suite | < 3 minutos |

---

## 🚀 Próximos Pasos Inmediatos

### Sprint 1 (1-2 semanas)

**Prioridad ALTA**:
1. ✅ Tests de autenticación OAuth2 (`test_api_auth.py`)
2. ✅ Tests de sincronización (`test_core_sync.py`)
3. ✅ Tests de CLI commands básicos

**Entregables**:
- 60-70 tests adicionales
- Cobertura 50-60%
- Documentación de tests

### Sprint 2 (2-3 semanas)

**Prioridad MEDIA**:
1. ✅ Integration tests de database
2. ✅ Integration tests de sync
3. ✅ GitHub Actions setup

**Entregables**:
- 40+ integration tests
- CI/CD funcionando
- Cobertura 70-75%

### Sprint 3 (1-2 semanas)

**Prioridad BAJA**:
1. ✅ E2E workflows
2. ✅ Performance tests básicos
3. ✅ Documentación completa

**Entregables**:
- 15+ E2E tests
- Performance benchmarks
- Cobertura 85%+

---

## 📚 Recursos y Referencias

### Librerías Recomendadas

```txt
# Testing core
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0

# Testing utils
freezegun>=1.4.0        # Time mocking
responses>=0.24.0       # HTTP mocking
requests-mock>=1.11.0   # Alternative HTTP mocking
faker>=22.0.0           # Test data generation

# Performance
pytest-benchmark>=4.0.0
memory-profiler>=0.61.0

# Coverage
coverage[toml]>=7.4.0
```

### Documentación

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Click testing](https://click.palletsprojects.com/en/8.1.x/testing/)
- [responses library](https://github.com/getsentry/responses)

### Buenas Prácticas

1. **AAA Pattern**: Arrange, Act, Assert
2. **One assertion per test** (cuando sea posible)
3. **Nombres descriptivos**: `test_sync_handles_expired_token`
4. **Fixtures reutilizables**: Evitar duplicación
5. **Mocking externo**: No hacer requests reales a APIs
6. **Tests independientes**: No depender de orden de ejecución
7. **Tests rápidos**: Unit tests < 100ms cada uno

---

## 📝 Notas de Implementación

### Convenciones de Nombres

```python
# Test files
test_<module_name>.py

# Test classes
class Test<Functionality>:
    def test_<behavior>_<expected_result>(self):
        pass

# Fixtures
@pytest.fixture
def mock_<what_it_mocks>():
    pass
```

### Estructura de Tests

```python
def test_function_does_something():
    """Test that function does X when Y."""
    # Arrange
    input_data = {...}
    expected = {...}

    # Act
    result = function(input_data)

    # Assert
    assert result == expected
```

### Markers Personalizados

```python
@pytest.mark.slow
def test_heavy_operation():
    pass

@pytest.mark.integration
def test_database_sync():
    pass

@pytest.mark.db
def test_query_performance():
    pass
```

**Ejecutar con markers**:
```bash
# Solo unit tests rápidos
pytest -m "unit and not slow"

# Solo integration tests
pytest -m integration

# Excluir tests que requieren DB
pytest -m "not db"
```

---

## 🎯 Conclusión

Este roadmap proporciona una guía clara y estructurada para completar la cobertura de testing del proyecto py-strava. La Fase 1 está completada exitosamente con 83 tests y cobertura del 22%.

Los próximos pasos críticos son implementar tests para los módulos `api/auth.py` y `core/sync.py` en la Fase 2, lo cual elevará la cobertura al 50-60% y proporcionará confianza en los componentes críticos del sistema.

**Actualizado**: Diciembre 2025
**Próxima revisión**: Después de completar Fase 2
