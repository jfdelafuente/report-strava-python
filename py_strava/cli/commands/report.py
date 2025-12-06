"""
Comando 'report' - Generar reportes de actividades y kudos.

Este comando extrae datos de la base de datos y genera reportes
en formato CSV u otros formatos.
"""

import logging
from pathlib import Path

import click

from py_strava.core.reports import run_report

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="./data/strava_data.csv",
    help="Ruta del archivo CSV de salida",
)
@click.option(
    "--db-path",
    type=click.Path(exists=True),
    default="./bd/strava.sqlite",
    help="Ruta a la base de datos SQLite",
)
@click.option(
    "--format",
    type=click.Choice(["csv"], case_sensitive=False),
    default="csv",
    help="Formato del reporte (por ahora solo CSV)",
)
def report(output, db_path, format):
    r"""
    Generar reporte de actividades y kudos desde la base de datos.

    \b
    Este comando:
    1. Se conecta a la base de datos
    2. Extrae información de actividades y kudos
    3. Genera un archivo CSV con los datos
    4. Muestra estadísticas del reporte

    \b
    El reporte incluye:
    - Nombre y apellido de quien dio el kudo
    - Tipo de actividad
    - ID de la actividad
    - Fecha de inicio de la actividad

    \b
    Ejemplos:
      strava report                           # Reporte por defecto
      strava report -o mi_reporte.csv         # Custom output
      strava report --db-path ./custom.sqlite # Usar BD custom
    """
    click.echo("[REPORT] Generando reporte de actividades y kudos...")
    click.echo(f"[INFO] Base de datos: {db_path}")
    click.echo(f"[INFO] Archivo de salida: {output}")

    # Verificar que la base de datos existe
    db_file = Path(db_path)
    if not db_file.exists():
        click.secho(f"\n[ERROR] Base de datos no encontrada: {db_path}", fg="red", err=True)
        click.echo("\nPara crear la base de datos, ejecuta:", err=True)
        click.echo("  strava init-db", err=True)
        raise click.Abort()

    try:
        # Generar reporte
        result = run_report(db_path=db_path, output_csv=output)

        if result["success"]:
            # Mostrar resultados
            click.echo("\n" + "=" * 60)
            click.secho("[SUCCESS] Reporte generado exitosamente", fg="green", bold=True)
            click.echo("=" * 60)
            click.echo(f'  Archivo generado:   {result["output_file"]}')
            click.echo(f'  Base de datos:      {result["db_path"]}')

            # Intentar contar registros en el archivo generado
            try:
                output_path = Path(result["output_file"])
                if output_path.exists():
                    with open(output_path, encoding="utf-8") as f:
                        # -1 para excluir el header
                        num_records = sum(1 for line in f) - 1
                    click.echo(f"  Registros exportados: {num_records}")
            except Exception:
                pass

            click.echo("=" * 60)
            click.secho(f'\n[OK] Reporte guardado en: {result["output_file"]}', fg="green")
        else:
            click.secho("\n[ERROR] No se pudo generar el reporte", fg="red", err=True)
            raise click.Abort()

    except FileNotFoundError as e:
        click.secho(f"\n[ERROR] Archivo no encontrado: {e}", fg="red", err=True)
        raise click.Abort()

    except Exception as e:
        click.secho(f"\n[ERROR] Error al generar el reporte: {e}", fg="red", err=True)
        logger.exception("Error en generación de reporte")
        raise click.Abort()
