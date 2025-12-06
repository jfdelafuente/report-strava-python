#!/usr/bin/env python
"""
Script para inicializar la base de datos SQLite de Strava.

Este script crea las tablas necesarias para almacenar:
- Activities: Actividades deportivas de Strava
- Kudos: Kudos recibidos en cada actividad

Uso:
    python scripts/init_database.py              # Crear tablas si no existen
    python scripts/init_database.py --reset      # Eliminar y recrear todas las tablas (¡CUIDADO!)
    python scripts/init_database.py --verify     # Verificar que las tablas existen
"""

import argparse
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Añadir el directorio raíz del proyecto al path de Python
# Esto permite importar py_strava desde cualquier ubicación
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Usar nuevos imports reorganizados
from py_strava.database import schema as db_schema
from py_strava.database import sqlite as db


def get_db_path() -> Path:
    """
    Obtiene la ruta al archivo de base de datos SQLite.

    Returns:
        Path: Ruta al archivo strava.sqlite
    """
    # Usar la raíz del proyecto
    db_dir = project_root / "bd"

    # Crear directorio si no existe
    db_dir.mkdir(exist_ok=True)

    return db_dir / "strava.sqlite"


def verify_tables(conn) -> bool:
    """
    Verifica que las tablas necesarias existan en la base de datos.

    Args:
        conn: Conexión a la base de datos

    Returns:
        bool: True si todas las tablas existen, False en caso contrario
    """
    tables = ["Activities", "Kudos"]
    all_exist = True

    logger.info("Verificando tablas existentes...")

    for table in tables:
        result = db.fetch_one(
            conn, "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        )

        if result:
            logger.info(f"  ✓ Tabla '{table}' existe")

            # Obtener información de columnas
            columns = db.fetch(conn, f"PRAGMA table_info({table})")
            logger.info(f"    Columnas: {', '.join([col['name'] for col in columns])}")
        else:
            logger.warning(f"  ✗ Tabla '{table}' NO existe")
            all_exist = False

    return all_exist


def create_tables(conn) -> None:
    """
    Crea las tablas necesarias si no existen.

    Args:
        conn: Conexión a la base de datos
    """
    logger.info("Creando tablas...")

    # Crear tabla Activities
    logger.info("  Creando tabla 'Activities'...")
    db.execute(conn, db_schema.CREATE_TABLE_ACTIVITIES)
    logger.info("  ✓ Tabla 'Activities' creada")

    # Crear tabla Kudos
    logger.info("  Creando tabla 'Kudos'...")
    db.execute(conn, db_schema.CREATE_TABLE_KUDOS)
    logger.info("  ✓ Tabla 'Kudos' creada")


def reset_database(conn) -> None:
    """
    Elimina y recrea todas las tablas.

    ¡PRECAUCIÓN! Esta función elimina todos los datos existentes.

    Args:
        conn: Conexión a la base de datos
    """
    logger.warning("=" * 60)
    logger.warning("¡ATENCIÓN! Vas a eliminar TODOS los datos de la base de datos")
    logger.warning("=" * 60)

    response = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")

    if response != "SI":
        logger.info("Operación cancelada por el usuario")
        return

    logger.info("Eliminando tablas existentes...")

    # Eliminar tabla Kudos primero (tiene foreign key)
    logger.info("  Eliminando tabla 'Kudos'...")
    db.execute(conn, db_schema.DROP_TABLE_KUDOS)

    # Eliminar tabla Activities
    logger.info("  Eliminando tabla 'Activities'...")
    db.execute(conn, db_schema.DROP_TABLE_ACTIVITIES)

    logger.info("  ✓ Tablas eliminadas")

    # Recrear tablas
    create_tables(conn)


def show_database_stats(conn) -> None:
    """
    Muestra estadísticas de la base de datos.

    Args:
        conn: Conexión a la base de datos
    """
    logger.info("\nEstadísticas de la base de datos:")
    logger.info("=" * 60)

    # Contar actividades
    result = db.fetch_one(conn, "SELECT COUNT(*) as count FROM Activities")
    activities_count = result["count"] if result else 0
    logger.info(f"  Activities: {activities_count} registros")

    # Contar kudos
    result = db.fetch_one(conn, "SELECT COUNT(*) as count FROM Kudos")
    kudos_count = result["count"] if result else 0
    logger.info(f"  Kudos: {kudos_count} registros")

    logger.info("=" * 60)


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Inicializa la base de datos SQLite de Strava",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python init_database.py              # Crear tablas si no existen
  python init_database.py --reset      # Eliminar y recrear todas las tablas
  python init_database.py --verify     # Solo verificar tablas existentes
        """,
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Eliminar y recrear todas las tablas (¡elimina todos los datos!)",
    )

    parser.add_argument(
        "--verify", action="store_true", help="Solo verificar que las tablas existan"
    )

    args = parser.parse_args()

    # Obtener ruta a la base de datos
    db_path = get_db_path()
    logger.info(f"Ruta de base de datos: {db_path}")

    # Conectar a la base de datos
    try:
        with db.DatabaseConnection(str(db_path)) as conn:
            logger.info(f"Conectado a la base de datos: {db_path}")

            if args.reset:
                # Modo reset: eliminar y recrear tablas
                reset_database(conn)

            elif args.verify:
                # Modo verificación: solo verificar tablas
                if verify_tables(conn):
                    logger.info("\n✓ Todas las tablas están correctamente creadas")
                else:
                    logger.error("\n✗ Faltan algunas tablas")
                    logger.info("\nEjecuta el script sin argumentos para crear las tablas:")
                    logger.info("  python init_database.py")
                    return 1

            else:
                # Modo normal: crear tablas si no existen
                logger.info("Inicializando base de datos...")
                create_tables(conn)
                logger.info("\n✓ Base de datos inicializada correctamente")

                # Verificar que todo esté correcto
                verify_tables(conn)

            # Mostrar estadísticas
            show_database_stats(conn)

            logger.info("\n✓ Operación completada exitosamente")
            return 0

    except Exception as e:
        logger.error(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
