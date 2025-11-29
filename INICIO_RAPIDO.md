# 🚀 Inicio Rápido - py-strava

Esta guía te ayudará a ejecutar el proyecto en **menos de 5 minutos** usando SQLite (sin necesidad de PostgreSQL).

---

## ✅ Pasos Rápidos

### 1. Abrir PowerShell en el directorio del proyecto

```powershell
cd "C:\My Program Files\workspace-python\report-strava-python"
```

### 2. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

Si da error de política de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias básicas

```powershell
pip install pandas numpy requests python-dateutil
```

**Nota:** Esto puede tomar 2-3 minutos. Pandas es el paquete más grande.

### 4. Verificar instalación

```powershell
python test_setup.py
```

**Deberías ver:**
```
[SUCCESS] TODAS LAS VERIFICACIONES PASARON

Puedes ejecutar:
  python -m py_strava.main
  python -m py_strava.informe_strava
```

---

## 🎯 Configurar Strava

### 5. Crear archivo de tokens

Crea el archivo `json/strava_tokens.json`:

```json
{
  "token_type": "Bearer",
  "expires_at": 0,
  "expires_in": 0,
  "refresh_token": "TU_REFRESH_TOKEN_AQUI",
  "access_token": "",
  "client_id": "TU_CLIENT_ID",
  "client_secret": "TU_CLIENT_SECRET"
}
```

**¿Dónde obtener estos datos?**
1. Ve a https://www.strava.com/settings/api
2. Crea una aplicación
3. Copia el `client_id` y `client_secret`
4. Autoriza la aplicación para obtener el `refresh_token`

---

## ▶️ Ejecutar el Proyecto

### 6. Sincronizar actividades

```powershell
python -m py_strava.main
```

**Salida esperada:**
```
2025-11-26 15:30:00 - INFO - === Inicio de sincronización de Strava ===
2025-11-26 15:30:00 - INFO - Usando base de datos: SQLite
2025-11-26 15:30:00 - INFO - Conexión a SQLite establecida: ./bd/strava.sqlite
2025-11-26 15:30:01 - INFO - Token de acceso obtenido correctamente
2025-11-26 15:30:02 - INFO - Obteniendo actividades desde Strava...
2025-11-26 15:30:03 - INFO - 10 actividades obtenidas
2025-11-26 15:30:04 - INFO - 10 actividades cargadas en la base de datos
2025-11-26 15:30:05 - INFO - 25 kudos cargados en la base de datos
2025-11-26 15:30:05 - INFO - === Sincronización completada exitosamente ===
```

### 7. Generar informe CSV

```powershell
python -m py_strava.informe_strava
```

El informe se guardará en `data/strava_data2.csv`

---

## 🔧 Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'pandas'"

**Solución:**
```powershell
pip install pandas numpy requests python-dateutil
```

### Error: "No such file or directory: json/strava_tokens.json"

**Solución:** Crea el archivo siguiendo el paso 5.

### Error: "Failed to build pandas"

**Solución:** Intenta instalar con wheels precompilados:
```powershell
pip install --only-binary :all: pandas numpy
```

Si persiste el error, pandas tomará más tiempo en compilarse (5-10 minutos), pero eventualmente se instalará.

---

## 📊 Base de Datos

**Por defecto usa SQLite** - No requiere instalación ni configuración adicional.

- La base de datos se crea automáticamente en: `bd/strava.sqlite`
- Puedes abrirla con cualquier visor de SQLite
- Si quieres usar PostgreSQL, consulta el [README.md](README.md)

---

## 🎉 ¡Listo!

Ya puedes:
- ✅ Sincronizar tus actividades de Strava
- ✅ Almacenarlas en una base de datos local
- ✅ Generar informes en CSV
- ✅ Analizar tus entrenamientos

---

## 📖 Documentación Adicional

- [README.md](README.md) - Documentación completa
- [SOLUCION_ERRORES.md](SOLUCION_ERRORES.md) - Guía de solución de problemas
- [RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md) - Historial de cambios

---

## ❓ Preguntas Frecuentes

**¿Necesito PostgreSQL?**
No, el proyecto funciona perfectamente con SQLite por defecto.

**¿Cuánto tiempo toma la instalación?**
2-3 minutos para instalar las dependencias.

**¿Puedo usar PostgreSQL después?**
Sí, solo instala `psycopg2-binary` y el proyecto lo detectará automáticamente.

**¿Dónde se guardan los datos?**
- Base de datos: `bd/strava.sqlite`
- Informes CSV: `data/strava_data2.csv`
- Logs: `data/strava_activities.log`

---

**¿Problemas?** Consulta [SOLUCION_ERRORES.md](SOLUCION_ERRORES.md) o ejecuta `python test_setup.py`
