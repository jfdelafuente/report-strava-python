# Roadmap de Migración - py-strava v2.1.0

## Línea de Tiempo

```
Semana 1          Semana 2-3        Semana 4-5        Semana 6+
┌─────────┐      ┌──────────┐      ┌──────────┐     ┌─────────┐
│ Fase 1  │─────▶│  Fase 2  │─────▶│  Fase 3  │────▶│ Fase 4  │
└─────────┘      └──────────┘      └──────────┘     └─────────┘
Organizar        Refactor          Nuevo CLI        Limpieza
estructura       módulos           profesional      y release
1-2 horas        1 semana          3-5 días         Variable

  🟢 Bajo          🟡 Medio          🟡 Medio         🔵 Opcional
  riesgo           riesgo            riesgo           riesgo
```

---

## Fase 1: Reorganización de Estructura 🟢

**Duración**: 1-2 horas
**Riesgo**: Muy bajo
**Reversible**: Sí (git reset)

### Objetivos

- ✅ Crear nueva estructura de directorios
- ✅ Mover documentación a `/docs`
- ✅ Mover scripts a `/scripts`
- ✅ Consolidar tests en `/tests`
- ✅ Crear archivos de configuración base

### Tareas Detalladas

| # | Tarea | Tiempo | Dificultad |
|---|-------|--------|------------|
| 1.1 | Ejecutar `migrate_structure.py --dry-run` | 2 min | Trivial |
| 1.2 | Revisar output del dry-run | 5 min | Trivial |
| 1.3 | Ejecutar migración real | 1 min | Trivial |
| 1.4 | Verificar archivos movidos correctamente | 10 min | Fácil |
| 1.5 | Ejecutar `scripts/test_setup.py` | 2 min | Trivial |
| 1.6 | Actualizar enlaces en README.md | 15 min | Fácil |
| 1.7 | Commit y push | 5 min | Trivial |
| **Total** | | **~40 min** | |

### Checklist de Verificación

```bash
# ✅ Estructura creada
[ ] docs/user/ existe
[ ] docs/dev/ existe
[ ] docs/database/ existe
[ ] scripts/ existe
[ ] tests/unit/ existe
[ ] tests/integration/ existe
[ ] examples/basic/ existe
[ ] requirements/ existe

# ✅ Archivos movidos
[ ] INICIO_RAPIDO.md → docs/user/
[ ] MEJORAS*.md → docs/dev/
[ ] INIT_DATABASE.md → docs/database/
[ ] init_database.py → scripts/
[ ] ejemplo_uso_bd.py → scripts/
[ ] test_setup.py → scripts/

# ✅ Archivos creados
[ ] .env.example
[ ] pytest.ini
[ ] tests/conftest.py
[ ] requirements/base.txt
[ ] requirements/dev.txt

# ✅ Funcionamiento
[ ] python scripts/test_setup.py pasa
[ ] No hay archivos rotos
[ ] Git status está limpio
```

### Resultado Esperado

```
ANTES                          DESPUÉS
────────────────────────────────────────────────────
Raíz: 14+ archivos        →   Raíz: ~10 archivos organizados
Docs dispersos            →   docs/ con 3 subdirectorios
Tests en 2 lugares        →   tests/ unificado
Scripts sueltos           →   scripts/ organizado
Sin configuración pytest  →   pytest.ini + conftest.py
```

### Rollback Plan

```bash
# Si necesitas revertir
git reset --hard HEAD~1

# O restaurar desde backup
python migrate_structure.py --rollback
```

---

## Fase 2: Refactoring de Módulos 🟡

**Duración**: 1 semana
**Riesgo**: Bajo-Medio
**Reversible**: Sí (git branch)

### Objetivos

- ✅ Crear nueva estructura de módulos
- ✅ Migrar código a nuevas ubicaciones
- ✅ Mantener compatibilidad con wrappers
- ✅ Actualizar imports gradualmente

### Estructura de Trabajo

```
Día 1-2: Crear módulos nuevos
├── py_strava/api/
├── py_strava/database/
├── py_strava/core/
└── py_strava/utils/

Día 3-4: Migrar código
├── Copiar (no mover) archivos
├── Actualizar imports internos
└── Crear tests para nuevos módulos

Día 5: Crear wrappers legacy
└── Mantener compatibilidad

Día 6-7: Testing y validación
├── Ejecutar tests completos
├── Validar que todo funciona
└── Code review
```

### Migraciones Específicas

#### 2.1 Módulo `api/` (1 día)

**Archivos a migrar**:
```python
py_strava/strava/strava_token.py     → py_strava/api/auth.py
py_strava/strava/strava_activities.py → py_strava/api/activities.py
```

**Cambios en imports**:
```python
# Antes
from py_strava.strava import strava_token as stravaToken
from py_strava.strava import strava_activities as stravaActivities

# Después
from py_strava.api import auth
from py_strava.api import activities
```

**Wrapper legacy**:
```python
# py_strava/strava/strava_token.py (wrapper)
import warnings
from py_strava.api import auth

warnings.warn(
    "py_strava.strava.strava_token está deprecado. "
    "Usa py_strava.api.auth",
    DeprecationWarning
)

# Re-exportar todo
__all__ = dir(auth)
```

#### 2.2 Módulo `database/` (1 día)

**Archivos a migrar**:
```python
py_strava/strava/strava_db_sqlite.py   → py_strava/database/sqlite.py
py_strava/strava/strava_db_postgres.py → py_strava/database/postgres.py
py_strava/db_schema.py                 → py_strava/database/schema.py
```

#### 2.3 Módulo `utils/` (0.5 días)

**Archivos a migrar**:
```python
py_strava/strava/strava_fechas.py → py_strava/utils/dates.py
```

**Nuevo**: `py_strava/utils/logging.py` - Configuración centralizada de logging

#### 2.4 Módulo `core/` (1 día)

**Extraer lógica de**:
```python
py_strava/main.py           → py_strava/core/sync.py (lógica)
                              py_strava/legacy/main.py (wrapper)

py_strava/informe_strava.py → py_strava/core/reports.py (lógica)
                              py_strava/legacy/informe_strava.py (wrapper)
```

### Checklist Fase 2

```bash
# ✅ Módulos creados
[ ] py_strava/api/__init__.py
[ ] py_strava/api/auth.py
[ ] py_strava/api/activities.py
[ ] py_strava/database/__init__.py
[ ] py_strava/database/sqlite.py
[ ] py_strava/database/postgres.py
[ ] py_strava/database/schema.py
[ ] py_strava/utils/__init__.py
[ ] py_strava/utils/dates.py
[ ] py_strava/core/__init__.py
[ ] py_strava/core/sync.py
[ ] py_strava/core/reports.py

# ✅ Wrappers legacy
[ ] py_strava/legacy/main.py (con deprecation warning)
[ ] py_strava/legacy/informe_strava.py
[ ] py_strava/strava/strava_token.py (wrapper)
[ ] py_strava/strava/strava_activities.py (wrapper)

# ✅ Tests actualizados
[ ] Tests pasan con nuevos imports
[ ] Tests pasan con imports legacy
[ ] Cobertura >= 80%

# ✅ Funcionamiento
[ ] python -m py_strava.main sigue funcionando
[ ] python -m py_strava.informe_strava sigue funcionando
[ ] from py_strava.api import auth funciona
```

---

## Fase 3: CLI Profesional 🟡

**Duración**: 3-5 días
**Riesgo**: Bajo
**Reversible**: Sí (es código nuevo)

### Objetivos

- ✅ Implementar CLI con Click
- ✅ Crear comando instalable `strava`
- ✅ Mantener compatibilidad con scripts antiguos

### Día 1: Setup Click

**Instalar Click**:
```bash
# Añadir a requirements/base.txt
click>=8.1.0
```

**Crear estructura**:
```python
py_strava/cli/
├── __init__.py
├── main.py              # Entry point principal
└── commands/
    ├── __init__.py
    ├── sync.py          # Comando sync
    ├── report.py        # Comando report
    └── init_db.py       # Comando init-db
```

### Día 2-3: Implementar Comandos

**Estructura de comandos**:
```python
# py_strava/cli/main.py
import click
from py_strava.cli.commands import sync, report, init_db

@click.group()
@click.option('--log-level', default='INFO', help='Nivel de logging')
def cli(log_level):
    """Strava Sync - Sincroniza y analiza actividades de Strava"""
    import logging
    logging.basicConfig(level=getattr(logging, log_level))

cli.add_command(sync.sync)
cli.add_command(report.report)
cli.add_command(init_db.init_db)

if __name__ == '__main__':
    cli()
```

**Comando sync**:
```python
# py_strava/cli/commands/sync.py
import click
from py_strava.core.sync import run_sync

@click.command()
@click.option('--since', help='Fecha desde la cual sincronizar (YYYY-MM-DD)')
@click.option('--force', is_flag=True, help='Forzar sincronización completa')
def sync(since, force):
    """Sincronizar actividades de Strava con la base de datos"""
    click.echo("🔄 Sincronizando actividades...")

    try:
        result = run_sync(since=since, force=force)
        click.secho(f"✓ {result['activities']} actividades sincronizadas", fg='green')
        click.secho(f"✓ {result['kudos']} kudos procesados", fg='green')
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg='red', err=True)
        raise click.Abort()
```

### Día 4: Crear `setup.py` y `pyproject.toml`

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name='py-strava',
    version='2.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'requests>=2.31.0',
        'python-dateutil>=2.8.2',
        'click>=8.1.0',
    ],
    entry_points={
        'console_scripts': [
            'strava=py_strava.cli.main:cli',
        ],
    },
)
```

**pyproject.toml**:
```toml
[project]
name = "py-strava"
version = "2.1.0"
description = "Sincroniza y analiza actividades de Strava"

[project.scripts]
strava = "py_strava.cli.main:cli"
```

### Día 5: Testing e Integración

**Instalar en modo desarrollo**:
```bash
pip install -e .
```

**Probar comandos**:
```bash
strava --help
strava sync --help
strava sync
strava report --output test.csv
strava init-db --verify
```

### Checklist Fase 3

```bash
# ✅ CLI implementado
[ ] py_strava/cli/ estructura creada
[ ] Click instalado
[ ] setup.py creado
[ ] pyproject.toml creado

# ✅ Comandos funcionando
[ ] strava --help funciona
[ ] strava sync funciona
[ ] strava report funciona
[ ] strava init-db funciona

# ✅ Instalación
[ ] pip install -e . exitoso
[ ] Comando strava disponible en PATH

# ✅ Compatibilidad
[ ] python -m py_strava.main sigue funcionando
[ ] Scripts antiguos siguen funcionando
```

---

## Fase 4: Limpieza y Release 🔵

**Duración**: Variable (2-5 días)
**Riesgo**: Bajo
**Opcional**: Sí

### Objetivos

- ✅ Eliminar código duplicado
- ✅ Eliminar archivos innecesarios
- ✅ Consolidar documentación
- ✅ Preparar release v2.1.0

### Tareas

#### 4.1 Eliminar Código Legacy (1 día)

**Archivos a eliminar**:
```bash
# Archivos incorrectos
py_strava__init__.py
py_stravastrava__init__.py

# Archivos legacy (si ya nadie los usa)
py_strava/legacy/ (después de período de deprecación)
py_strava/strava/ (wrappers deprecados)
```

#### 4.2 Consolidar Documentación (1 día)

**Crear documento único**: `docs/dev/MEJORAS_COMPLETAS.md`

**Consolidar**:
- MEJORAS.md
- MEJORAS_MODULOS_DATABASE.md
- MEJORAS_STRAVA_DB_SQLITE.md
- MEJORAS_STRAVA_TOKEN_Y_MAIN.md
- ANALISIS_MEJORAS_POSTGRES.md
- RESUMEN_CAMBIOS.md

#### 4.3 Crear CHANGELOG.md (0.5 días)

```markdown
# Changelog

## [2.1.0] - 2025-12-15

### Added
- 🎉 CLI profesional con comando `strava`
- 📁 Estructura modular de proyecto
- 🧪 Suite de tests unificada con pytest
- 📚 Documentación reorganizada en /docs
- ⚙️ Configuración moderna con pyproject.toml

### Changed
- 🔧 Módulos reorganizados (api/, database/, core/, utils/)
- 📦 Sistema de instalación con pip

### Deprecated
- ⚠️ `python -m py_strava.main` (usar `strava sync`)
- ⚠️ Imports desde py_strava.strava.*

### Fixed
- 🐛 Archivos __init__.py incorrectos eliminados
```

#### 4.4 Preparar Release (1 día)

**Checklist de release**:
```bash
# ✅ Código
[ ] Todos los tests pasan
[ ] Linting pasa (black, flake8)
[ ] Type checking pasa (mypy)
[ ] No hay TODO/FIXME críticos

# ✅ Documentación
[ ] README.md actualizado
[ ] CHANGELOG.md completo
[ ] Docs en /docs actualizadas
[ ] Ejemplos funcionan

# ✅ Versionado
[ ] Version bump en pyproject.toml
[ ] Git tag v2.1.0
[ ] Release notes escritas

# ✅ Distribución (opcional)
[ ] Build funcionando
[ ] Puede instalarse desde PyPI
```

---

## Métricas de Progreso

### Dashboard de Progreso

```
Fase 1: Reorganización    [████████████████████] 100% ✓ Completada
Fase 2: Refactoring       [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ Pendiente
Fase 3: CLI               [░░░░░░░░░░░░░░░░░░░░]   0% ⏳ Pendiente
Fase 4: Limpieza          [░░░░░░░░░░░░░░░░░░░░]   0% 🔵 Opcional

Progreso Total: 25% (1 de 4 fases)
```

### KPIs por Fase

| Fase | KPI | Meta | Actual | Estado |
|------|-----|------|--------|--------|
| 1 | Archivos reorganizados | 15+ | 0 | ⏳ |
| 1 | Directorios creados | 10+ | 0 | ⏳ |
| 2 | Módulos migrados | 8 | 0 | ⏳ |
| 2 | Tests pasando | 100% | - | ⏳ |
| 3 | Comandos CLI | 4 | 0 | ⏳ |
| 3 | Instalación funcional | Sí | No | ⏳ |
| 4 | Archivos eliminados | 5+ | 0 | 🔵 |
| 4 | Release publicado | Sí | No | 🔵 |

---

## Hitos y Releases

```
v2.0.0 (actual)
   ↓
   ├─ Fase 1 completada
   ├─ v2.0.1 (bugfixes)
   ↓
v2.1.0-alpha (Fase 2)
   ↓
   ├─ Nuevos módulos
   ├─ Tests pasando
   ↓
v2.1.0-beta (Fase 3)
   ↓
   ├─ CLI funcional
   ├─ Instalable
   ↓
v2.1.0 (Release Final)
   ↓
   ├─ Código limpio
   ├─ Docs completas
   ├─ Producción ready
```

---

## Recursos Necesarios

### Humanos

| Rol | Dedicación | Responsabilidad |
|-----|------------|-----------------|
| **Desarrollador Lead** | 80% (2 semanas) | Refactoring, revisión |
| **Desarrollador Junior** | 40% (1 semana) | Tests, documentación |
| **Revisor** | 20% (distribuido) | Code review |

### Técnicos

- Git/GitLab para control de versiones
- Python 3.8+ con venv
- Herramientas: black, flake8, mypy, pytest

### Tiempo

- **Fase 1**: 1-2 horas (inmediato)
- **Fase 2**: 1 semana (próxima semana)
- **Fase 3**: 3-5 días (semana 2-3)
- **Fase 4**: 2-5 días (opcional, semana 4+)

**Total**: 2-3 semanas para fases principales

---

## Plan de Comunicación

### Semana 1 (Fase 1)
- ✉️ Email: "Reorganización de estructura iniciada"
- 📢 Standup: Demo de nueva estructura
- 📝 Wiki: Actualizar con nueva ubicación de docs

### Semana 2-3 (Fases 2-3)
- ✉️ Email: "Nuevos módulos y CLI disponibles"
- 📢 Demo: Mostrar nuevos comandos `strava`
- 📚 Tutorial: Cómo usar el nuevo CLI

### Semana 4+ (Fase 4)
- 🎉 Announce: Release v2.1.0
- 📖 Blog post: "py-strava v2.1: Más profesional, más fácil"
- 🚀 Migration guide: Para usuarios actuales

---

## Próxima Acción

### ¿Listo para empezar?

**Ejecuta Fase 1 AHORA** (15 minutos):

```bash
# 1. Backup (por seguridad)
git checkout -b feature/restructure-project
git add -A
git commit -m "checkpoint: antes de reestructuración"

# 2. Ver qué cambiaría
python migrate_structure.py --dry-run

# 3. Ejecutar migración
python migrate_structure.py

# 4. Verificar
python scripts/test_setup.py
ls -la docs/
ls -la scripts/
ls -la tests/

# 5. Commit
git add -A
git commit -m "refactor: reorganizar estructura del proyecto (Fase 1)"
git push -u origin feature/restructure-project

# 6. Crear PR
gh pr create --title "Reestructuración del proyecto (Fase 1)" \
             --body "Ver PROPUESTA_REESTRUCTURACION.md para detalles"
```

---

**Última actualización**: 3 de diciembre de 2025
**Versión roadmap**: 1.0
