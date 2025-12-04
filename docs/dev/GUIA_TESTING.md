# Guía de Configuración del Entorno de Testing

Esta guía te ayudará a configurar correctamente el entorno de testing para el proyecto `report-strava-python` y ejecutar los tests con garantías.

## 1. Requisitos Previos

- **Python**: 3.8 o superior
- **pip**: Gestor de paquetes de Python
- **Git**: Para control de versiones

## 2. Configuración Inicial del Entorno

### 2.1. Crear y Activar Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En Linux/macOS:
source venv/bin/activate
```

### 2.2. Instalar Dependencias del Proyecto

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar el proyecto en modo desarrollo
pip install -e .

# Instalar dependencias de testing
pip install pytest pytest-cov pytest-mock
```

### 2.3. Verificar Instalación

```bash
# Verificar que pytest está instalado
pytest --version

# Verificar que pytest-mock está instalado
python -m pip show pytest-mock

# Verificar que pytest-cov está instalado
python -m pip show pytest-cov
```

Deberías ver algo como:
```
pytest 9.0.1
pytest-mock 3.15.1
pytest-cov 7.0.0
```

## 3. Estructura de Directorios Necesaria

Antes de ejecutar los tests, asegúrate de que existen los siguientes directorios:

```bash
# Crear directorios de datos de prueba si no existen
mkdir -p data/test
mkdir -p json/test
mkdir -p bd

# Verificar estructura
ls -la data/test
ls -la json/test
```

### 3.1. Archivos de Datos de Prueba

Verifica que existen estos archivos:

**data/test/strava_activities_all_fields.csv**
```csv
id,name,start_date_local,type,distance,moving_time,elapsed_time,total_elevation_gain,end_latlng,kudos_count,external_id
12345,Morning Run,2020-03-31T17:58:15Z,Run,5000.0,1800,2000,50.0,"[40.7128, -74.0060]",3,ext_001
```

**json/test/strava_tokens.json**
```json
{
    "token_type": "Bearer",
    "access_token": "f4e2939500ffa174654f91a9177e05b87d217938",
    "expires_at": 1613511684,
    "expires_in": 21600,
    "refresh_token": "e518c071c6bed349dbfb9b46e1e75efab02e4ff1"
}
```

## 4. Comandos para Ejecutar Tests

### 4.1. Limpiar Cache (Recomendado antes de cada sesión)

```bash
# Limpiar cache de pytest
pytest --cache-clear

# Limpiar archivos .pyc y __pycache__
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# En Windows PowerShell:
Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Filter *.pyc | Remove-Item -Force
```

### 4.2. Ejecutar Todos los Tests

```bash
# Ejecutar todos los tests unitarios
python -m pytest tests/unit/ -v

# Salida esperada: 102 passed in ~7-8s
```

### 4.3. Ejecutar Tests Específicos

```bash
# Ejecutar tests de un archivo específico
python -m pytest tests/unit/test_strava_token.py -v

# Ejecutar una clase específica de tests
python -m pytest tests/unit/test_strava_token.py::TestStravaToken -v

# Ejecutar un test específico
python -m pytest tests/unit/test_strava_token.py::TestStravaToken::test_get_token_from_file -v
```

### 4.4. Ejecutar Tests con Diferentes Niveles de Detalle

```bash
# Modo silencioso (solo muestra resumen)
python -m pytest tests/unit/ -q

# Modo verbose (muestra cada test)
python -m pytest tests/unit/ -v

# Modo extra verbose (muestra más detalles)
python -m pytest tests/unit/ -vv

# Mostrar output de prints (útil para debugging)
python -m pytest tests/unit/ -v -s

# Mostrar traceback completo en errores
python -m pytest tests/unit/ -v --tb=long

# Mostrar traceback corto (recomendado)
python -m pytest tests/unit/ -v --tb=short
```

### 4.5. Ejecutar Tests con Cobertura

```bash
# Ejecutar tests con reporte de cobertura
python -m pytest tests/unit/ --cov=py_strava --cov-report=term-missing

# Generar reporte HTML de cobertura
python -m pytest tests/unit/ --cov=py_strava --cov-report=html

# Abrir reporte HTML (se genera en htmlcov/index.html)
# En Windows:
start htmlcov/index.html
# En Linux/macOS:
open htmlcov/index.html
```

### 4.6. Ejecutar Tests con Marcadores (Markers)

```bash
# Ejecutar solo tests marcados como 'unit'
python -m pytest tests/unit/ -v -m unit

# Ejecutar solo tests marcados como 'db'
python -m pytest tests/unit/ -v -m db

# Excluir tests lentos
python -m pytest tests/unit/ -v -m "not slow"
```

### 4.7. Ejecutar Tests en Paralelo (Opcional)

```bash
# Instalar plugin para ejecución paralela
pip install pytest-xdist

# Ejecutar tests en paralelo (usa todos los CPUs)
python -m pytest tests/unit/ -v -n auto

# Ejecutar tests en 4 procesos paralelos
python -m pytest tests/unit/ -v -n 4
```

## 5. Solución de Problemas Comunes

### 5.1. Error: "ModuleNotFoundError: No module named 'pytest'"

**Solución:**
```bash
pip install pytest pytest-cov pytest-mock
```

### 5.2. Error: "FileNotFoundError: strava_tokens.json"

**Solución:**
```bash
# Crear directorio y archivo
mkdir -p json/test
echo '{"token_type": "Bearer", "access_token": "f4e2939500ffa174654f91a9177e05b87d217938", "expires_at": 1613511684, "expires_in": 21600, "refresh_token": "e518c071c6bed349dbfb9b46e1e75efab02e4ff1"}' > json/test/strava_tokens.json
```

### 5.3. Error: "fixture 'mocker' not found"

**Solución:**
```bash
pip install pytest-mock
```

### 5.4. Tests Pasan Individualmente pero Fallan en Suite Completa

**Solución:**
```bash
# Limpiar cache completamente
pytest --cache-clear
rm -rf .pytest_cache
rm -rf htmlcov
rm -rf .coverage

# Ejecutar de nuevo
python -m pytest tests/unit/ -v
```

### 5.5. Error: "ImportError: cannot import name 'X' from 'py_strava'"

**Solución:**
```bash
# Reinstalar el proyecto en modo desarrollo
pip install -e .
```

### 5.6. Error: "ModuleNotFoundError: No module named 'py_strava'" (CRÍTICO)

Este es el error más común y crítico al ejecutar tests. Se manifiesta de varias formas:

**Síntomas:**

```text
ERROR collecting tests/unit/test_strava_token.py
ImportError while importing test module
E   ModuleNotFoundError: No module named 'py_strava'
```

O también puede aparecer como:

```text
ERROR at setup of TestStravaToken.test_no_refresh_token_with_mock
```

**Causa:**
El paquete `py_strava` no está instalado en modo desarrollo (editable mode), por lo que Python no puede encontrar el módulo.

**Solución:**

```bash
# Instalar el paquete en modo desarrollo (editable)
pip install -e .
```

**Verificación:**

```bash
# Verificar que el paquete está instalado correctamente
python -c "import py_strava; print(py_strava.__version__)"

# Debe mostrar: 2.2.0
```

**Nota Importante:**

- Este comando **debe ejecutarse siempre** después de clonar el repositorio
- Debe ejecutarse desde el directorio raíz del proyecto
- El modo desarrollo (`-e`) permite que los cambios en el código se reflejen inmediatamente sin reinstalar

## 6. Workflow Recomendado para Desarrollo

### 6.1. Antes de Empezar a Trabajar

```bash
# 1. Activar entorno virtual
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 2. Limpiar cache
pytest --cache-clear

# 3. Ejecutar tests para verificar estado inicial
python -m pytest tests/unit/ -v
```

### 6.2. Durante el Desarrollo

```bash
# Ejecutar solo los tests relacionados con tu cambio
python -m pytest tests/unit/test_mi_modulo.py -v

# Ejecutar con coverage para ver qué falta probar
python -m pytest tests/unit/test_mi_modulo.py --cov=py_strava.mi_modulo --cov-report=term-missing
```

### 6.3. Antes de Hacer Commit

```bash
# 1. Ejecutar todos los tests
python -m pytest tests/unit/ -v

# 2. Verificar cobertura
python -m pytest tests/unit/ --cov=py_strava --cov-report=term-missing

# 3. Si todo pasa, hacer commit
git add .
git commit -m "Descripción del cambio"
```

## 7. Configuración de pytest.ini

El proyecto ya tiene configurado `pytest.ini` con las siguientes opciones:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    db: marks tests that require database
    api: marks tests that interact with Strava API
addopts =
    -ra
    --strict-markers
```

## 8. Resumen de Comandos Más Usados

```bash
# Comando diario recomendado (limpia + ejecuta + muestra cobertura)
pytest --cache-clear && python -m pytest tests/unit/ -v --cov=py_strava --cov-report=term-missing

# Comando rápido (solo ejecutar tests)
python -m pytest tests/unit/ -v

# Comando para debugging (con prints)
python -m pytest tests/unit/test_mi_archivo.py -v -s

# Comando para CI/CD (con coverage y XML)
python -m pytest tests/unit/ --cov=py_strava --cov-report=xml --cov-report=term-missing
```

## 9. Script de Diagnóstico Automático

El proyecto incluye un script de diagnóstico que verifica automáticamente todo el entorno de testing.

### 9.1. Uso del Script

```bash
# Ejecutar diagnóstico completo
python scripts/diagnostico_tests.py
```

### 9.2. Verificaciones que Realiza

El script verifica automáticamente los siguientes aspectos:

1. ✅ **Versión de Python** - Verifica que sea 3.8 o superior
2. ✅ **Dependencias instaladas** - pytest, pytest-cov, pytest-mock
3. ✅ **Estructura de directorios** - tests/, data/test/, json/test/, bd/, etc.
4. ✅ **Archivos de datos de prueba** - CSV y JSON necesarios
5. ✅ **Archivos de test** - Verifica que existan todos los test_*.py
6. ✅ **Configuración pytest.ini** - Verifica que el archivo existe
7. ✅ **Ejecución de test simple** - Ejecuta un test básico para verificar funcionamiento

### 9.3. Salida Esperada

```text
============================================================
DIAGNÓSTICO DEL ENTORNO DE TESTING
============================================================

============================================================
1. VERIFICACIÓN DE PYTHON
============================================================
Versión de Python: 3.11.2
Ejecutable: C:\Program Files (x86)\Python\python.exe
✅ Versión de Python es compatible (>=3.8)

============================================================
2. VERIFICACIÓN DE DEPENDENCIAS
============================================================
✅ pytest: v9.0.1
✅ pytest-cov: v7.0.0
✅ pytest-mock: vdesconocida

============================================================
3. VERIFICACIÓN DE ESTRUCTURA DE DIRECTORIOS
============================================================
✅ tests/
✅ tests/unit/
✅ data/test/
✅ json/test/
✅ bd/
✅ py_strava/
✅ docs/dev/

============================================================
4. VERIFICACIÓN DE ARCHIVOS DE DATOS DE PRUEBA
============================================================
✅ data/test/strava_activities_all_fields.csv (217 bytes)
✅ json/test/strava_tokens.json (220 bytes)

============================================================
5. VERIFICACIÓN DE ARCHIVOS DE TEST
============================================================
Encontrados 8 archivos de test:
  ✅ test_config.py
  ✅ test_core_reports.py
  ✅ test_database_schema.py
  ✅ test_database_sqlite.py
  ✅ test_fechas.py
  ✅ test_imports.py
  ✅ test_strava_token.py
  ✅ test_version.py

============================================================
6. VERIFICACIÓN DE PYTEST.INI
============================================================
✅ pytest.ini encontrado

============================================================
7. EJECUCIÓN DE TEST SIMPLE
============================================================
✅ Tests ejecutados correctamente

============================================================
RESUMEN
============================================================
Python.................................. ✅ OK
Dependencias............................ ✅ OK
Estructura de directorios............... ✅ OK
Archivos de datos....................... ✅ OK
Archivos de test........................ ✅ OK
pytest.ini.............................. ✅ OK
Test simple............................. ✅ OK

✅ Todas las verificaciones pasaron (7/7)

🎉 El entorno está correctamente configurado!
```

### 9.4. Cuándo Usar el Script de Diagnóstico

Ejecuta este script en las siguientes situaciones:

- **Después de clonar el repositorio** - Para verificar que todo está correctamente configurado
- **Cuando los tests fallan inesperadamente** - Para identificar problemas de configuración
- **Antes de reportar un error** - Para confirmar que el entorno está bien configurado
- **Después de actualizar dependencias** - Para verificar compatibilidad

### 9.5. Interpretando Errores

Si alguna verificación falla (muestra ❌), el script indicará qué está mal:

- **Python**: Actualiza a Python 3.8 o superior
- **Dependencias**: Ejecuta `pip install pytest pytest-cov pytest-mock`
- **Estructura**: Crea los directorios faltantes con `mkdir`
- **Archivos de datos**: Consulta la sección 3.1 de esta guía
- **pytest.ini**: Verifica que el archivo existe en la raíz del proyecto

## 10. Verificación Final del Entorno

Ejecuta este comando para verificar que todo está correctamente configurado:

```bash
# Test de verificación completo
python -m pytest tests/unit/ -v --tb=short --cov=py_strava --cov-report=term-missing
```

**Resultado esperado:**
```
========================= 102 passed in ~7-8s =========================
Coverage: 23%
```

Si ves este resultado, tu entorno está correctamente configurado y listo para usar.

## 11. Estructura de Tests del Proyecto

```
tests/
├── conftest.py              # Fixtures compartidas
├── unit/
│   ├── test_config.py       # Tests de configuración (11 tests)
│   ├── test_database_sqlite.py  # Tests de SQLite (28 tests)
│   ├── test_database_schema.py  # Tests de schema DB (18 tests)
│   ├── test_core_reports.py     # Tests de reportes (26 tests)
│   ├── test_strava_token.py     # Tests de tokens (8 tests)
│   ├── test_fechas.py           # Tests de fechas (3 tests)
│   ├── test_imports.py          # Tests de imports (6 tests)
│   └── test_version.py          # Tests de versión (2 tests)
└── integration/             # Tests de integración (futuros)
```

## 12. Métricas de Cobertura por Módulo

| Módulo | Cobertura | Tests |
|--------|-----------|-------|
| `py_strava/config.py` | 100% | 11 |
| `py_strava/database/sqlite.py` | 91% | 28 |
| `py_strava/database/schema.py` | 53% | 18 |
| `py_strava/core/reports.py` | 90% | 26 |
| `py_strava/strava/strava_token_1.py` | 89% | 8 |
| `py_strava/strava/strava_fechas.py` | 100% | 3 |
| **Total Global** | **23%** | **102** |

## 13. Recursos Adicionales

- **Documentación de pytest**: https://docs.pytest.org/
- **Documentación de pytest-mock**: https://pytest-mock.readthedocs.io/
- **Documentación de pytest-cov**: https://pytest-cov.readthedocs.io/
- **Roadmap de Testing del Proyecto**: [ROADMAP_TESTING.md](ROADMAP_TESTING.md)

---

**Última actualización**: 2025-12-04
**Versión del documento**: 1.0
**Autor**: Claude Code Assistant
