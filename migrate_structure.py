#!/usr/bin/env python
"""
Script para migrar el proyecto a la nueva estructura propuesta.

Este script implementa la Fase 1 de la migración de forma segura:
- Crea nueva estructura de directorios
- Mueve documentación a /docs
- Mueve scripts a /scripts
- Reorganiza tests
- NO toca el código fuente (evita romper nada)

Uso:
    python migrate_structure.py --dry-run    # Ver qué se haría sin hacer cambios
    python migrate_structure.py              # Ejecutar migración
    python migrate_structure.py --rollback   # Revertir cambios
"""

import os
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class ProjectMigrator:
    """Gestiona la migración de estructura del proyecto."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.root = project_root
        self.dry_run = dry_run
        self.backup_file = self.root / f'.migration_backup_{datetime.now():%Y%m%d_%H%M%S}.json'
        self.operations: List[Dict] = []

    def log(self, message: str, level: str = "INFO"):
        """Log con prefijo según modo."""
        prefix = "[DRY-RUN]" if self.dry_run else "[MIGRATE]"
        print(f"{prefix} {level}: {message}")

    def create_directory(self, path: Path, description: str = ""):
        """Crea un directorio si no existe."""
        if path.exists():
            self.log(f"Directorio ya existe: {path}", "SKIP")
            return

        self.log(f"Crear directorio: {path} {description}")

        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
            # Crear .gitkeep si está vacío
            gitkeep = path / '.gitkeep'
            if not any(path.iterdir()):
                gitkeep.touch()

        self.operations.append({
            'action': 'create_dir',
            'path': str(path),
            'description': description
        })

    def move_file(self, src: Path, dst: Path, reason: str = ""):
        """Mueve un archivo de src a dst."""
        if not src.exists():
            self.log(f"Archivo no existe (skip): {src}", "SKIP")
            return

        if dst.exists():
            self.log(f"Destino ya existe (skip): {dst}", "SKIP")
            return

        self.log(f"Mover: {src} -> {dst} ({reason})")

        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

        self.operations.append({
            'action': 'move',
            'src': str(src),
            'dst': str(dst),
            'reason': reason
        })

    def copy_file(self, src: Path, dst: Path, reason: str = ""):
        """Copia un archivo (para templates)."""
        if not src.exists():
            self.log(f"Archivo no existe (skip): {src}", "SKIP")
            return

        self.log(f"Copiar: {src} -> {dst} ({reason})")

        if not self.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src), str(dst))

        self.operations.append({
            'action': 'copy',
            'src': str(src),
            'dst': str(dst),
            'reason': reason
        })

    def create_file(self, path: Path, content: str, description: str = ""):
        """Crea un archivo nuevo con contenido."""
        if path.exists():
            self.log(f"Archivo ya existe (skip): {path}", "SKIP")
            return

        self.log(f"Crear archivo: {path} ({description})")

        if not self.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')

        self.operations.append({
            'action': 'create',
            'path': str(path),
            'description': description
        })

    def save_backup(self):
        """Guarda registro de operaciones para rollback."""
        if self.dry_run:
            return

        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(self.operations, f, indent=2)

        self.log(f"Backup guardado: {self.backup_file}")

    def migrate_phase_1(self):
        """
        Fase 1: Reorganización sin tocar código fuente.

        - Crear estructura de directorios
        - Mover documentación
        - Mover scripts
        - Crear archivos de configuración
        """
        self.log("=" * 70)
        self.log("FASE 1: Reorganización de estructura (sin tocar código)")
        self.log("=" * 70)

        # 1. Crear estructura de directorios
        self.log("\n1. Creando estructura de directorios...\n")

        directories = [
            (self.root / 'docs', ''),
            (self.root / 'docs' / 'user', 'Documentación para usuarios'),
            (self.root / 'docs' / 'dev', 'Documentación para desarrolladores'),
            (self.root / 'docs' / 'database', 'Documentación de base de datos'),
            (self.root / 'scripts', 'Scripts de utilidad'),
            (self.root / 'tests', 'Tests unificados'),
            (self.root / 'tests' / 'unit', 'Tests unitarios'),
            (self.root / 'tests' / 'integration', 'Tests de integración'),
            (self.root / 'tests' / 'fixtures', 'Datos de prueba'),
            (self.root / 'examples', 'Ejemplos de uso'),
            (self.root / 'examples' / 'basic', 'Ejemplos básicos'),
            (self.root / 'examples' / 'advanced', 'Ejemplos avanzados'),
            (self.root / 'requirements', 'Dependencias por entorno'),
        ]

        for path, desc in directories:
            self.create_directory(path, desc)

        # 2. Mover documentación
        self.log("\n2. Reorganizando documentación...\n")

        doc_moves = [
            # Documentación de usuario
            ('INICIO_RAPIDO.md', 'docs/user/INICIO_RAPIDO.md', 'Doc de usuario'),
            ('SOLUCION_ERRORES.md', 'docs/user/SOLUCION_ERRORES.md', 'Doc de usuario'),

            # Documentación de desarrollador
            ('MEJORAS.md', 'docs/dev/MEJORAS_IMPLEMENTADAS.md', 'Doc de desarrollo'),
            ('MEJORAS_MODULOS_DATABASE.md', 'docs/dev/MEJORAS_MODULOS_DATABASE.md', 'Doc de desarrollo'),
            ('MEJORAS_STRAVA_DB_SQLITE.md', 'docs/dev/MEJORAS_STRAVA_DB_SQLITE.md', 'Doc de desarrollo'),
            ('MEJORAS_STRAVA_TOKEN_Y_MAIN.md', 'docs/dev/MEJORAS_STRAVA_TOKEN_Y_MAIN.md', 'Doc de desarrollo'),
            ('ANALISIS_MEJORAS_POSTGRES.md', 'docs/dev/ANALISIS_MEJORAS_POSTGRES.md', 'Doc de desarrollo'),
            ('RESUMEN_CAMBIOS.md', 'docs/dev/RESUMEN_CAMBIOS.md', 'Doc de desarrollo'),
            ('SSL_CERTIFICADOS.md', 'docs/dev/SSL_CERTIFICADOS.md', 'Doc de desarrollo'),

            # Documentación de base de datos
            ('INIT_DATABASE.md', 'docs/database/INIT_DATABASE.md', 'Doc de BD'),
        ]

        for src_name, dst_name, reason in doc_moves:
            src = self.root / src_name
            dst = self.root / dst_name
            self.move_file(src, dst, reason)

        # 3. Mover scripts
        self.log("\n3. Moviendo scripts a /scripts...\n")

        script_moves = [
            ('init_database.py', 'scripts/init_database.py', 'Script de utilidad'),
            ('ejemplo_uso_bd.py', 'scripts/ejemplo_uso_bd.py', 'Script de ejemplo'),
            ('test_setup.py', 'scripts/test_setup.py', 'Script de verificación'),
        ]

        for src_name, dst_name, reason in script_moves:
            src = self.root / src_name
            dst = self.root / dst_name
            self.move_file(src, dst, reason)

        # 4. Mover tests
        self.log("\n4. Reorganizando tests...\n")

        test_moves = [
            ('test/test_fechas.py', 'tests/unit/test_fechas.py', 'Test unitario'),
            ('test/test_strava_token.py', 'tests/unit/test_strava_token.py', 'Test unitario'),
        ]

        for src_name, dst_name, reason in test_moves:
            src = self.root / src_name
            dst = self.root / dst_name
            self.move_file(src, dst, reason)

        # 5. Mover ejemplos
        self.log("\n5. Reorganizando ejemplos...\n")

        # Crear README en examples
        examples_readme = """# Ejemplos de Uso

Este directorio contiene ejemplos de cómo usar py-strava.

## Estructura

- `basic/`: Ejemplos básicos para empezar
- `advanced/`: Ejemplos avanzados y casos de uso complejos

## Ejemplos Básicos

Recomendamos empezar por los ejemplos básicos en orden:

1. `01_get_token.py` - Obtener y refrescar tokens
2. `02_get_activities.py` - Obtener actividades
3. `03_query_database.py` - Consultar la base de datos

## Ejemplos Avanzados

Los ejemplos avanzados demuestran:
- Sincronización personalizada
- Operaciones batch
- Uso avanzado de la base de datos
"""
        self.create_file(
            self.root / 'examples' / 'README.md',
            examples_readme,
            'README de ejemplos'
        )

        # 6. Crear archivos de configuración
        self.log("\n6. Creando archivos de configuración...\n")

        # .env.example
        env_example = """# Configuración de Base de Datos
DB_TYPE=sqlite  # sqlite o postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=strava
DB_USER=postgres
DB_PASSWORD=

# Rutas de archivos SQLite
SQLITE_DB_PATH=./bd/strava.sqlite

# Configuración de Strava API
STRAVA_CLIENT_ID=
STRAVA_CLIENT_SECRET=
STRAVA_REFRESH_TOKEN=

# Configuración de Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./data/strava.log

# Configuración de Rate Limiting
RATE_LIMIT_CALLS=100
RATE_LIMIT_PERIOD=900
"""
        self.create_file(self.root / '.env.example', env_example, 'Template de configuración')

        # pytest.ini
        pytest_ini = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
"""
        self.create_file(self.root / 'pytest.ini', pytest_ini, 'Configuración de pytest')

        # tests/conftest.py
        conftest = """\"\"\"Configuración de pytest y fixtures compartidos.\"\"\"

import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    \"\"\"Retorna la raíz del proyecto.\"\"\"
    return Path(__file__).parent.parent

@pytest.fixture
def sample_db_path(tmp_path):
    \"\"\"Retorna path a BD temporal para tests.\"\"\"
    return tmp_path / 'test_strava.sqlite'
"""
        self.create_file(self.root / 'tests' / 'conftest.py', conftest, 'Configuración de pytest')

        # requirements/base.txt
        base_req = """# Core dependencies
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
python-dateutil>=2.8.2
"""
        self.create_file(
            self.root / 'requirements' / 'base.txt',
            base_req,
            'Dependencias base'
        )

        # requirements/dev.txt
        dev_req = """-r base.txt

# Development tools
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.7.0
black>=23.12.0
flake8>=6.1.0
isort>=5.12.0
"""
        self.create_file(
            self.root / 'requirements' / 'dev.txt',
            dev_req,
            'Dependencias desarrollo'
        )

        # 7. Crear README en directorios vacíos
        self.log("\n7. Creando README en directorios de datos...\n")

        data_readme = """# Directorio de Datos

Este directorio contiene:
- Archivos CSV exportados
- Logs de la aplicación
- Datos generados

**NOTA**: Los archivos en este directorio son generados automáticamente y no deben
incluirse en el control de versiones.
"""
        self.create_file(self.root / 'data' / 'README.md', data_readme, 'README de data')

        bd_readme = """# Directorio de Base de Datos

Este directorio contiene:
- `strava.sqlite` - Base de datos SQLite (si se usa SQLite)
- `postgres_credentials.json` - Credenciales de PostgreSQL (no en git)

## Configuración

Copia `postgres_credentials.json.example` a `postgres_credentials.json` y edita
con tus credenciales si usas PostgreSQL.
"""
        self.create_file(self.root / 'bd' / 'README.md', bd_readme, 'README de bd')

        json_readme = """# Directorio de Configuración JSON

Este directorio contiene:
- `strava_tokens.json` - Tokens de Strava (no en git)

## Configuración

Copia `strava_tokens.json.example` a `strava_tokens.json` y edita con tus tokens.
"""
        self.create_file(self.root / 'json' / 'README.md', json_readme, 'README de json')

        # 8. Guardar backup
        self.save_backup()

        # 9. Resumen
        self.log("\n" + "=" * 70)
        self.log(f"RESUMEN: {len(self.operations)} operaciones planificadas/ejecutadas")
        self.log("=" * 70)

        operations_by_type = {}
        for op in self.operations:
            op_type = op['action']
            operations_by_type[op_type] = operations_by_type.get(op_type, 0) + 1

        for op_type, count in operations_by_type.items():
            self.log(f"  {op_type}: {count}")

        if not self.dry_run:
            self.log(f"\n✓ Migración completada exitosamente")
            self.log(f"✓ Backup guardado en: {self.backup_file}")
            self.log(f"\nPróximos pasos:")
            self.log(f"  1. Revisar los cambios")
            self.log(f"  2. Ejecutar: python scripts/test_setup.py")
            self.log(f"  3. Si algo salió mal: python migrate_structure.py --rollback")
        else:
            self.log(f"\n✓ Dry-run completado")
            self.log(f"✓ Para ejecutar de verdad: python migrate_structure.py")


def main():
    parser = argparse.ArgumentParser(
        description='Migrar proyecto a nueva estructura',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mostrar qué se haría sin hacer cambios'
    )

    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Revertir la última migración'
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent

    if args.rollback:
        print("Rollback no implementado aún")
        print("Por favor, usa git para revertir cambios si es necesario")
        return 1

    migrator = ProjectMigrator(project_root, dry_run=args.dry_run)
    migrator.migrate_phase_1()

    return 0


if __name__ == '__main__':
    exit(main())
