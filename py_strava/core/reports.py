"""
Módulo de generación de informes de actividades y kudos de Strava.

Este módulo contiene la lógica de negocio para generar informes
en diversos formatos (CSV, JSON, etc.) desde los datos almacenados
en la base de datos.
"""

import csv
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from py_strava.database import sqlite as stravaBBDD

# Configuración de logging
logger = logging.getLogger(__name__)

# Constantes por defecto
DEFAULT_DB_PATH = 'bd/strava.sqlite'
DEFAULT_OUTPUT_CSV = 'data/strava_data2.csv'

# Definición de consultas SQL
QUERY_KUDOS_ACTIVITIES = """
    SELECT
        firstname,
        lastname,
        type,
        kudos.id_activity,
        start_date_local
    FROM Kudos
    INNER JOIN Activities ON kudos.id_activity = Activities.id_activity
    ORDER BY start_date_local DESC, lastname, firstname
"""

# Campos del CSV de salida
CSV_FIELDNAMES = ['FIRST_NAME', 'LAST_NAME', 'TIPO', 'ACTIVIDAD', 'START_DATE']


def connect_to_database(db_path: str) -> Optional[object]:
    """
    Establece conexión con la base de datos SQLite.

    Args:
        db_path: Ruta al archivo de base de datos SQLite

    Returns:
        Conexión a la base de datos o None si falla
    """
    try:
        conn = stravaBBDD.sql_connection(db_path)
        logger.info(f"Conexión establecida con la base de datos: {db_path}")
        return conn
    except Exception as ex:
        logger.error(f"Error al conectar con la base de datos: {ex}")
        return None


def fetch_kudos_data(conn) -> List[Tuple]:
    """
    Obtiene los datos de kudos y actividades desde la base de datos.

    Args:
        conn: Conexión a la base de datos

    Returns:
        Lista de tuplas con los datos de kudos y actividades
    """
    try:
        records = stravaBBDD.fetch(conn, QUERY_KUDOS_ACTIVITIES)
        logger.info(f"{len(records)} registros obtenidos de la base de datos")
        return records
    except Exception as ex:
        logger.error(f"Error al obtener datos de la base de datos: {ex}")
        return []


def export_to_csv(data: List[Tuple], output_file: str, fieldnames: List[str]) -> bool:
    """
    Exporta los datos a un archivo CSV.

    Args:
        data: Lista de tuplas con los datos a exportar
        output_file: Ruta del archivo CSV de salida
        fieldnames: Nombres de las columnas del CSV

    Returns:
        True si la exportación fue exitosa, False en caso contrario
    """
    if not data:
        logger.warning("No hay datos para exportar")
        return False

    try:
        # Crear directorio si no existe
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(
                file,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            csv_writer.writerow(fieldnames)
            csv_writer.writerows(data)

        logger.info(f"Datos exportados correctamente a {output_file}")
        logger.info(f"Total de registros exportados: {len(data)}")
        return True

    except Exception as ex:
        logger.error(f"Error al exportar datos a CSV: {ex}")
        return False


def generate_kudos_report(db_path: str, output_csv: str) -> bool:
    """
    Genera un informe completo de kudos en formato CSV.

    Args:
        db_path: Ruta a la base de datos SQLite
        output_csv: Ruta del archivo CSV de salida

    Returns:
        True si el informe se generó correctamente, False en caso contrario
    """
    logger.info("=== Inicio de generación de informe de kudos ===")

    # Conectar a la base de datos
    conn = connect_to_database(db_path)
    if not conn:
        return False

    try:
        # Obtener datos
        data = fetch_kudos_data(conn)

        # Exportar a CSV
        success = export_to_csv(data, output_csv, CSV_FIELDNAMES)

        return success

    finally:
        # Cerrar conexión
        if conn:
            conn.close()
            logger.info("Conexión a la base de datos cerrada")
            logger.info("=== Generación de informe completada ===")


def run_report(
    db_path: str = DEFAULT_DB_PATH,
    output_csv: str = DEFAULT_OUTPUT_CSV
) -> Dict[str, Any]:
    """
    Ejecuta la generación de informe de kudos.

    Args:
        db_path: Ruta a la base de datos SQLite
        output_csv: Ruta del archivo CSV de salida

    Returns:
        Dict con estadísticas del informe generado:
            - success: booleano indicando si el informe se generó correctamente
            - output_file: ruta del archivo generado
            - records_count: número de registros exportados
    """
    success = generate_kudos_report(db_path, output_csv)

    return {
        'success': success,
        'output_file': output_csv if success else None,
        'db_path': db_path
    }
