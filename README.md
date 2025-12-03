# py-strava

Aplicación Python profesional para sincronizar y analizar actividades de Strava con base de datos local.

## Descripción

**py-strava** es una herramienta CLI profesional que permite:

- Sincronizar automáticamente tus actividades de Strava con una base de datos local
- Almacenar información detallada de actividades y kudos recibidos
- Generar informes y exportar datos a formato CSV
- Mantener un historial completo de tus entrenamientos

El proyecto ha sido completamente refactorizado siguiendo las mejores prácticas de desarrollo en Python, incluyendo CLI profesional con Click, logging estructurado, arquitectura modular, manejo robusto de errores y documentación completa.

## Características

✅ **CLI Profesional**: Comandos intuitivos tipo `strava sync`, `strava report`
✅ **Instalación con pip**: Instala con `pip install -e .` y usa desde cualquier directorio
✅ **Sincronización automática**: Obtiene actividades nuevas desde la última sincronización
✅ **Gestión de tokens**: Refresca automáticamente el token de acceso de Strava
✅ **Base de datos**: Soporta SQLite y PostgreSQL
✅ **Kudos tracking**: Registra todos los kudos recibidos en cada actividad
✅ **Informes CSV**: Exporta datos para análisis externo
✅ **Logging completo**: Sistema de logs estructurado para debugging
✅ **Manejo de errores**: Procesamiento robusto que continúa ante fallos individuales
✅ **Configuración flexible**: Variables de entorno y archivos de configuración
✅ **Help integrado**: Ayuda contextual en todos los comandos con `--help`

## Inicio Rápido

```bash
# 1. Instalar el proyecto
pip install -e .

# 2. Configurar credenciales en json/strava_tokens.json (ver sección Configuración)

# 3. Inicializar base de datos
strava init-db

# 4. Sincronizar actividades
strava sync

# 5. Generar reporte
strava report
```

## Estructura del Proyecto

```plaintext
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
├── requirements/           # Dependencias por entorno
│   ├── base.txt
│   ├── dev.txt
│   └── postgres.txt
│
├── data/                   # Datos generados (logs, CSV)
├── bd/                     # Base de datos SQLite
├── json/                   # Configuración (tokens)
│
├── setup.py                # Instalación pip
├── pyproject.toml          # Configuración moderna
├── CHANGELOG.md            # Historial de cambios
└── README.md               # Este archivo
```

> **Nota**: El proyecto ha sido completamente reestructurado (Fases 1-3). Ver [CHANGELOG.md](CHANGELOG.md) y [docs/dev/ARQUITECTURA.md](docs/dev/ARQUITECTURA.md) para detalles completos.

## Requisitos

- Python 3.8 o superior
- Cuenta de Strava con API habilitada
- PostgreSQL o SQLite

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://gitlab.com/josefcodelafuente/py-strava.git
cd py-strava
```

### 2. Crear entorno virtual

```bash
python3.8 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Actualizar pip

```bash
python3.8 -m pip install --upgrade pip
```

### 4. Instalar el proyecto

**Modo desarrollo (recomendado)**:

```bash
# Instala el proyecto en modo editable con el comando 'strava'
pip install -e .
```

**O con dependencias de desarrollo**:

```bash
# Incluye pytest, mypy, black, flake8, etc.
pip install -e ".[dev]"
```

**O con soporte PostgreSQL**:

```bash
# Incluye psycopg2-binary
pip install -e ".[postgres]"
```

**Todo junto**:

```bash
pip install -e ".[dev,postgres]"
```

Después de la instalación, el comando `strava` estará disponible globalmente en tu PATH.

### 5. Verificar instalación

**Verificar que el comando `strava` está disponible**:

```bash
# Verificar instalación
strava --version
# Debería mostrar: strava, version 2.2.0

# Ver ayuda
strava --help

# Verificar comandos disponibles
strava sync --help
strava report --help
strava init-db --help
```

**Script de verificación completo** (opcional):

```bash
python scripts/test_setup.py           # Verificación completa
python scripts/test_setup.py --quick   # Verificación rápida
python scripts/test_setup.py --verbose # Información detallada
```

## Configuración

### 1. Configurar la API de Strava

1. Ve a [Strava API Settings](https://www.strava.com/settings/api)
2. Crea una nueva aplicación
3. Obtén tu `client_id` y `client_secret`
4. Autoriza la aplicación y obtén el `refresh_token`

### 2. Crear archivo de tokens

Crea el archivo `json/strava_tokens.json`:

```json
{
  "token_type": "Bearer",
  "expires_at": 0,
  "expires_in": 0,
  "refresh_token": "TU_REFRESH_TOKEN",
  "access_token": "",
  "client_id": "TU_CLIENT_ID",
  "client_secret": "TU_CLIENT_SECRET"
}
```

### 3. Configurar base de datos

**El proyecto usa SQLite por defecto** (no requiere configuración adicional). Si prefieres PostgreSQL, sigue las instrucciones abajo.

#### Opción A: SQLite (por defecto - recomendado)

✅ **No requiere configuración** - El archivo SQLite se crea automáticamente en `bd/strava.sqlite`.

#### Opción B: PostgreSQL (opcional)

##### Método 1: Archivo de credenciales (recomendado)

Crea el archivo `bd/postgres_credentials.json`:

```json
{
  "server": "localhost",
  "database": "strava",
  "username": "postgres",
  "password": "tu_password_aqui",
  "port": "5432"
}
```

##### Método 2: Variables de entorno

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=strava
export DB_USER=postgres
export DB_PASSWORD=tu_password
```

##### Método 3: Instalar soporte PostgreSQL

```bash
pip install -e ".[postgres]"
```

### 4. Inicializar la base de datos

**Usar el comando CLI** (recomendado):

```bash
# Crear tablas Activities y Kudos
strava init-db

# Solo verificar (no crear)
strava init-db --verify

# Recrear todas las tablas (¡CUIDADO! Elimina datos)
strava init-db --reset

# Base de datos personalizada
strava init-db --db-path ./mi_bd/strava.db
```

**O usar el script legacy**:

```bash
python scripts/init_database.py              # Crear tablas si no existen
python scripts/init_database.py --verify     # Verificar tablas existentes
python scripts/init_database.py --reset      # Recrear todas las tablas
```

Ver [docs/database/INIT_DATABASE.md](docs/database/INIT_DATABASE.md) para más detalles.

**Para PostgreSQL**: El proyecto detecta automáticamente las credenciales de PostgreSQL si están configuradas.

## Uso

### Flujo de trabajo típico

```bash
# 1. Inicializar BD (solo primera vez)
strava init-db

# 2. Sincronizar actividades
strava sync

# 3. Generar reporte
strava report

# 4. Ver resultados
cat data/strava_data.csv
```

### Comando `strava sync` - Sincronizar actividades

**Uso básico**:

```bash
# Sincronización incremental (desde última sincronización)
strava sync
```

**Opciones avanzadas**:

```bash
# Sincronizar desde fecha específica
strava sync --since 2024-01-01

# Sincronizar desde timestamp Unix
strava sync --since 1704067200

# Sincronización completa (todas las actividades)
strava sync --force

# Base de datos personalizada
strava sync --db-path ./mi_bd/strava.db

# Archivo de tokens personalizado
strava sync --token-file ./config/tokens.json

# Log personalizado
strava sync --activities-log ./logs/activities.log

# Modo verbose (debugging)
strava --verbose sync

# Modo silencioso (solo errores)
strava --quiet sync
```

**Salida esperada**:

```plaintext
[INFO] === Sincronización de Strava ===
[INFO] Token de acceso válido hasta: 2025-12-03 18:30:00
[INFO] Última sincronización: 2025-11-20T08:00:00Z
[INFO] Obteniendo actividades desde Strava...
[SUCCESS] 5 actividades sincronizadas
[SUCCESS] 12 kudos sincronizados
[SUCCESS] Sincronización completada
```

### Comando `strava report` - Generar informes

**Uso básico**:

```bash
# Generar reporte CSV por defecto
strava report
```

**Opciones avanzadas**:

```bash
# Output personalizado
strava report -o mi_reporte.csv

# Con fecha en el nombre
strava report -o "reporte_$(date +%Y%m%d).csv"

# Base de datos personalizada
strava report --db-path ./mi_bd/strava.db

# Especificar formato (solo CSV por ahora)
strava report --format csv
```

**Salida esperada**:

```plaintext
[INFO] === Generación de Reporte ===
[INFO] Base de datos: bd/strava.sqlite
[INFO] 150 registros encontrados
[SUCCESS] Reporte generado: data/strava_data.csv
[INFO] Total exportado: 150 registros
```

**Formato del CSV generado**:

```csv
FIRST_NAME,LAST_NAME,TIPO,ACTIVIDAD,START_DATE
Juan,García,Run,12345678,2025-11-26T08:00:00Z
María,López,Ride,12345679,2025-11-25T17:30:00Z
...
```

### Comando `strava init-db` - Inicializar base de datos

```bash
# Crear tablas (si no existen)
strava init-db

# Solo verificar sin crear
strava init-db --verify

# Recrear todas las tablas (¡CUIDADO!)
strava init-db --reset

# BD personalizada
strava init-db --db-path ./custom.db
```

### Comandos legacy (deprecados pero funcionales)

```bash
# Estos comandos siguen funcionando pero emiten warnings
python -m py_strava.main              # usar: strava sync
python -m py_strava.informe_strava    # usar: strava report
python scripts/init_database.py       # usar: strava init-db
```

## Configuración Avanzada

### Variables de Entorno

Puedes configurar el comportamiento de la aplicación mediante variables de entorno:

```bash
# Nivel de logging (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=INFO

# Base de datos PostgreSQL
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=strava
export DB_USER=postgres
export DB_PASSWORD=tu_password
```

### Archivo .env

Crea un archivo `.env` en la raíz del proyecto:

```env
LOG_LEVEL=INFO
DB_HOST=localhost
DB_PORT=5432
DB_NAME=strava
DB_USER=postgres
DB_PASSWORD=tu_password
```

## Esquema de Base de Datos

### Tabla Activities

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_activity | INTEGER | ID único de la actividad (PK) |
| name | TEXT | Nombre de la actividad |
| start_date_local | TEXT | Fecha y hora de inicio |
| type | TEXT | Tipo (Run, Ride, Swim, etc.) |
| distance | REAL | Distancia en metros |
| moving_time | REAL | Tiempo en movimiento (segundos) |
| elapsed_time | REAL | Tiempo total (segundos) |
| total_elevation_gain | REAL | Desnivel acumulado (metros) |
| end_latlng | TEXT | Coordenadas finales |
| kudos_count | INTEGER | Número de kudos |
| external_id | INTEGER | ID externo |

### Tabla Kudos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_kudos | INTEGER | ID único del kudo (PK) |
| resource_state | TEXT | Estado del recurso |
| firstname | TEXT | Nombre del usuario |
| lastname | TEXT | Apellido del usuario |
| id_activity | INTEGER | ID de la actividad (FK) |

## Mejoras Recientes

### v2.2.0 - CLI Profesional (Diciembre 2025) ✨ ACTUAL

Implementación de CLI profesional con Click framework:

- 🚀 **CLI Profesional**: Comandos `strava sync`, `strava report`, `strava init-db`
- 📦 **Instalación pip**: `pip install -e .` - comando disponible globalmente
- 🏗️ **Arquitectura modular**: `api/`, `database/`, `core/`, `cli/`, `utils/`
- 🎯 **Entry points**: setup.py y pyproject.toml para instalación estándar
- 💡 **Help integrado**: `--help` en todos los comandos
- 🎨 **Mensajes coloreados**: Salida user-friendly en terminal
- 🔧 **Opciones configurables**: Flags para personalizar comportamiento
- 📚 **Documentación completa**: CHANGELOG.md, ARQUITECTURA.md
- ✅ **100% retrocompatible**: Comandos antiguos siguen funcionando

**Migración de comandos**:

| Antes (v2.1.0) | Después (v2.2.0) | Mejora |
|----------------|------------------|--------|
| `python -m py_strava.main` | `strava sync` | -54% caracteres |
| `python -m py_strava.informe_strava` | `strava report` | -65% caracteres |
| `python scripts/init_database.py` | `strava init-db` | -57% caracteres |
| No disponible | `strava --help` | Ayuda integrada |
| No disponible | `strava --version` | Versión integrada |

Ver [CHANGELOG.md](CHANGELOG.md) para detalles completos.

### v2.1.0 - Reorganización del Proyecto (Noviembre 2025)

- 📁 **Estructura organizada**: Documentación en `/docs`, scripts en `/scripts`
- 🧪 **Tests mejorados**: Script de verificación con múltiples modos
- 📚 **Documentación clara**: Separada por audiencia (usuario/desarrollador/BD)
- 🔧 **Scripts de utilidad**: Herramientas para setup e inicialización

### v2.0.0 - Refactorización Inicial (Octubre 2025)

- ✅ Sistema de logging profesional
- ✅ Manejo robusto de errores
- ✅ Código modular y documentado
- ✅ Type hints y validaciones
- ✅ Optimizaciones de rendimiento

## Solución de Problemas

### Verificar la instalación

**Primero, ejecuta el script de verificación:**

```bash
python scripts/test_setup.py
```

Este script comprobará que todos los módulos, dependencias y archivos estén correctamente configurados.

**Opciones**:

```bash
python scripts/test_setup.py --quick    # Verificación rápida
python scripts/test_setup.py --verbose  # Información detallada
```

---

### Error: ModuleNotFoundError

**Causa**: Imports incorrectos o paquetes no instalados.

**Solución**:

1. Asegúrate de ejecutar desde la raíz del proyecto: `cd "c:\My Program Files\workspace-python\report-strava-python"`
2. Instala las dependencias: `pip install -r requirements.txt`
3. Ejecuta con: `python -m py_strava.main` (no `python py_strava/main.py`)

---

### Error: "No se pudo obtener el token de acceso"

**Causa**: Token de refresh inválido o expirado.

**Solución**:

1. Ve a [Strava API Settings](https://www.strava.com/settings/api)
2. Revoca el acceso y vuelve a autorizar
3. Obtén un nuevo `refresh_token`
4. Actualiza `json/strava_tokens.json`

---

### Error: "Error al conectar con la base de datos"

**Causa**: Credenciales incorrectas o servidor no disponible.

**Solución**:

1. Verifica que PostgreSQL esté ejecutándose
2. Crea el archivo `bd/postgres_credentials.json` usando la plantilla `bd/postgres_credentials.json.example`
3. O configura las variables de entorno (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
4. Verifica la conectividad: `psql -h localhost -U postgres -d strava`

---

### Error: "No hay actividades nuevas"

**Causa**: No hay actividades desde la última sincronización.

**Solución**: Esto es normal si ya sincronizaste recientemente. Sal a entrenar y vuelve a sincronizar.

---

### Limpiar base de datos

Si necesitas reiniciar la base de datos:

```bash
python scripts/init_database.py --reset
```

⚠️ **PRECAUCIÓN**: Este comando elimina TODOS los datos existentes. El script pedirá confirmación antes de ejecutar.

---

### Más ayuda

Consulta la documentación completa:

- [docs/user/SOLUCION_ERRORES.md](docs/user/SOLUCION_ERRORES.md) - Guía de solución de problemas
- [docs/user/INICIO_RAPIDO.md](docs/user/INICIO_RAPIDO.md) - Guía de inicio rápido
- [docs/database/INIT_DATABASE.md](docs/database/INIT_DATABASE.md) - Documentación de la base de datos
- [docs/dev/](docs/dev/) - Documentación técnica para desarrolladores

## Desarrollo

### Ejecutar en modo debug

```bash
export LOG_LEVEL=DEBUG
python -m py_strava.main
```

### Estructura del código

Consulta [PROPUESTA_REESTRUCTURACION.md](PROPUESTA_REESTRUCTURACION.md) para detalles de la arquitectura.

**Código principal**:

- `py_strava/main.py`: Script principal de sincronización
- `py_strava/informe_strava.py`: Generador de informes
- `py_strava/config.py`: Configuración centralizada
- `py_strava/db_schema.py`: Esquemas de base de datos

**Scripts de utilidad**:

- `scripts/init_database.py`: Inicialización de BD
- `scripts/test_setup.py`: Verificación de instalación
- `scripts/ejemplo_uso_bd.py`: Ejemplos de uso

**Documentación**:

- `docs/user/`: Guías para usuarios
- `docs/dev/`: Documentación técnica
- `docs/database/`: Documentación de BD

### Próximas mejoras planificadas

Ver [ROADMAP_MIGRACION.md](ROADMAP_MIGRACION.md) para el plan completo.

**Completado** ✅:

- [x] **Fase 1**: Reorganización de estructura y documentación
- [x] **Fase 2**: Refactoring de módulos en `api/`, `database/`, `core/`, `utils/`
- [x] **Fase 3**: CLI profesional con Click: `strava sync`, `strava report`, `strava init-db`

**En progreso** 🔄:

- [ ] **Fase 4**: Limpieza final y release v2.2.0

**Futuro** 🔵:

- [ ] Tests unitarios con pytest
- [ ] CI/CD con GitLab CI
- [ ] Validación de tipos con mypy
- [ ] Linting automático (black, flake8)
- [ ] Publicación en PyPI
- [ ] Dashboard web interactivo

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guía de estilo

- Sigue PEP 8
- Agrega docstrings a todas las funciones
- Usa type hints
- Escribe logs descriptivos
- Maneja errores apropiadamente

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

**Jose F. de la Fuente**

- GitLab: [@josefcodelafuente](https://gitlab.com/josefcodelafuente)

## Agradecimientos

- [Strava API](https://developers.strava.com/) por proporcionar acceso a los datos
- Comunidad de Python por las excelentes bibliotecas
- Claude Code Assistant por las mejoras en el código

## Estado del Proyecto

🚀 **Activo** - El proyecto está en desarrollo activo y se aceptan contribuciones.

**Última actualización**: 3 de diciembre de 2025
**Versión**: 2.2.0 (CLI Profesional - Fases 1-3 completadas)
**Estado**: En Fase 4 (Limpieza y Release)

### Roadmap

- ✅ **Fase 1 (Completada)**: Reorganización de estructura y documentación
- ✅ **Fase 2 (Completada)**: Refactoring de módulos en `api/`, `database/`, `core/`, `utils/`
- ✅ **Fase 3 (Completada)**: CLI profesional con Click
- 🔄 **Fase 4 (En Progreso)**: Limpieza y release v2.2.0
- 🔵 **Futuro**: PyPI, tests, CI/CD

Ver [ROADMAP_MIGRACION.md](ROADMAP_MIGRACION.md) y [CHANGELOG.md](CHANGELOG.md) para detalles completos.

---

## Enlaces Útiles

### Documentación del Proyecto

- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios oficial
- [docs/dev/ARQUITECTURA.md](docs/dev/ARQUITECTURA.md) - Arquitectura del proyecto v2.2.0
- [ROADMAP_MIGRACION.md](ROADMAP_MIGRACION.md) - Plan de migración por fases
- [docs/user/](docs/user/) - Guías para usuarios
- [docs/dev/](docs/dev/) - Documentación técnica
- [docs/database/](docs/database/) - Documentación de base de datos

### Changelogs por Fase

- [CHANGELOG_FASE_1.md](CHANGELOG_FASE_1.md) - Reorganización del proyecto
- [CHANGELOG_FASE_2.md](CHANGELOG_FASE_2.md) - Refactoring de módulos
- [CHANGELOG_FASE_3.md](CHANGELOG_FASE_3.md) - CLI profesional

### Recursos Externos

- [Documentación de Strava API](https://developers.strava.com/docs/reference/)
- [Strava API Settings](https://www.strava.com/settings/api)
- [Issues en GitLab](https://gitlab.com/josefcodelafuente/py-strava/-/issues)

---

**¿Preguntas o problemas?**

1. Ejecuta `python scripts/test_setup.py` para verificar tu instalación
2. Consulta [docs/user/SOLUCION_ERRORES.md](docs/user/SOLUCION_ERRORES.md) para errores comunes
3. Revisa [docs/user/INICIO_RAPIDO.md](docs/user/INICIO_RAPIDO.md) para guía rápida
4. Abre un [issue](https://gitlab.com/josefcodelafuente/py-strava/-/issues) en GitLab
