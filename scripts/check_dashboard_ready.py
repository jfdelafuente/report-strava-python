#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar que el sistema está listo para el dashboard.
Verifica la existencia de la base de datos y datos necesarios.
"""

import sys
import io
from pathlib import Path
import sqlite3

# Fix encoding en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from py_strava import config


def check_database_exists():
    """Verifica si existe la base de datos."""
    db_path = config.SQLITE_DB_PATH
    return db_path.exists()


def check_activities_count():
    """Cuenta el número de actividades en la base de datos."""
    db_path = config.SQLITE_DB_PATH

    if not db_path.exists():
        return 0

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Activities")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def check_kudos_count():
    """Cuenta el número de kudos en la base de datos."""
    db_path = config.SQLITE_DB_PATH

    if not db_path.exists():
        return 0

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Kudos")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


def main():
    """Verifica el estado del sistema para el dashboard."""
    print("=" * 60)
    print("  Verificación del Dashboard de Strava")
    print("=" * 60)
    print()

    # Verificar base de datos
    db_exists = check_database_exists()

    if not db_exists:
        print("❌ Base de datos NO encontrada")
        print()
        print("Para usar el dashboard necesitas:")
        print("  1. Crear directorios: mkdir bd data json")
        print("  2. Inicializar BD: strava init-db")
        print("  3. Sincronizar: strava sync")
        print()
        return 1

    print(f"✅ Base de datos encontrada: {config.SQLITE_DB_PATH}")
    print()

    # Contar actividades
    activities_count = check_activities_count()
    kudos_count = check_kudos_count()

    print(f"📊 Actividades en la BD: {activities_count}")
    print(f"👍 Kudos en la BD: {kudos_count}")
    print()

    if activities_count == 0:
        print("⚠️  No hay actividades sincronizadas")
        print()
        print("Para sincronizar actividades:")
        print("  strava sync")
        print()
        return 1

    # Todo OK
    print("✅ El sistema está listo para el dashboard")
    print()
    print("Para iniciar el dashboard ejecuta:")
    print("  streamlit run dashboard_app.py")
    print()
    print("  O usa los scripts de inicio rápido:")
    print("    - Windows: run_dashboard.bat")
    print("    - Linux/Mac: ./run_dashboard.sh")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
