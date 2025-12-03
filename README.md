# py-strava

Aplicación Python para sincronizar y analizar actividades de Strava con base de datos local.

## Descripción

**py-strava** es una herramienta que permite:

- Sincronizar automáticamente tus actividades de Strava con una base de datos local
- Almacenar información detallada de actividades y kudos recibidos
- Generar informes y exportar datos a formato CSV
- Mantener un historial completo de tus entrenamientos

El proyecto ha sido completamente refactorizado siguiendo las mejores prácticas de desarrollo en Python, incluyendo logging profesional, manejo robusto de errores, documentación completa y código modular.

## Características

✅ **Sincronización automática**: Obtiene actividades nuevas desde la última sincronización
✅ **Gestión de tokens**: Refresca automáticamente el token de acceso de Strava
✅ **Base de datos**: Soporta SQLite y PostgreSQL
✅ **Kudos tracking**: Registra todos los kudos recibidos en cada actividad
✅ **Informes CSV**: Exporta datos para análisis externo
✅ **Logging completo**: Sistema de logs estructurado para debugging
✅ **Manejo de errores**: Procesamiento robusto que continúa ante fallos individuales
✅ **Configuración flexible**: Variables de entorno y archivos de configuración

## Estructura del Proyecto

```
py-strava/
├── py_strava/                  # Código fuente principal
│   ├── main.py                 # Script principal de sincronización
│   ├── informe_strava.py       # Generación de informes CSV
│   ├── config.py               # Configuración centralizada
│   ├── db_schema.py            # Esquemas SQL y funciones de BD
│   └── strava/                 # Módulos de Strava
│       ├── strava_activities.py    # Gestión de actividades
│       ├── strava_db_postgres.py   # Conexión PostgreSQL
│       ├── strava_db_sqlite.py     # Conexión SQLite
│       ├── strava_token.py         # Gestión de tokens
│       └── strava_fechas.py        # Utilidades de fechas
│
├── scripts/                    # Scripts de utilidad
│   ├── init_database.py        # Inicializar base de datos
│   ├── ejemplo_uso_bd.py       # Ejemplos de uso
│   └── test_setup.py           # Verificar instalación
│
├── docs/                       # Documentación organizada
│   ├── user/                   # Guías para usuarios
│   ├── dev/                    # Documentación técnica
│   └── database/               # Docs de base de datos
│
├── data/                       # Datos generados (logs, CSV)
├── bd/                         # Base de datos SQLite
├── json/                       # Configuración (tokens)
│
├── README.md                   # Este archivo
├── requirements.txt            # Dependencias Python
└── .env.example                # Template de configuración
```

> **Nota**: El proyecto ha sido reorganizado recientemente. Ver [PROPUESTA_REESTRUCTURACION.md](PROPUESTA_REESTRUCTURACION.md) para detalles completos de los cambios.

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

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Verificar instalación

**IMPORTANTE**: Después de instalar, verifica que todo esté correctamente configurado:

```bash
python scripts/test_setup.py
```

Este script verifica:

- ✓ Estructura de directorios
- ✓ Archivos necesarios
- ✓ Dependencias instaladas
- ✓ Imports funcionando
- ✓ Configuración básica

**Opciones del script de verificación**:

```bash
python scripts/test_setup.py           # Verificación completa
python scripts/test_setup.py --quick   # Verificación rápida
python scripts/test_setup.py --verbose # Información detallada
python scripts/test_setup.py --help    # Ver ayuda
```

### 6. Instalación opcional para PostgreSQL

Si vas a usar PostgreSQL, instala las dependencias adicionales:

```bash
# Linux/macOS
sudo apt-get update
sudo apt-get install libpq-dev python3.8-dev
pip install psycopg2

# Windows
pip install psycopg2-binary
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

#### Opción A: SQLite (por defecto - recomendado para desarrollo)

✅ **No requiere configuración** - El archivo SQLite se crea automáticamente en `bd/strava.sqlite`.

El proyecto detecta automáticamente si `psycopg2` está disponible. Si no lo está, usa SQLite.

#### Opción B: PostgreSQL (opcional - para producción)

**Método 1: Archivo de credenciales (recomendado)**

Crea el archivo `bd/postgres_credentials.json` (puedes usar `postgres_credentials.json.example` como plantilla):

```json
{
  "server": "localhost",
  "database": "strava",
  "username": "postgres",
  "password": "tu_password_aqui",
  "port": "5432"
}
```

**Método 2: Variables de entorno**

Configura las variables de entorno o edita [config.py](py_strava/config.py):

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=strava
export DB_USER=postgres
export DB_PASSWORD=tu_password
```

**Método 3: Instalar psycopg2**

```bash
pip install psycopg2-binary
```

Si tienes problemas en Windows, el proyecto funcionará perfectamente con SQLite (opción por defecto).

### 4. Inicializar la base de datos

**Para SQLite** (recomendado para empezar):

```bash
python scripts/init_database.py
```

Este script:

- Crea automáticamente el archivo `bd/strava.sqlite`
- Crea las tablas `Activities` y `Kudos`
- Verifica que todo esté correctamente configurado

**Opciones disponibles**:

```bash
python scripts/init_database.py              # Crear tablas si no existen
python scripts/init_database.py --verify     # Verificar tablas existentes
python scripts/init_database.py --reset      # Recrear todas las tablas (¡cuidado!)
```

Ver [docs/database/INIT_DATABASE.md](docs/database/INIT_DATABASE.md) para más detalles.

**Para PostgreSQL**:

Si configuraste PostgreSQL, el script detectará automáticamente las credenciales y usará PostgreSQL en lugar de SQLite.

## Uso

### Sincronizar actividades

Ejecuta el script principal para sincronizar tus actividades de Strava:

```bash
python -m py_strava.main
```

**IMPORTANTE:** Siempre ejecuta con `python -m py_strava.main` desde la raíz del proyecto, no con `python py_strava/main.py`.

**Salida esperada:**

```
2025-11-26 10:30:15 - INFO - === Inicio de sincronización de Strava ===
2025-11-26 10:30:15 - INFO - Conexión a base de datos establecida
2025-11-26 10:30:16 - INFO - Token de acceso obtenido correctamente
2025-11-26 10:30:16 - INFO - Última sincronización: 2025-11-20T08:00:00Z
2025-11-26 10:30:17 - INFO - Obteniendo actividades desde Strava...
2025-11-26 10:30:18 - INFO - 5 actividades obtenidas
2025-11-26 10:30:19 - INFO - 5 actividades cargadas en la base de datos
2025-11-26 10:30:22 - INFO - 12 kudos cargados en la base de datos
2025-11-26 10:30:22 - INFO - Log actualizado: 2025-11-26T10:30:22Z - 5 actividades
2025-11-26 10:30:22 - INFO - === Sincronización completada exitosamente ===
```

### Generar informes

Genera un informe CSV con actividades y kudos:

```bash
python -m py_strava.informe_strava
```

**Salida esperada:**

```
2025-11-26 10:35:00 - INFO - === Inicio de generación de informe de kudos ===
2025-11-26 10:35:00 - INFO - Conexión establecida con la base de datos: bd/strava.sqlite
2025-11-26 10:35:00 - INFO - 150 registros obtenidos de la base de datos
2025-11-26 10:35:01 - INFO - Datos exportados correctamente a data/strava_data2.csv
2025-11-26 10:35:01 - INFO - Total de registros exportados: 150
2025-11-26 10:35:01 - INFO - Conexión a la base de datos cerrada
2025-11-26 10:35:01 - INFO - === Generación de informe completada ===
2025-11-26 10:35:01 - INFO - Informe generado exitosamente en: data/strava_data2.csv
```

El archivo CSV generado tendrá el siguiente formato:

```csv
FIRST_NAME,LAST_NAME,TIPO,ACTIVIDAD,START_DATE
Juan,García,Run,12345678,2025-11-26T08:00:00Z
María,López,Ride,12345679,2025-11-25T17:30:00Z
...
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

### v2.1.0 - Reorganización del Proyecto (Diciembre 2025)

El proyecto ha sido reorganizado para mejor mantenibilidad y experiencia del desarrollador:

- 📁 **Estructura organizada**: Documentación en `/docs`, scripts en `/scripts`
- 🧪 **Tests mejorados**: Script de verificación con múltiples modos
- 📚 **Documentación clara**: Separada por audiencia (usuario/desarrollador/BD)
- 🔧 **Scripts de utilidad**: Herramientas para setup e inicialización

Ver [PROPUESTA_REESTRUCTURACION.md](PROPUESTA_REESTRUCTURACION.md) para detalles completos.

### v2.0.0 - Refactorización Completa (Noviembre 2025)

Este proyecto ha sido completamente refactorizado. Consulta [docs/dev/](docs/dev/) para conocer en detalle:

- ✅ Sistema de logging profesional
- ✅ Manejo robusto de errores
- ✅ Código modular y documentado
- ✅ Type hints y validaciones
- ✅ Optimizaciones de rendimiento
- ✅ Configuración centralizada
- ✅ Mejores prácticas de Python (PEP 8)

**Comparación de métricas:**

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Funciones documentadas | 0% | 100% | +100% |
| Cobertura de logging | 10% | 100% | +90% |
| Manejo de errores | Básico | Completo | ✅ |
| Modularidad | Baja | Alta | ✅ |

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

**Fase 2 - Refactoring de módulos**:

- [ ] Reorganizar código en `api/`, `database/`, `core/`, `utils/`
- [ ] Crear wrappers de compatibilidad

**Fase 3 - CLI profesional**:

- [ ] Implementar CLI con Click: `strava sync`, `strava report`
- [ ] Instalación con pip: `pip install -e .`

**Fase 4 - Mejoras adicionales**:

- [ ] Tests unitarios con pytest
- [ ] CI/CD con GitLab CI
- [ ] Validación de tipos con mypy
- [ ] Linting automático (black, flake8)
- [ ] Dashboard web interactivo (futuro)

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
**Versión**: 2.1.0 (Reorganizado - Fase 1 completada)

### Roadmap

- ✅ **Fase 1 (Completada)**: Reorganización de estructura y documentación
- ⏳ **Fase 2 (Planificada)**: Refactoring de módulos
- ⏳ **Fase 3 (Planificada)**: CLI profesional con Click
- 🔵 **Fase 4 (Opcional)**: Limpieza y release PyPI

Ver [ROADMAP_MIGRACION.md](ROADMAP_MIGRACION.md) para detalles completos.

---

## Enlaces Útiles

### Documentación del Proyecto

- [PROPUESTA_REESTRUCTURACION.md](PROPUESTA_REESTRUCTURACION.md) - Propuesta de reorganización del proyecto
- [ROADMAP_MIGRACION.md](ROADMAP_MIGRACION.md) - Plan de migración por fases
- [COMPARACION_ESTRUCTURA.md](COMPARACION_ESTRUCTURA.md) - Comparativa antes/después
- [RESUMEN_EJECUTIVO_REESTRUCTURACION.md](RESUMEN_EJECUTIVO_REESTRUCTURACION.md) - Resumen ejecutivo
- [docs/user/](docs/user/) - Guías para usuarios
- [docs/dev/](docs/dev/) - Documentación técnica
- [docs/database/](docs/database/) - Documentación de base de datos

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
