# Solución de Errores - py-strava

## Problemas Identificados y Resueltos

### 1. ❌ Error de Imports Relativos

**Problema:** Los archivos `main.py` e `informe_strava.py` usaban imports incorrectos:
```python
import strava.strava_token_1 as stravaToken  # ❌ Incorrecto
```

**Solución Aplicada:** ✅ Se corrigieron a imports absolutos desde el paquete:
```python
from py_strava.strava import strava_token_1 as stravaToken  # ✅ Correcto
```

**Archivos modificados:**
- [py_strava/main.py](py_strava/main.py#L18-L21)
- [py_strava/informe_strava.py](py_strava/informe_strava.py#L15)

---

### 2. ❌ Archivo de Credenciales Faltante

**Problema:** El código buscaba `bd/postgres_credentials.json` que no existía, causando un error al conectar con PostgreSQL.

**Solución Aplicada:** ✅ Se modificó `strava_bd_postgres.py` para:
1. Buscar primero el archivo de credenciales JSON
2. Si no existe, usar las variables de entorno de [config.py](py_strava/config.py)
3. Mejorar el manejo de errores con mensajes descriptivos

**Archivo creado:**
- `bd/postgres_credentials.json.example` - Plantilla de ejemplo

**Archivo modificado:**
- [py_strava/strava/strava_bd_postgres.py](py_strava/strava/strava_bd_postgres.py#L7-L35)

---

### 3. ❌ Directorio `data/` No Existía

**Problema:** El código intentaba escribir en `data/strava_activities_bd.log` sin verificar si el directorio existía.

**Solución Aplicada:** ✅ Se agregó código para crear el directorio automáticamente:
```python
log_dir = Path('data')
log_dir.mkdir(exist_ok=True)
```

**Archivo modificado:**
- [py_strava/strava/strava_bd_postgres.py](py_strava/strava/strava_bd_postgres.py#L40-L42)

---

### 4. ❌ Paquetes Python No Configurados

**Problema:** Faltaban archivos `__init__.py` para que Python reconozca los directorios como paquetes.

**Solución Aplicada:** ✅ Se crearon los archivos:
- `py_strava/__init__.py`
- `py_strava/strava/__init__.py`

---

### 5. ❌ Import Incorrecto en strava_bd_1.py

**Problema:** El archivo intentaba importar `Statement` desde `sqlite3.dbapi2`, que no existe en versiones modernas de Python:
```python
from sqlite3.dbapi2 import Statement  # ❌ No existe
```

**Solución Aplicada:** ✅ Se eliminó el import innecesario y se agregó `Path` para manejo de directorios:
```python
from pathlib import Path  # ✅ Correcto
```

**Archivo modificado:**
- [py_strava/strava/strava_bd_1.py](py_strava/strava/strava_bd_1.py#L3)

---

## Cómo Ejecutar el Proyecto Ahora

### Opción 1: Usar PostgreSQL con Archivo de Credenciales

1. **Crea el archivo de credenciales:**
```bash
cp bd/postgres_credentials.json.example bd/postgres_credentials.json
```

2. **Edita el archivo con tus datos:**
```json
{
  "server": "localhost",
  "database": "strava",
  "username": "postgres",
  "password": "tu_password",
  "port": "5432"
}
```

3. **Ejecuta el script desde la raíz del proyecto:**
```bash
python -m py_strava.main
```

### Opción 2: Usar PostgreSQL con Variables de Entorno

1. **Configura las variables de entorno:**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=strava
export DB_USER=postgres
export DB_PASSWORD=tu_password
```

2. **Ejecuta el script:**
```bash
python -m py_strava.main
```

### Opción 3: Usar SQLite (desarrollo)

1. **Ejecuta directamente** (el archivo SQLite se crea automáticamente):
```bash
python -m py_strava.main
```

---

## Generar Informes

Para generar el informe CSV de kudos y actividades:

```bash
python -m py_strava.informe_strava
```

El archivo se generará en `data/strava_data2.csv`

---

## Verificar que Todo Funciona

### 1. Verificar instalación de dependencias:
```bash
pip install -r requirements.txt
```

### 2. Verificar estructura del proyecto:
```bash
py-strava/
├── py_strava/
│   ├── __init__.py          ✅ CREADO
│   ├── main.py              ✅ CORREGIDO
│   ├── informe_strava.py    ✅ CORREGIDO
│   ├── config.py
│   ├── db_schema.py
│   └── strava/
│       ├── __init__.py      ✅ CREADO
│       ├── strava_bd_postgres.py  ✅ CORREGIDO
│       └── ...
├── bd/
│   └── postgres_credentials.json.example  ✅ CREADO
└── requirements.txt
```

### 3. Probar la conexión a la base de datos:
```python
python -c "from py_strava.strava import strava_bd_postgres as db; conn = db.sql_connection(); print('✅ Conexión exitosa')"
```

---

## Errores Comunes y Soluciones

### Error: `ModuleNotFoundError: No module named 'py_strava'`

**Causa:** Estás ejecutando el script desde dentro del directorio `py_strava/`

**Solución:** Ejecuta desde la raíz del proyecto:
```bash
cd "c:\My Program Files\workspace-python\report-strava-python"
python -m py_strava.main
```

### Error: `No such file or directory: 'bd/postgres_credentials.json'`

**Causa:** No has creado el archivo de credenciales y tampoco tienes variables de entorno

**Solución:** Crea el archivo o configura las variables de entorno (ver arriba)

### Error: `psycopg2.OperationalError: could not connect to server`

**Causa:** PostgreSQL no está ejecutándose o las credenciales son incorrectas

**Solución:**
1. Verifica que PostgreSQL esté ejecutándose
2. Comprueba las credenciales
3. Prueba la conexión: `psql -h localhost -U postgres -d strava`

### Error: `No module named 'psycopg2'`

**Causa:** No has instalado las dependencias

**Solución:**
```bash
pip install -r requirements.txt
```

---

## Verificación de la Instalación

Para verificar que todas las correcciones funcionan correctamente, ejecuta:

```bash
python test_setup.py
```

Este script verificará:
- ✅ Estructura de directorios
- ✅ Archivos necesarios
- ✅ Dependencias instaladas
- ✅ Imports correctos
- ✅ Configuración válida

**Resultado esperado:**
```
[SUCCESS] TODAS LAS VERIFICACIONES PASARON

Puedes ejecutar:
  python -m py_strava.main
  python -m py_strava.informe_strava
```

---

## Resumen de Cambios

| Archivo | Estado | Descripción |
|---------|--------|-------------|
| `py_strava/__init__.py` | ✅ CREADO | Marca el directorio como paquete Python |
| `py_strava/strava/__init__.py` | ✅ CREADO | Marca el subdirectorio como paquete |
| `py_strava/main.py` | ✅ CORREGIDO | Imports corregidos (líneas 18-21) |
| `py_strava/informe_strava.py` | ✅ CORREGIDO | Imports corregidos (línea 15) |
| `py_strava/strava/strava_bd_postgres.py` | ✅ CORREGIDO | Manejo de credenciales mejorado + creación automática de directorios |
| `py_strava/strava/strava_bd_1.py` | ✅ CORREGIDO | Import incorrecto eliminado + creación automática de directorios |
| `bd/postgres_credentials.json.example` | ✅ CREADO | Plantilla de ejemplo para credenciales |
| `test_setup.py` | ✅ CREADO | Script de verificación de configuración |
| `SOLUCION_ERRORES.md` | ✅ CREADO | Este documento |
| `README.md` | ✅ ACTUALIZADO | Documentación mejorada |

---

## Errores Comunes Adicionales

### 7. ❌ Archivo de Log No Existe

**Problema:** Error al intentar leer o escribir en `data/strava_activities.log`.

**Síntomas:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/strava_activities.log'
```

**Causa:** El archivo de log no se crea automáticamente hasta la primera sincronización.

**Soluciones:**

**Opción 1 - Dejar que se cree automáticamente (Recomendado):**

```bash
# El archivo se crea automáticamente en la primera sincronización
strava sync
```

**Opción 2 - Crear manualmente:**

```bash
# Linux/Mac
touch data/strava_activities.log

# Windows (CMD)
type nul > data\strava_activities.log

# Windows (PowerShell)
New-Item -Path data\strava_activities.log -ItemType File -Force
```

**Función del archivo:**

- Registra todas las actividades sincronizadas
- Permite sincronización incremental (solo actividades nuevas)
- Formato: una línea por actividad con ID y fecha

**Ejemplo de contenido:**

```text
12345678 - 2025-11-26T08:00:00Z
12345679 - 2025-11-25T17:30:00Z
12345680 - 2025-11-24T09:15:00Z
```

---

## Próximos Pasos Recomendados

1. ✅ Crea los directorios necesarios: `mkdir -p bd data json`
2. ✅ Configura tus credenciales de PostgreSQL (opcional)
3. ✅ Configura tu token de Strava en `json/strava_tokens.json`
4. ✅ Ejecuta `strava sync` para sincronizar (crea el log automáticamente)
5. ✅ Genera informes con `strava report`

---

**Fecha de corrección:** 3 de diciembre de 2025
**Todos los errores identificados han sido resueltos** ✅
