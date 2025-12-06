"""
Módulo de sincronización de actividades de Strava.

Este módulo contiene la lógica de negocio para sincronizar actividades
desde la API de Strava hacia la base de datos.
"""

import csv
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd

from py_strava import config
from py_strava.api import activities as stravaActivities
from py_strava.api import auth as stravaAuth
from py_strava.utils import dates as stravaFechas

# Intentar importar PostgreSQL, si no está disponible usar SQLite
try:
    from py_strava.database import postgres as stravaBBDD

    DB_TYPE = "PostgreSQL"
    USE_POSTGRES = True
except ImportError:
    from py_strava.database import sqlite as stravaBBDD

    DB_TYPE = "SQLite"
    USE_POSTGRES = False

# Configuración de logging
logger = logging.getLogger(__name__)

# Constantes por defecto (usando config centralizado)
DEFAULT_ACTIVITIES_LOG = str(config.STRAVA_ACTIVITIES_LOG)
DEFAULT_TOKEN_JSON = str(config.STRAVA_TOKEN_JSON)
DEFAULT_SQLITE_DB_PATH = str(config.SQLITE_DB_PATH)

# Campos de actividades a extraer
ACTIVITY_FIELDS = [
    "id",
    "name",
    "start_date_local",
    "type",
    "distance",
    "moving_time",
    "elapsed_time",
    "total_elevation_gain",
    "end_latlng",
    "kudos_count",
    "external_id",
]

def get_access_token(token_file: str) -> Optional[str]:
    """
    Obtiene un token de acceso válido de Strava.

    Args:
        token_file: Ruta al archivo JSON con los tokens de Strava

    Returns:
        Token de acceso válido o None si falla
    """
    try:
        current_token = stravaAuth.getTokenFromFile(token_file)
        strava_tokens = stravaAuth.refreshToken(current_token, token_file)
        access_token = strava_tokens["access_token"]
        logger.info("Token de acceso obtenido correctamente")
        return access_token
    except Exception as ex:
        logger.error(f"Error al obtener el token de acceso: {ex}")
        return None


def get_last_sync_timestamp(log_file: str) -> int:
    """
    Obtiene el timestamp de la última sincronización.

    Args:
        log_file: Ruta al archivo de log de actividades

    Returns:
        Timestamp Unix de la última sincronización o 0 si no existe
    """
    try:
        last_time = stravaFechas.last_timestamp(log_file)
        seconds = stravaFechas.timestamp_to_unix(last_time)
        logger.info(f"Última sincronización: {last_time}")
        return seconds
    except Exception as ex:
        logger.warning(f"No se encontró registro de sincronización previa: {ex}")
        return 0


def load_activities_to_db(conn, activities: pd.DataFrame) -> int:
    """
    Carga las actividades en la base de datos usando batch insert para mejor rendimiento.

    Args:
        conn: Conexión a la base de datos
        activities: DataFrame con las actividades

    Returns:
        Número de actividades cargadas
    """
    if activities.empty:
        logger.info("No hay actividades nuevas para cargar")
        return 0

    try:
        # Preparar lista de registros para batch insert
        records = []
        for _, row in activities.iterrows():
            record = {
                "id_activity": row["id"],
                "name": row["name"],
                "start_date_local": row["start_date_local"],
                "type": row["type"],
                "distance": row["distance"],
                "moving_time": row["moving_time"],
                "elapsed_time": row["elapsed_time"],
                "total_elevation_gain": row["total_elevation_gain"],
                "end_latlng": str(row["end_latlng"]),
                "kudos_count": row["kudos_count"],
                "external_id": row["external_id"],
            }
            records.append(record)

        # Batch insert (20-40x más rápido que insertar una por una)
        count = stravaBBDD.insert_many(conn, "Activities", records)
        logger.info(f"{count} actividades cargadas en la base de datos (batch insert)")
        return count

    except Exception as ex:
        logger.error(f"Error al insertar actividades con batch insert: {ex}")
        logger.info("Intentando inserción individual como fallback...")

        # Fallback: insertar una por una si falla el batch
        count = 0
        for _, row in activities.iterrows():
            try:
                record = {
                    "id_activity": row["id"],
                    "name": row["name"],
                    "start_date_local": row["start_date_local"],
                    "type": row["type"],
                    "distance": row["distance"],
                    "moving_time": row["moving_time"],
                    "elapsed_time": row["elapsed_time"],
                    "total_elevation_gain": row["total_elevation_gain"],
                    "end_latlng": str(row["end_latlng"]),
                    "kudos_count": row["kudos_count"],
                    "external_id": row["external_id"],
                }
                stravaBBDD.insert(conn, "Activities", record)
                count += 1
            except Exception as ex:
                logger.error(f"Error al insertar actividad {row['id']}: {ex}")
                continue

        logger.info(f"{count} actividades cargadas (inserción individual)")
        return count


def update_sync_log(log_file: str, num_activities: int) -> None:
    """
    Actualiza el log de sincronización con la fecha actual.

    Args:
        log_file: Ruta al archivo de log
        num_activities: Número de actividades procesadas
    """
    try:
        date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(log_file, "a", newline="\n") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([date, num_activities])
        logger.info(f"Log actualizado: {date} - {num_activities} actividades")
    except Exception as ex:
        logger.error(f"Error al actualizar el log: {ex}")


def run_sync(
    token_file: str = DEFAULT_TOKEN_JSON,
    activities_log: str = DEFAULT_ACTIVITIES_LOG,
    db_path: str = DEFAULT_SQLITE_DB_PATH,
    since: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Ejecuta el proceso de sincronización completo de actividades.

    Args:
        token_file: Ruta al archivo JSON con los tokens de Strava
        activities_log: Ruta al archivo de log de actividades
        db_path: Ruta a la base de datos SQLite (solo para SQLite)
        since: Timestamp Unix opcional para sincronizar desde una fecha específica

    Returns:
        Dict con estadísticas de la sincronización:
            - activities: número de actividades sincronizadas
            - db_type: tipo de base de datos utilizada
    """
    logger.info("=== Inicio de sincronización de Strava ===")
    logger.info(f"Usando base de datos: {DB_TYPE}")

    # Obtener token de acceso
    access_token = get_access_token(token_file)
    if not access_token:
        logger.error("No se pudo obtener el token de acceso. Abortando.")
        raise ValueError("No se pudo obtener el token de acceso")

    # Obtener timestamp de última sincronización
    if since is None:
        last_sync = get_last_sync_timestamp(activities_log)
    else:
        last_sync = since
        logger.info(f"Sincronizando desde timestamp proporcionado: {since}")

    # Obtener actividades nuevas
    try:
        logger.info("Obteniendo actividades desde Strava...")
        activities = stravaActivities.request_activities(access_token, last_sync)
        logger.info(f"{len(activities)} actividades obtenidas")
    except Exception as ex:
        logger.error(f"Error al obtener actividades: {ex}")
        raise

    if activities.empty:
        logger.info("No hay actividades nuevas. Finalizando.")
        return {"activities": 0, "db_type": DB_TYPE}

    # Usar context manager para manejo automático de la conexión
    try:
        # Crear context manager según el tipo de base de datos
        if USE_POSTGRES:
            logger.info("Usando PostgreSQL")
            # type: ignore - DatabaseConnection de PostgreSQL no requiere parámetros
            with stravaBBDD.DatabaseConnection() as conn:  # type: ignore
                # Cargar actividades en la base de datos
                num_loaded = load_activities_to_db(conn, activities)

                if num_loaded == 0:
                    logger.info("No se pudieron cargar actividades. Finalizando.")
                    return {"activities": 0, "db_type": DB_TYPE}

                # La conexión se cierra y commitea automáticamente al salir del context manager
                logger.info("Datos guardados exitosamente")
        else:
            logger.info(f"Usando SQLite: {db_path}")
            # type: ignore - DatabaseConnection de SQLite requiere db_path
            with stravaBBDD.DatabaseConnection(db_path) as conn:  # type: ignore
                # Cargar actividades en la base de datos
                num_loaded = load_activities_to_db(conn, activities)

                if num_loaded == 0:
                    logger.info("No se pudieron cargar actividades. Finalizando.")
                    return {"activities": 0, "db_type": DB_TYPE}

                # La conexión se cierra y commitea automáticamente al salir del context manager
                logger.info("Datos guardados exitosamente")

    except Exception as ex:
        logger.error(f"Error durante la sincronización: {ex}")
        raise

    # Actualizar log de sincronización (fuera de la transacción DB)
    update_sync_log(activities_log, len(activities))

    logger.info("=== Sincronización completada exitosamente ===")

    return {"activities": num_loaded, "db_type": DB_TYPE}
