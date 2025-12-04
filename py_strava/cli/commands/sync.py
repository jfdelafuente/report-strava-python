"""
Comando 'sync' - Sincronizar actividades de Strava.

Este comando sincroniza las actividades desde la API de Strava
hacia la base de datos local.
"""

import logging
from datetime import datetime

import click

from py_strava.core.sync import run_sync

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--since",
    type=str,
    help="Fecha desde la cual sincronizar (formato: YYYY-MM-DD o timestamp Unix)",
)
@click.option(
    "--token-file",
    type=click.Path(exists=True),
    default="./json/strava_tokens.json",
    help="Ruta al archivo de tokens de Strava",
)
@click.option(
    "--activities-log",
    type=click.Path(),
    default="./data/strava_activities.log",
    help="Ruta al archivo de log de actividades",
)
@click.option(
    "--db-path",
    type=click.Path(),
    default="./bd/strava.sqlite",
    help="Ruta a la base de datos SQLite",
)
@click.option("--force", is_flag=True, help="Forzar sincronización completa (ignorar última sync)")
def sync(since, token_file, activities_log, db_path, force):
    r"""
    Sincronizar actividades de Strava con la base de datos.

    \b
    Este comando:
    1. Obtiene un token de acceso válido (renovándolo si es necesario)
    2. Descarga actividades nuevas desde Strava API
    3. Almacena las actividades en la base de datos
    4. Descarga y almacena los kudos de cada actividad
    5. Registra la fecha de sincronización

    \b
    Ejemplos:
      strava sync                              # Sincronizar desde última vez
      strava sync --since 2024-01-01           # Desde fecha específica
      strava sync --since 1704067200           # Desde timestamp Unix
      strava sync --force                      # Sincronización completa
      strava sync --db-path ./custom.sqlite    # Usar BD custom
    """
    click.echo("[SYNC] Iniciando sincronización de actividades de Strava...")

    # Convertir 'since' a timestamp Unix si se proporcionó
    since_timestamp = None
    if since:
        try:
            # Intentar parsear como fecha YYYY-MM-DD
            if "-" in since:
                dt = datetime.strptime(since, "%Y-%m-%d")
                since_timestamp = int(dt.timestamp())
                click.echo(f"[INFO] Sincronizando desde: {since} (timestamp: {since_timestamp})")
            else:
                # Asumir que es un timestamp Unix
                since_timestamp = int(since)
                dt = datetime.fromtimestamp(since_timestamp)
                click.echo(
                    f'[INFO] Sincronizando desde timestamp: {since_timestamp} ({dt.strftime("%Y-%m-%d %H:%M:%S")})'
                )
        except ValueError:
            click.secho(f"[ERROR] Formato de fecha inválido: {since}", fg="red", err=True)
            click.echo("Usa formato YYYY-MM-DD o timestamp Unix", err=True)
            raise click.Abort()
    elif force:
        since_timestamp = 0
        click.echo("[INFO] Modo --force: Sincronizando todas las actividades")

    try:
        # Ejecutar sincronización
        result = run_sync(
            token_file=token_file,
            activities_log=activities_log,
            db_path=db_path,
            since=since_timestamp,
        )

        # Mostrar resultados
        click.echo("\n" + "=" * 60)
        click.secho("[SUCCESS] Sincronización completada", fg="green", bold=True)
        click.echo("=" * 60)
        click.echo(f'  Actividades sincronizadas: {result["activities"]}')
        click.echo(f'  Kudos procesados:          {result["kudos"]}')
        click.echo(f'  Base de datos:             {result["db_type"]}')
        click.echo("=" * 60)

        if result["activities"] == 0:
            click.secho("\n[INFO] No hay actividades nuevas para sincronizar", fg="yellow")
        else:
            click.secho(
                f'\n[OK] {result["activities"]} actividades añadidas a la base de datos', fg="green"
            )

    except FileNotFoundError as e:
        click.secho(f"\n[ERROR] Archivo no encontrado: {e}", fg="red", err=True)
        click.echo("\nVerifica que:", err=True)
        click.echo(f"  1. El archivo de tokens existe: {token_file}", err=True)
        click.echo("  2. Has configurado tus credenciales de Strava", err=True)
        raise click.Abort()

    except ValueError as e:
        click.secho(f"\n[ERROR] {e}", fg="red", err=True)
        raise click.Abort()

    except Exception as e:
        click.secho(f"\n[ERROR] Error durante la sincronización: {e}", fg="red", err=True)
        logger.exception("Error en sincronización")
        raise click.Abort()
