# Arquitectura del Proyecto

**Versión**: 2.2.0
**Última actualización**: 3 de diciembre de 2025

---

## Resumen

Este documento describe la arquitectura actual del proyecto después de la reestructuración completa (Fases 1-3).

## Estructura del Proyecto

```
py-strava/
├── py_strava/              # Código fuente principal
│   ├── api/                # Comunicación con Strava API
│   │   ├── auth.py         # Autenticación OAuth2
│   │   └── activities.py   # Gestión de actividades y kudos
│   │
│   ├── database/           # Persistencia de datos
│   │   ├── sqlite.py       # Driver SQLite
│   │   ├── postgres.py     # Driver PostgreSQL
│   │   └── schema.py       # Esquemas SQL
│   │
│   ├── utils/              # Utilidades generales
│   │   └── dates.py        # Manejo de fechas
│   │
│   ├── core/               # Lógica de negocio
│   │   ├── sync.py         # Sincronización de actividades
│   │   └── reports.py      # Generación de reportes
│   │
│   ├── cli/                # Interfaz de línea de comandos
│   │   ├── main.py         # Entry point CLI
│   │   └── commands/       # Subcomandos
│   │       ├── sync.py
│   │       ├── report.py
│   │       └── init_db.py
│   │
│   ├── legacy/             # Wrappers deprecados
│   ├── strava/             # Módulos antiguos (deprecados)
│   ├── main.py             # Wrapper legacy
│   ├── informe_strava.py   # Wrapper legacy
│   └── config.py           # Configuración global
│
├── scripts/                # Scripts de utilidad
│   ├── init_database.py
│   ├── ejemplo_uso_bd.py
│   └── test_setup.py
│
├── docs/                   # Documentación
│   ├── user/               # Guías de usuario
│   ├── dev/                # Documentación técnica
│   └── database/           # Docs de BD
│
├── tests/                  # Suite de tests
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── requirements/           # Dependencias por entorno
│   ├── base.txt
│   ├── dev.txt
│   └── postgres.txt
│
├── setup.py                # Instalación pip
├── pyproject.toml          # Configuración moderna
└── README.md               # Documentación principal
```

## Módulos Principales

### 1. API (`py_strava/api/`)

**Responsabilidad**: Comunicación con la API REST de Strava

#### `api/auth.py`
- Clase `StravaTokenManager`: Gestión orientada a objetos de tokens
- Renovación automática de tokens expirados
- Funciones legacy para retrocompatibilidad
- Configuración mediante variables de entorno

#### `api/activities.py`
- Descarga de actividades desde Strava API
- Obtención de kudos por actividad
- Paginación automática
- Manejo de rate limits

### 2. Database (`py_strava/database/`)

**Responsabilidad**: Persistencia y gestión de datos

#### `database/sqlite.py`
- Context manager `DatabaseConnection`
- Operaciones CRUD básicas
- Batch inserts (20-40x más rápido)
- Manejo automático de transacciones

#### `database/postgres.py`
- Similar a SQLite pero para PostgreSQL
- Soporte para conexiones remotas
- Pool de conexiones
- Transacciones ACID

#### `database/schema.py`
- Definiciones SQL de tablas
- Constraints y foreign keys
- Funciones de creación de esquema

### 3. Core (`py_strava/core/`)

**Responsabilidad**: Lógica de negocio principal

#### `core/sync.py`
- Función `run_sync()`: API programática para sincronización
- Gestión de última sincronización
- Batch processing de actividades y kudos
- Logging detallado

#### `core/reports.py`
- Función `run_report()`: API programática para reportes
- Generación de CSV
- Queries optimizadas
- Estadísticas de export

### 4. CLI (`py_strava/cli/`)

**Responsabilidad**: Interfaz de línea de comandos

#### `cli/main.py`
- Comando principal `strava`
- Opciones globales: `--verbose`, `--quiet`, `--log-level`
- Registro de subcomandos
- Manejo de excepciones global

#### `cli/commands/`
- `sync.py`: Comando `strava sync`
- `report.py`: Comando `strava report`
- `init_db.py`: Comando `strava init-db`

## Flujo de Datos

### Sincronización de Actividades

```
1. Usuario ejecuta: strava sync
         ↓
2. CLI parsea argumentos
         ↓
3. core.sync.run_sync()
         ↓
4. api.auth → Obtiene token válido
         ↓
5. api.activities → Descarga actividades
         ↓
6. database.sqlite → Batch insert actividades
         ↓
7. api.activities → Descarga kudos por actividad
         ↓
8. database.sqlite → Batch insert kudos
         ↓
9. Actualiza log de sincronización
         ↓
10. Retorna estadísticas
```

### Generación de Reportes

```
1. Usuario ejecuta: strava report
         ↓
2. CLI parsea argumentos
         ↓
3. core.reports.run_report()
         ↓
4. database.sqlite → Query JOIN Activities-Kudos
         ↓
5. Genera CSV con resultados
         ↓
6. Retorna estadísticas
```

## Patrones de Diseño

### 1. Context Managers (Database)
```python
with DatabaseConnection(db_path) as conn:
    # Operaciones de BD
    # Auto-commit y auto-close
```

### 2. Dependency Injection (Core)
```python
def run_sync(
    token_file='./json/tokens.json',  # Inyectable
    db_path='./bd/strava.sqlite'       # Inyectable
):
    # Lógica con dependencias configurables
```

### 3. Command Pattern (CLI)
```python
@click.command()
def sync(...):
    # Cada comando es independiente
    # Encapsula una operación
```

### 4. Adapter Pattern (Legacy)
```python
# main.py (wrapper)
def main():
    # Adapta interfaz antigua a nueva
    run_sync(...)
```

## Decisiones Arquitectónicas

### 1. Separación por Capas
- **API**: Comunicación externa
- **Database**: Persistencia
- **Core**: Lógica de negocio
- **CLI**: Interfaz de usuario

**Ventajas**:
- Fácil testing (cada capa se puede mockear)
- Bajo acoplamiento
- Alta cohesión

### 2. Wrappers de Retrocompatibilidad
Mantener `main.py` y `informe_strava.py` como wrappers permite:
- Migración gradual
- No romper scripts existentes
- Deprecación controlada

### 3. CLI como Capa Separada
El CLI no mezcla lógica de negocio:
- `cli/` solo maneja UI/UX
- `core/` contiene toda la lógica
- Permite usar el proyecto como biblioteca

### 4. Batch Inserts
Insertar muchos registros de una vez:
- 20-40x más rápido que inserts individuales
- Reduce transacciones
- Mejor para sincronizaciones grandes

## Dependencias

### Core
- pandas: Análisis de datos
- numpy: Operaciones numéricas
- requests: HTTP client
- python-dateutil: Manejo de fechas
- click: Framework CLI

### Opcionales
- psycopg2-binary: Driver PostgreSQL
- pytest: Testing
- black, flake8: Linting
- mypy: Type checking

## Historial de Mejoras

Para ver el historial detallado de mejoras y cambios:

### Documentación Histórica (docs/dev/)
- `MEJORAS_IMPLEMENTADAS.md`: Mejoras iniciales
- `MEJORAS_MODULOS_DATABASE.md`: Evolución del módulo database
- `MEJORAS_STRAVA_DB_SQLITE.md`: Mejoras en SQLite
- `MEJORAS_STRAVA_TOKEN_Y_MAIN.md`: Mejoras en auth y main
- `ANALISIS_MEJORAS_POSTGRES.md`: Análisis de PostgreSQL
- `RESUMEN_CAMBIOS.md`: Resumen de cambios históricos

### Changelogs de Reestructuración
- `CHANGELOG_FASE_1.md`: Reorganización del proyecto
- `CHANGELOG_FASE_2.md`: Refactoring de módulos
- `CHANGELOG_FASE_3.md`: CLI profesional
- `CHANGELOG_FASE_4.md`: Limpieza y release
- `CHANGELOG.md`: Changelog oficial versionado

## Próximas Mejoras

Ver `ROADMAP_MIGRACION.md` para:
- Fase 4: Limpieza final
- Futuras features
- Roadmap de releases

## Referencias

- [README.md](../../README.md): Guía de inicio rápido
- [ROADMAP_MIGRACION.md](../../ROADMAP_MIGRACION.md): Plan de reestructuración
- [docs/user/](../user/): Documentación para usuarios
- [docs/database/](../database/): Documentación de BD

---

**Última actualización**: 3 de diciembre de 2025
**Versión de la arquitectura**: 2.2.0
