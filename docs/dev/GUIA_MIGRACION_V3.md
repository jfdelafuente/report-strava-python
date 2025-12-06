# Guía de Migración a v3.0.0

**Fecha**: 6 de diciembre de 2025
**Versión**: 3.0.0

---

## Resumen de Cambios

La versión **3.0.0** introduce cambios importantes (breaking changes) que completan la reestructuración del proyecto iniciada en la Fase 2:

### Cambios Principales

1. ✅ **Eliminado módulo deprecado `py_strava.strava`**
2. ✅ **Eliminada funcionalidad de sincronización de kudos**
3. ✅ **Estructura modular consolidada**: `api/`, `database/`, `utils/`, `core/`, `cli/`

---

## 1. Eliminación del Módulo `py_strava.strava`

### ¿Por qué se eliminó?

El módulo `py_strava.strava` fue marcado como deprecado en v2.0.0 y toda su funcionalidad fue migrada a la nueva estructura modular. Mantener código duplicado generaba:
- Confusión sobre qué módulos usar
- Dificultad en el mantenimiento
- Warnings de deprecación en los logs

### Migración de Imports

#### Antes (v2.x)
```python
from py_strava.strava import strava_token
from py_strava.strava import strava_activities
from py_strava.strava import strava_db_sqlite
from py_strava.strava import strava_db_postgres
from py_strava.strava import strava_fechas
```

#### Después (v3.0.0)
```python
from py_strava.api import auth
from py_strava.api import activities
from py_strava.database import sqlite
from py_strava.database import postgres
from py_strava.utils import dates
```

### Tabla de Mapeo Completa

| Módulo Antiguo (v2.x) | Módulo Nuevo (v3.0.0) | Notas |
|----------------------|----------------------|-------|
| `py_strava.strava.strava_token` | `py_strava.api.auth` | Mismo API, sin cambios |
| `py_strava.strava.strava_token_1` | `py_strava.api.auth` | Mismo API, sin cambios |
| `py_strava.strava.strava_activities` | `py_strava.api.activities` | Sin kudos (ver sección 2) |
| `py_strava.strava.strava_db_sqlite` | `py_strava.database.sqlite` | Mismo API, sin cambios |
| `py_strava.strava.strava_db_postgres` | `py_strava.database.postgres` | Mismo API, sin cambios |
| `py_strava.strava.strava_fechas` | `py_strava.utils.dates` | Mismo API, sin cambios |

---

## 2. Eliminación de Funcionalidad de Kudos

### ¿Por qué se eliminó?

La funcionalidad de sincronización individual de kudos por actividad fue eliminada por:
- Alto costo en llamadas a la API (1 llamada por actividad)
- Información de kudos_count ya disponible en cada actividad
- Bajo valor agregado vs costo de rendimiento

### Cambios en el Código

#### Función eliminada: `load_kudos_to_db()`

**Antes (v2.x)**:
```python
# py_strava/core/sync.py
num_kudos = load_kudos_to_db(conn, access_token, activity_ids)
```

**Después (v3.0.0)**:
```python
# Función completamente eliminada
# Ya no se sincronizan kudos individuales
```

#### Return de `run_sync()`

**Antes (v2.x)**:
```python
return {
    "activities": num_loaded,
    "kudos": num_kudos,  # ❌ Eliminado
    "db_type": DB_TYPE
}
```

**Después (v3.0.0)**:
```python
return {
    "activities": num_loaded,
    "db_type": DB_TYPE
}
```

### Información de Kudos Disponible

El **contador de kudos** (`kudos_count`) sigue disponible en cada actividad:

```python
# Campo kudos_count en tabla Activities
activities = [
    {
        "id": 12345,
        "name": "Morning Run",
        "kudos_count": 15,  # ✅ Sigue disponible
        # ... otros campos
    }
]
```

### Migración de Código

Si tu código dependía de la tabla `Kudos` con información individual:

**Opción 1: Usar kudos_count**
```python
# Antes: obtener kudos individuales
kudos = db.query("SELECT * FROM Kudos WHERE id_activity = ?", (activity_id,))
num_kudos = len(kudos)

# Después: usar kudos_count directamente
activity = db.query("SELECT kudos_count FROM Activities WHERE id_activity = ?", (activity_id,))
num_kudos = activity["kudos_count"]
```

**Opción 2: Implementar tu propia sincronización (si realmente la necesitas)**
```python
from py_strava.api import activities

# Obtener kudos manualmente si es absolutamente necesario
access_token = "..."
activity_id = 12345
kudos_df = activities.request_kudos(access_token, activity_id)
```

---

## 3. Script de Migración Automática

### Para actualizar imports en tu código

```bash
#!/bin/bash
# migrate_to_v3.sh

echo "Migrando código a py-strava v3.0.0..."

# Encuentra todos los archivos Python
find . -name "*.py" -type f -not -path "./venv/*" | while read file; do
    # Backup
    cp "$file" "$file.bak"

    # Migrar imports
    sed -i \
        -e 's/from py_strava\.strava import strava_token/from py_strava.api import auth as strava_token/g' \
        -e 's/from py_strava\.strava import strava_activities/from py_strava.api import activities as strava_activities/g' \
        -e 's/from py_strava\.strava import strava_db_sqlite/from py_strava.database import sqlite as strava_db_sqlite/g' \
        -e 's/from py_strava\.strava import strava_db_postgres/from py_strava.database import postgres as strava_db_postgres/g' \
        -e 's/from py_strava\.strava import strava_fechas/from py_strava.utils import dates as strava_fechas/g' \
        -e 's/from py_strava\.strava\.strava_fechas import/from py_strava.utils.dates import/g' \
        -e 's/from py_strava\.strava\.strava_token_1 import/from py_strava.api.auth import/g' \
        "$file"

    echo "✅ Migrado: $file"
done

echo "✅ Migración completada"
echo "⚠️  Archivos backup guardados como *.bak"
```

### Ejecutar el script

```bash
chmod +x migrate_to_v3.sh
./migrate_to_v3.sh
```

---

## 4. Validación Post-Migración

### Paso 1: Verificar imports

```bash
# Buscar referencias al módulo antiguo
grep -r "from py_strava.strava" . --include="*.py" --exclude-dir=venv

# No debería retornar resultados
```

### Paso 2: Ejecutar tests

```bash
# Tests unitarios
pytest tests/ -v

# Script de verificación
python scripts/test_setup.py
```

### Paso 3: Verificar CLI

```bash
# Verificar comandos CLI
strava --version   # Debe mostrar v3.0.0
strava --help
strava sync --help
strava report --help
```

### Paso 4: Probar funcionalidad

```bash
# Sincronización (sin kudos)
strava sync

# Debe mostrar:
# [SUCCESS] X actividades sincronizadas
# (SIN mención a kudos)

# Generar reporte
strava report
```

---

## 5. Preguntas Frecuentes (FAQ)

### ¿Puedo volver a v2.x?

Sí, puedes hacer downgrade:

```bash
pip install py-strava==2.2.0
```

Sin embargo, **no se recomienda** ya que v2.x no recibirá más actualizaciones.

### ¿Perdí datos de kudos al actualizar?

No. Los datos existentes en la tabla `Kudos` de tu base de datos **no se eliminan**.

Sin embargo:
- Nuevas sincronizaciones no añadirán más kudos individuales
- Sigue teniendo `kudos_count` en cada actividad

### ¿Cómo sincronizo kudos si los necesito?

Si absolutamente necesitas kudos individuales:

```python
from py_strava.api import auth, activities
from py_strava.database import sqlite

# Obtener token
token_data = auth.getTokenFromFile("json/strava_tokens.json")
access_token = token_data["access_token"]

# Obtener actividades
with sqlite.DatabaseConnection("bd/strava.sqlite") as conn:
    result = conn.execute("SELECT id_activity FROM Activities")
    activity_ids = [row[0] for row in result]

    # Sincronizar kudos manualmente
    for activity_id in activity_ids:
        kudos_df = activities.request_kudos(access_token, activity_id)
        # ... procesar kudos
```

### ¿Los comandos CLI cambiaron?

**No**. Los comandos CLI siguen siendo los mismos:

```bash
strava sync      # ✅ Sin cambios
strava report    # ✅ Sin cambios
strava init-db   # ✅ Sin cambios
```

Solo cambió la implementación interna.

### ¿Mi configuración existente sigue funcionando?

**Sí**. Todos los archivos de configuración son compatibles:

```
json/strava_tokens.json          # ✅ Compatible
bd/postgres_credentials.json     # ✅ Compatible
bd/strava.sqlite                 # ✅ Compatible
data/strava_activities.log       # ✅ Compatible
```

---

## 6. Errores Comunes

### Error: `ModuleNotFoundError: No module named 'py_strava.strava'`

**Causa**: Código usando imports antiguos.

**Solución**:
```bash
# Buscar imports antiguos
grep -r "from py_strava.strava" . --include="*.py"

# Actualizar según tabla de mapeo (sección 1)
```

### Error: `KeyError: 'kudos'` en código personalizado

**Causa**: Código esperando `kudos` en el return de `run_sync()`.

**Solución**:
```python
# Antes
result = run_sync()
print(f"Kudos: {result['kudos']}")  # ❌ KeyError

# Después
result = run_sync()
# Eliminar referencia a kudos o usar kudos_count de Activities
```

### Error: Función `load_kudos_to_db` no encontrada

**Causa**: Código usando función eliminada.

**Solución**: Ver sección 2 "Eliminación de Funcionalidad de Kudos"

---

## 7. Recursos Adicionales

### Documentación

- [CHANGELOG.md](../../CHANGELOG.md) - Historial completo de cambios
- [ARQUITECTURA.md](ARQUITECTURA.md) - Arquitectura del proyecto v3.0.0
- [ANALISIS_ELIMINACION_MODULO_STRAVA.md](ANALISIS_ELIMINACION_MODULO_STRAVA.md) - Análisis técnico

### Soporte

Si encuentras problemas durante la migración:

1. Revisa esta guía completa
2. Consulta [docs/user/SOLUCION_ERRORES.md](../user/SOLUCION_ERRORES.md)
3. Abre un issue en [GitLab](https://gitlab.com/josefcodelafuente/py-strava/-/issues)

---

## 8. Checklist de Migración

Usa este checklist para asegurar una migración exitosa:

- [ ] ✅ Backup de tu código y base de datos
- [ ] ✅ Revisar tabla de mapeo de imports (sección 1)
- [ ] ✅ Ejecutar script de migración automática (opcional)
- [ ] ✅ Actualizar imports manualmente
- [ ] ✅ Eliminar referencias a tabla `Kudos` (si aplica)
- [ ] ✅ Actualizar código que usa `result['kudos']`
- [ ] ✅ Ejecutar tests: `pytest tests/ -v`
- [ ] ✅ Ejecutar verificación: `python scripts/test_setup.py`
- [ ] ✅ Probar CLI: `strava sync` y `strava report`
- [ ] ✅ Validar que no hay imports antiguos: `grep -r "py_strava.strava"`
- [ ] ✅ Eliminar archivos backup (*.bak)

---

**¡Bienvenido a py-strava v3.0.0!** 🎉

Hemos completado la reestructuración del proyecto con una arquitectura moderna, modular y mantenible.

**Última actualización**: 6 de diciembre de 2025
**Versión del documento**: 1.0
