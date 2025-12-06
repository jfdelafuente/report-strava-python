# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [3.0.0] - 2025-12-06

### 💥 Breaking Changes

#### Eliminado módulo deprecado `py_strava.strava`

- **Eliminado completamente** el módulo `py_strava.strava` y todos sus submódulos
- El módulo fue marcado como deprecado en v2.0.0 y toda funcionalidad fue migrada
- **Acción requerida**: Actualizar imports a nueva estructura modular
- Ver [GUIA_MIGRACION_V3.md](docs/dev/GUIA_MIGRACION_V3.md) para instrucciones detalladas

**Migración de imports**:

```python
# Antes (v2.x) ❌
from py_strava.strava import strava_token
from py_strava.strava import strava_activities
from py_strava.strava import strava_db_sqlite

# Después (v3.0.0) ✅
from py_strava.api import auth
from py_strava.api import activities
from py_strava.database import sqlite
```

#### Eliminada sincronización de kudos individuales

- **Eliminada función** `load_kudos_to_db()` del módulo `core/sync.py`
- Ya no se sincronizan kudos individuales en tabla `Kudos`
- **Razón**: Alto costo en llamadas API vs bajo valor agregado
- **Alternativa**: Campo `kudos_count` sigue disponible en cada actividad
- Los datos existentes en tabla `Kudos` no se eliminan automáticamente

**Cambio en return de `run_sync()`**:

```python
# Antes (v2.x)
{"activities": 10, "kudos": 45, "db_type": "SQLite"}

# Después (v3.0.0)
{"activities": 10, "db_type": "SQLite"}
```

### Cambiado

- Actualizado README.md eliminando referencias a kudos y módulo deprecado
- Actualizados tests unitarios para usar nueva estructura de imports
- Actualizado script de verificación `test_setup.py` con nuevos imports
- Simplificado proceso de sincronización (sin llamadas individuales de kudos)

### Documentación

- ✅ Añadida [GUIA_MIGRACION_V3.md](docs/dev/GUIA_MIGRACION_V3.md) - Guía completa de migración
- ✅ Añadida [ANALISIS_ELIMINACION_MODULO_STRAVA.md](docs/dev/ANALISIS_ELIMINACION_MODULO_STRAVA.md) - Análisis técnico
- Actualizada estructura del proyecto en documentación

### Mejoras

- 📉 Reducción de ~2,500 líneas de código duplicado
- 📦 Reducción del tamaño del paquete (~150 KB)
- 🎯 Arquitectura más clara y mantenible
- ⚡ Sincronización más rápida (sin llamadas extras de kudos)
- 🔇 Eliminados warnings de deprecación en logs

---

## [2.2.0] - 2025-12-03

### Añadido

#### CLI Profesional (Fase 3)
- Implementación completa de CLI profesional usando Click framework
- Comando instalable `strava` disponible globalmente en PATH
- Subcomando `strava sync`: Sincronizar actividades desde Strava API
  - Opción `--since` para sincronización desde fecha específica
  - Opción `--force` para sincronización completa
  - Opciones configurables: `--token-file`, `--db-path`, `--activities-log`
- Subcomando `strava report`: Generar reportes de actividades y kudos
  - Opción `-o/--output` para especificar archivo CSV de salida
  - Opción `--db-path` para base de datos personalizada
  - Opción `--format` para formato de reporte (CSV por defecto)
- Subcomando `strava init-db`: Inicializar/verificar base de datos
  - Opción `--verify` para verificar sin modificar
  - Opción `--reset` para recrear tablas (con confirmación)
  - Opción `--db-path` para base de datos personalizada
- Opciones globales en todos los comandos:
  - `--verbose/-v`: Modo debug con logging detallado
  - `--quiet/-q`: Modo silencioso (solo errores)
  - `--log-level`: Control granular de nivel de logging
  - `--version`: Mostrar versión del programa
- Help integrado en todos los comandos con `--help`
- Mensajes coloreados y user-friendly en terminal
- Gestión centralizada de logging

#### Nueva Arquitectura de Módulos (Fase 2)
- Módulo `py_strava/api/`: Comunicación con Strava API
  - `api/auth.py`: Autenticación OAuth2 y gestión de tokens
  - `api/activities.py`: Descarga de actividades y kudos
- Módulo `py_strava/database/`: Persistencia de datos
  - `database/sqlite.py`: Driver SQLite con context manager
  - `database/postgres.py`: Driver PostgreSQL (opcional)
  - `database/schema.py`: Definiciones SQL de esquema
- Módulo `py_strava/utils/`: Utilidades generales
  - `utils/dates.py`: Manejo de fechas y conversiones
- Módulo `py_strava/core/`: Lógica de negocio
  - `core/sync.py`: Función `run_sync()` - API programática para sincronización
  - `core/reports.py`: Función `run_report()` - API programática para reportes
- Módulo `py_strava/cli/`: Interfaz de línea de comandos
  - `cli/main.py`: Entry point del CLI
  - `cli/commands/sync.py`: Comando sync
  - `cli/commands/report.py`: Comando report
  - `cli/commands/init_db.py`: Comando init-db
- Módulo `py_strava/legacy/`: Wrappers deprecados para retrocompatibilidad

#### Instalación y Empaquetado
- Archivo `setup.py` para instalación con pip
- Archivo `pyproject.toml` para configuración moderna (PEP 517/518)
- Entry point `strava` en console_scripts
- Soporte para instalación editable: `pip install -e .`
- Dependencias opcionales: `[dev]`, `[postgres]`

#### Documentación
- `docs/dev/ARQUITECTURA.md`: Arquitectura completa del proyecto v2.2.0
- `docs/user/`: Guías de usuario actualizadas
- `requirements/README.md`: Documentación de dependencias
- `CHANGELOG_FASE_1.md`: Changelog de reorganización del proyecto
- `CHANGELOG_FASE_2.md`: Changelog de refactoring de módulos
- `CHANGELOG_FASE_3.md`: Changelog de implementación del CLI

#### Dependencias
- Nueva dependencia: `click>=8.1.0` (framework CLI)
- Organizadas en `requirements/base.txt`, `requirements/dev.txt`, `requirements/postgres.txt`

### Cambiado

#### Reorganización del Proyecto (Fase 1)
- Reestructuración completa de directorios:
  - Scripts movidos de raíz a `scripts/`
  - Documentación consolidada en `docs/`
  - JSON de configuración movidos a `json/`
  - Bases de datos movidas a `bd/`
- Estructura modular mejorada con separación de responsabilidades
- Todos los imports actualizados a nuevas rutas

#### Refactoring de Módulos (Fase 2)
- Separación de capas: API, Database, Core, CLI
- Context managers para gestión de conexiones de BD
- Dependency injection en funciones del core
- Batch inserts en SQLite (20-40x más rápido)
- Manejo mejorado de errores y logging

#### Mejoras en Scripts
- `scripts/init_database.py`: Actualizado para usar `py_strava.database.sqlite`
- `scripts/ejemplo_uso_bd.py`: Actualizado para usar nuevos módulos
- `scripts/test_setup.py`: Actualizado para validar nueva estructura

#### Configuración
- `requirements.txt` actualizado con click>=8.1.0
- Variables de entorno documentadas en `config.py`
- Rutas por defecto configurables vía argumentos CLI

### Corregido

- Bug en `cli/commands/init_db.py`: Acceso incorrecto a cursor de BD
  - Cambiado de `db.cursor.fetchone()` a `cursor = conn.cursor(); cursor.fetchone()`
- Inconsistencia en dependencias entre `requirements.txt` y `requirements/base.txt`
- Archivos temporales eliminados: `=8.1.0`, `py_strava__init__.py`, `py_stravastrava__init__.py`

### Deprecado

- `py_strava/main.py` como módulo de lógica de negocio
  - Ahora es wrapper que delega a `core.sync.run_sync()`
  - Emite `DeprecationWarning` al importar
  - Se recomienda usar `py_strava.core.sync` directamente
- `py_strava/informe_strava.py` como módulo de reportes
  - Ahora es wrapper que delega a `core.reports.run_report()`
  - Emite `DeprecationWarning` al importar
  - Se recomienda usar `py_strava.core.reports` directamente
- Imports desde `py_strava/strava/`:
  - `py_strava.strava.strava_token` → usar `py_strava.api.auth`
  - `py_strava.strava.strava_activities` → usar `py_strava.api.activities`
  - `py_strava.strava.strava_db_sqlite` → usar `py_strava.database.sqlite`
  - `py_strava.strava.strava_fechas` → usar `py_strava.utils.dates`

### Mantenido (Retrocompatibilidad)

- ✅ Todos los comandos antiguos siguen funcionando:
  - `python -m py_strava.main` (con DeprecationWarning)
  - `python -m py_strava.informe_strava` (con DeprecationWarning)
  - `python scripts/init_database.py`
- ✅ Imports antiguos funcionan con warnings de deprecación
- ✅ Rutas de archivos por defecto sin cambios
- ✅ Formato de base de datos SQLite sin cambios
- ✅ Estructura de `tokens.json` sin cambios
- ✅ API programática (`run_sync()`, `run_report()`) compatible

## [2.1.0] - 2025-11-XX

### Añadido
- Mejoras en gestión de tokens OAuth2
- Soporte para PostgreSQL como alternativa a SQLite
- Batch inserts para mejor rendimiento
- Context managers para conexiones de BD
- Logging mejorado

### Cambiado
- Optimizaciones en `strava_db_sqlite.py`
- Refactoring de `strava_token.py` con clase `StravaTokenManager`

## [2.0.0] - 2025-10-XX

### Añadido
- Sistema de sincronización de actividades
- Descarga automática de kudos
- Base de datos SQLite para persistencia
- Scripts de inicialización de BD

### Cambiado
- Primera versión estable con arquitectura base

---

## Guía de Migración

### De comandos antiguos a nuevos (v2.2.0)

```bash
# ANTES (v2.1.0)
python -m py_strava.main
python -m py_strava.informe_strava
python scripts/init_database.py

# DESPUÉS (v2.2.0) - Recomendado
strava sync
strava report
strava init-db

# Los comandos antiguos siguen funcionando pero emiten warnings
```

### De imports antiguos a nuevos (v2.2.0)

```python
# ANTES (v2.1.0)
from py_strava.strava import strava_token
from py_strava.strava import strava_activities
from py_strava.strava import strava_db_sqlite

# DESPUÉS (v2.2.0) - Recomendado
from py_strava.api import auth
from py_strava.api import activities
from py_strava.database import sqlite

# Los imports antiguos siguen funcionando pero emiten DeprecationWarning
```

### Instalación

```bash
# v2.2.0 y superior
pip install -e .
strava --help

# v2.1.0 y anterior
python -m py_strava.main --help  # (no existía --help)
```

---

## Notas de Versiones

### v2.2.0 (Actual)
- **Estado**: Estable ✅
- **Fases completadas**: 1 (Reorganización), 2 (Refactoring), 3 (CLI)
- **Fase en progreso**: 4 (Cleanup y Release)
- **Retrocompatibilidad**: 100%
- **CLI**: Completo y funcional
- **Tests**: Validados manualmente
- **Recomendación**: Usar comandos `strava` en lugar de `python -m py_strava`

### v2.1.0
- **Estado**: Obsoleto (funcional pero sin CLI moderno)
- **Recomendación**: Actualizar a v2.2.0

### v2.0.0
- **Estado**: Obsoleto
- **Recomendación**: Actualizar a v2.2.0

---

## Enlaces

- [Arquitectura del Proyecto](docs/dev/ARQUITECTURA.md)
- [Roadmap de Migración](ROADMAP_MIGRACION.md)
- [Changelog Fase 1](CHANGELOG_FASE_1.md)
- [Changelog Fase 2](CHANGELOG_FASE_2.md)
- [Changelog Fase 3](CHANGELOG_FASE_3.md)
- [Documentación de Usuario](docs/user/)
- [Documentación de Base de Datos](docs/database/)

---

**Formato**: [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/)
**Versionado**: [Semantic Versioning](https://semver.org/lang/es/)
**Última actualización**: 3 de diciembre de 2025
