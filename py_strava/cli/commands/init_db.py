"""
Comando 'init-db' - Inicializar la base de datos.

Este comando crea las tablas necesarias en la base de datos SQLite.
"""

import logging
from pathlib import Path

import click

from py_strava.database import schema as db_schema
from py_strava.database import sqlite as db

logger = logging.getLogger(__name__)


@click.command("init-db")
@click.option(
    "--db-path",
    type=click.Path(),
    default="./bd/strava.sqlite",
    help="Ruta a la base de datos SQLite",
)
@click.option("--reset", is_flag=True, help="[PELIGRO] Eliminar y recrear todas las tablas")
@click.option("--verify", is_flag=True, help="Solo verificar que las tablas existen (no crear)")
def init_db(db_path, reset, verify):
    """
    Inicializar la base de datos SQLite.

    \b
    Este comando:
    1. Crea las tablas Activities y Kudos si no existen
    2. Verifica la estructura de las tablas
    3. Muestra estadísticas de la base de datos

    \b
    Tablas creadas:
    - Activities: Almacena las actividades deportivas
    - Kudos: Almacena los kudos recibidos en cada actividad

    \b
    Ejemplos:
      strava init-db                      # Crear tablas si no existen
      strava init-db --verify             # Solo verificar
      strava init-db --reset              # ¡CUIDADO! Eliminar todo y recrear
      strava init-db --db-path custom.db  # Usar ruta custom
    """
    db_file = Path(db_path)

    if verify:
        click.echo("[VERIFY] Verificando base de datos...")
    elif reset:
        click.secho("[WARNING] Modo RESET activado", fg="yellow", bold=True)
    else:
        click.echo("[INIT-DB] Inicializando base de datos...")

    click.echo(f"[INFO] Ruta de la base de datos: {db_path}")

    # Crear directorio si no existe
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Conectar a la base de datos
    try:
        conn = db.sql_connection(str(db_path))
    except Exception as e:
        click.secho(f"\n[ERROR] No se pudo conectar a la base de datos: {e}", fg="red", err=True)
        raise click.Abort()

    try:
        if reset:
            # Confirmar antes de eliminar
            if not click.confirm(
                "\n[PELIGRO] ¿Estás seguro de que quieres ELIMINAR todas las tablas y datos?",
                default=False,
            ):
                click.echo("[INFO] Operación cancelada")
                return

            click.echo("\n[INFO] Eliminando tablas existentes...")
            try:
                db.execute(conn, "DROP TABLE IF EXISTS Kudos")
                db.execute(conn, "DROP TABLE IF EXISTS Activities")
                conn.commit()
                click.secho("[OK] Tablas eliminadas", fg="yellow")
            except Exception as e:
                click.secho(f"[WARNING] Error al eliminar tablas: {e}", fg="yellow")

        if not verify:
            # Crear tablas
            click.echo("\n[INFO] Creando tablas...")

            # Tabla Activities
            try:
                db.create_table(conn, "Activities", db_schema.SQL_CREATE_ACTIVITIES)
                click.secho("[OK] Tabla Activities creada/verificada", fg="green")
            except Exception as e:
                click.secho(f"[WARNING] Tabla Activities: {e}", fg="yellow")

            # Tabla Kudos
            try:
                db.create_table(conn, "Kudos", db_schema.SQL_CREATE_KUDOS)
                click.secho("[OK] Tabla Kudos creada/verificada", fg="green")
            except Exception as e:
                click.secho(f"[WARNING] Tabla Kudos: {e}", fg="yellow")

            conn.commit()

        # Verificar tablas
        click.echo("\n[INFO] Verificando estructura...")

        # Verificar Activities
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Activities")
            num_activities = cursor.fetchone()[0]
            click.secho(f"[OK] Tabla Activities: {num_activities} actividades", fg="green")
        except Exception as e:
            click.secho(
                f"[FAIL] Tabla Activities no existe o tiene errores: {e}", fg="red", err=True
            )

        # Verificar Kudos
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Kudos")
            num_kudos = cursor.fetchone()[0]
            click.secho(f"[OK] Tabla Kudos: {num_kudos} kudos", fg="green")
        except Exception as e:
            click.secho(f"[FAIL] Tabla Kudos no existe o tiene errores: {e}", fg="red", err=True)

        # Resumen
        click.echo("\n" + "=" * 60)
        if verify:
            click.secho("[SUCCESS] Verificación completada", fg="green", bold=True)
        else:
            click.secho("[SUCCESS] Base de datos inicializada", fg="green", bold=True)
        click.echo("=" * 60)
        click.echo(f"  Base de datos: {db_path}")
        click.echo(
            f"  Tamaño:        {db_file.stat().st_size / 1024:.2f} KB"
            if db_file.exists()
            else "  Tamaño:        N/A"
        )
        click.echo("=" * 60)

        if not verify:
            click.secho("\n[OK] La base de datos está lista para usar", fg="green")
            click.echo("\nPróximos pasos:")
            click.echo("  1. Sincronizar actividades:")
            click.echo("     strava sync")
            click.echo("\n  2. Generar reporte:")
            click.echo("     strava report")

    except Exception as e:
        click.secho(f"\n[ERROR] Error durante la inicialización: {e}", fg="red", err=True)
        logger.exception("Error en init-db")
        raise click.Abort()

    finally:
        conn.close()
