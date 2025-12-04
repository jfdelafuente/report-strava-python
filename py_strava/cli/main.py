"""
CLI Principal - Punto de entrada del comando 'strava'.

Este módulo implementa la interfaz de línea de comandos principal
usando Click, proporcionando comandos intuitivos para sincronizar
actividades, generar reportes e inicializar la base de datos.
"""

import logging
import sys
from pathlib import Path

import click

# Configuración de versión
__version__ = "2.2.0"


@click.group()
@click.version_option(version=__version__, prog_name="strava")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Nivel de logging",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Modo verbose (equivalente a --log-level DEBUG)"
)
@click.option(
    "--quiet", "-q", is_flag=True, help="Modo silencioso (equivalente a --log-level ERROR)"
)
def cli(log_level, verbose, quiet):
    """
    Strava CLI - Sincroniza y analiza actividades de Strava.

    \b
    Comandos disponibles:
      sync      Sincronizar actividades desde Strava API
      report    Generar reportes de actividades y kudos
      init-db   Inicializar la base de datos

    \b
    Ejemplos:
      strava sync                    # Sincronizar actividades
      strava sync --since 2024-01-01 # Sincronizar desde fecha específica
      strava report                  # Generar reporte
      strava init-db --verify        # Verificar base de datos

    Para más información sobre un comando específico:
      strava COMANDO --help
    """
    # Determinar nivel de logging
    if quiet:
        log_level = "ERROR"
    elif verbose:
        log_level = "DEBUG"

    # Configurar logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


# Importar y registrar comandos
from py_strava.cli.commands import init_db as init_db_cmd
from py_strava.cli.commands import report as report_cmd
from py_strava.cli.commands import sync as sync_cmd

cli.add_command(sync_cmd.sync)
cli.add_command(report_cmd.report)
cli.add_command(init_db_cmd.init_db)


def main():
    """Entry point para setup.py"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\n[!] Operación cancelada por el usuario", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n[ERROR] Error inesperado: {e}", err=True)
        logging.exception("Error inesperado")
        sys.exit(1)


if __name__ == "__main__":
    main()
